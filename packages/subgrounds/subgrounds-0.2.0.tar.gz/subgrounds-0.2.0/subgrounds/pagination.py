""" Pagination module

This module implements functions and data structures used to perform automatic
pagination on user-specified Subgrounds GraphQL queries.

Pagination is done in two steps:
1. The input query is transformed such that every field selection in the query
which yields a list of entities has:

#. An ordering (i.e.: ``orderBy`` and ``orderDirection`` are specified)
#. A ``first`` argument set to the ``firstN`` variable
#. A ``skip`` argument set to the ``skipN`` variable
#. A ``where`` filter with the filter name derived from the ordering and the
   value being a variable named ``lastOrderingValueN``

In other words, the query will be transformed in a form which allows Subgrounds
to paginate automatically by simply setting the set of pagination variables
(i.e.: ``firstN``, ``skipN`` and ``lastOrderingValueN``) to different
values. Each field that requires pagination (i.e.: each field that yields a list)
will have its own set of variables, hence the ``N`` post-fix.

Example:
The initial query

.. code-block:: none

  query {
    items(
      orderBy: timestamp,
      orderDirection: desc,
      first: 10000
    ) {
      foo
    }
  }

will be transformed to

.. code-block:: none

  query($first0: Int, $skip0: Int, $lastOrderingValue0: BigInt) {
    items(
      orderBy: timestamp,
      orderDirection: desc,
      first: $first0,
      skip: $skip0,
      where: {
        timestamp_lt: $lastOrderingValue0
      }
    ) {
      foo
    }
  }

As part of this step, a tree of PaginationNode objects is also created, which
mirrors the selection tree of the initial query but only includes fields that
require pagination.

See :class:`PaginationNode`, :func:`preprocess_selection` and
:func:`preprocess_document`.

2. Using the PaginationNode tree, a "cursor" (ish) tree is initialized which
provides a cursor that is used to iterate through the set of pagination arguments
values (i.e.: ``firstN``, ``skipN``, ``lastOrderingValueN``). This
"cursor" maintains a pagination state for each of the pagination nodes in the
pagination node tree that keeps track (amongst other things) of the number of
entities queried for each list fields. The cursor is moved forward based on
the response from the query executed with the variable values of the cursor's
previous state.

By looping through the "cursor" states until enough entities are queried, we can
get a sequence of response data which, when merged, are equivalen to the initial
request.

See :class:`Cursor`, :func:`trim_document` and :func:`paginate`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import reduce
from itertools import count
from pipe import map, traverse, where
from typing import Any, Iterator, Optional, Tuple

from subgrounds.query import (
  Argument,
  Document,
  InputValue,
  Selection,
  Query,
  VariableDefinition
)
import subgrounds.client as client
from subgrounds.schema import SchemaMeta, TypeMeta, TypeRef
from subgrounds.utils import extract_data, union

DEFAULT_NUM_ENTITIES = 100
PAGE_SIZE = 900


class PaginationError(RuntimeError):
  def __init__(self, message: Any, cursor: Cursor):
    super().__init__(message)
    self.cursor = cursor


@dataclass(frozen=True)
class PaginationNode:
  """ Class representing the pagination config for a single GraphQL list field.

  Attributes:
    node_idx (int): Index of PaginationNode, used to label pagination arguments
      for this node.
    filter_field (str): Name of the node's filter field, e.g.: if
      ``filter_name`` is ``timestamp_gt``, then :attr:`filter_field`
      is ``timestamp``
    first_value (int): Initial value of the ``first`` argument
    skip_value (int): Initial value of the ``skip`` argument
    filter_value (Any): Initial value of the filter argument
      (i.e.: ``where: {filter: FILTER_VALUE}``)
    filter_value_type (TypeRef.T): Type of the filter value
    key_path (list[str]): Location in the list field to which this pagination
      node refers to in the initial query
    inner (list[PaginationNode]): Nested pagination nodes (if any).
  """
  node_idx: int
  filter_field: str

  first_value: int
  skip_value: int
  filter_value: Any
  filter_value_type: TypeRef.T

  key_path: list[str]
  inner: list[PaginationNode] = field(default_factory=list)

  def variable_definitions(self: PaginationNode) -> list[VariableDefinition]:
    """ Returns a list of variable definitions corresponding to this pagination
    node's pagination arguments as well as the variable definitions related
    to any nested pagination nodes.

    Args:
      self (PaginationNode): The current PaginationNode

    Returns:
      list[VariableDefinition]: _description_
    """
    vardefs = [
      VariableDefinition(f'first{self.node_idx}', TypeRef.Named('Int')),
      VariableDefinition(f'skip{self.node_idx}', TypeRef.Named('Int')),
      VariableDefinition(f'lastOrderingValue{self.node_idx}', self.filter_value_type),
    ]

    nested_vardefs = list(
      self.inner
      | map(PaginationNode.variable_definitions)
      | traverse
    )

    return nested_vardefs + vardefs


def preprocess_selection(
  schema: SchemaMeta,
  select: Selection,
  key_path: list[str],
  counter: count[int]
) -> Tuple[Selection, PaginationNode]:
  """ Returns a tuple ``(select_, node)`` where ``select_`` is the same
  selection tree as ``select`` except it has been normalized for pagination
  and ``node`` is a :class:`PaginationNode` tree containing all pagination
  metadata for each selection in ``select`` yielding a list of entities.

  Args:
    schema (SchemaMeta): _description_
    select (Selection): _description_
    key_path (list[str]): _description_
    counter (count[int]): _description_

  Returns:
    Tuple[Selection, PaginationNode]: _description_
  """

  # 'Folding' function to recursively apply `preprocess_selection` to
  # `select`'s inner selections
  def fold(
    acc: Tuple[list[Selection], list[PaginationNode]],
    select_: Selection
  ) -> Tuple[list[Selection], list[PaginationNode]]:
    new_select, pagination_node = preprocess_selection(
      schema,
      select_,
      [*key_path, select.key],
      counter
    )
    return ([*acc[0], new_select], [*acc[1], pagination_node])

  # Compute nested nromalized selections and pagination nodes
  acc0: Tuple[list[Selection], list[PaginationNode]] = ([], [])
  new_selections, pagination_nodes = reduce(fold, select.selection, acc0)

  if (
    select.fmeta.type_.is_list
    and (
      type(schema.type_of_typeref(select.fmeta.type_)) == TypeMeta.ObjectMeta
      or type(schema.type_of_typeref(select.fmeta.type_)) == TypeMeta.InterfaceMeta
    )
  ):
    # Add id to selection if not already present
    try:
      next(new_selections | where(lambda select: select.fmeta.name == 'id'))
    except StopIteration:
      new_selections.append(Selection(fmeta=TypeMeta.FieldMeta('id', '', [], TypeRef.Named('String'))))

    n = next(counter)

    # Starting point for new arguments: all arguments not important for pagination
    pagination_args = ['first', 'skip', 'where', 'orderBy', 'orderDirection']
    new_args = list(
      select.arguments
      | where(lambda arg: arg.name not in pagination_args)
    )

    # Set `first` argument
    try:
      first_arg = select.get_argument('first', recurse=False)
      first_arg_value = first_arg.value.value
    except KeyError:
      first_arg_value = DEFAULT_NUM_ENTITIES
    new_args.append(Argument(name='first', value=InputValue.Variable(f'first{n}')))

    # Set `skip` argument
    try:
      skip_arg = select.get_argument('skip', recurse=False)
      skip_arg_value = skip_arg.value.value
    except KeyError:
      skip_arg_value = 0
    new_args.append(Argument(name='skip', value=InputValue.Variable(f'skip{n}')))

    # Check if `orderBy` argument is provided. If not, set the `orderBy` argument to `id`
    try:
      order_by_arg = select.get_argument('orderBy', recurse=False)
      order_by_val = order_by_arg.value.value

      # Add `order_by_val` field to selection if not already present
      try:
        next(new_selections | where(lambda select: select.fmeta.name == order_by_val))
      except StopIteration:
        select_type: TypeMeta.ObjectMeta = schema.type_of_typeref(select.fmeta.type_)
        new_selections.append(Selection(fmeta=TypeMeta.FieldMeta(order_by_val, '', [], select_type.type_of_field(order_by_val))))

    except KeyError:
      order_by_arg = Argument(name='orderBy', value=InputValue.Enum('id'))
      order_by_val = 'id'
    new_args.append(order_by_arg)

    # Check if `orderDirection` argument is provided. If not, set it to `asc`.
    try:
      order_direction_arg = select.get_argument('orderDirection', recurse=False)
      order_direction_val = order_direction_arg.value.value
    except KeyError:
      order_direction_arg = Argument(name='orderDirection', value=InputValue.Enum('asc'))
      order_direction_val = 'asc'
    new_args.append(order_direction_arg)

    # Check if `where` argument is provided. If not, set it to `where: {filtering_arg: $lastOrderingValueN}`
    # where `filtering_arg` depends on the previous values of `orderBy` and `orderDirection`.
    # E.g.: if `orderBy` is `foo` and `orderDirection` is `asc`, then `filtering_arg` will be `foo_gt`
    filtering_arg = '{}_{}'.format(order_by_val, 'gt' if order_direction_val == 'asc' else 'lt')

    try:
      where_arg = select.get_argument('where', recurse=False)

      if filtering_arg in where_arg.value.value:
        filter_value = where_arg.value.value[filtering_arg].value
      else:
        filter_value = None

      where_arg = Argument(name='where', value=InputValue.Object(
        where_arg.value.value | {filtering_arg: InputValue.Variable(f'lastOrderingValue{n}')}
      ))
    except KeyError:
      where_arg = Argument(name='where', value=InputValue.Object({
        filtering_arg: InputValue.Variable(f'lastOrderingValue{n}')
      }))
      filter_value = None
    new_args.append(where_arg)

    # Find type of filter argument
    t: TypeRef.T = select.fmeta.type_of_arg('where')
    where_arg_type: TypeMeta.InputObjectMeta = schema.type_of_typeref(t)
    filtering_arg_type: TypeRef.T = where_arg_type.type_of_input_field(filtering_arg)

    return (
      Selection(
        fmeta=select.fmeta,
        alias=select.alias,
        arguments=new_args,
        selection=new_selections
      ),
      PaginationNode(
        node_idx=n,
        filter_field=order_by_val,

        first_value=first_arg_value,
        skip_value=skip_arg_value,
        filter_value=filter_value,
        filter_value_type=filtering_arg_type,

        key_path=[*key_path, select.alias if select.alias is not None else select.fmeta.name],
        inner=list(pagination_nodes | traverse)
      )
    )
  else:
    # If selection does not return a list of entities, leave it unchanged
    return (
      Selection(
        fmeta=select.fmeta,
        alias=select.alias,
        arguments=select.arguments,
        selection=new_selections
      ),
      list(pagination_nodes | traverse)
    )


def preprocess_document(
  schema: SchemaMeta,
  document: Document,
) -> Tuple[Document, list[PaginationNode]]:
  match document:
    case Document(url, None, fragments, variables) as doc:
      return (doc, [])

    case Document(url, query, fragments, variables) as doc:
      counter = count(0)

      def fold(
        acc: Tuple[list[Selection], list[PaginationNode]],
        select: Selection
      ) -> Tuple[list[Selection], list[PaginationNode]]:
        new_select, pagination_node = preprocess_selection(schema, select, [], counter)
        return ([*acc[0], new_select], [*acc[1], pagination_node])

      acc0: Tuple[list[Selection], list[PaginationNode]] = ([], [])
      new_selections, pagination_nodes = reduce(fold, query.selection, acc0)

      variable_defs = list(
        pagination_nodes
        | traverse
        | map(PaginationNode.variable_definitions)
        | traverse
      )

      return (
        Document(
          url=url,
          query=Query(
            name=query.name,
            selection=new_selections,
            variables=union(
              query.variables,
              variable_defs,
              key=lambda vardef: vardef.name,
              combine=lambda _, x: x
            )
          ),
          fragments=fragments,
          variables=variables
        ),
        list(pagination_nodes | traverse)
      )


@dataclass
class Cursor:
  """ Class used to generate the pagination variables for a given tree of
  ``PaginationNode`` objects.

  Attributes:
    page_node: The ``PaginationNode`` object which this cursor is iterating
      through.
    inner: The cursors for nested ``PaginationNodes``, if any.
    inner_idx: The index of the inner ``PaginationNode`` through which this cursor
      iterating.
    filter_value: The previous page's index value used to query the next data page.
      Depends on ``page_node.filter_field``, e.g.: if ``page_node.filter_field``
      is ``timestamp_gt``, then ``filter_value`` will be the highest timestamp
      the entities returned in the previous data page.
    queried_entities: Counter keeping track of the total number of queried entities.
    stop: Flag indicating whether or not to stop the cursor.
    page_count: Counter keeping track of the total number data pages queried.
    keys: Set keeping track of the keys of all queried entities to avoid duplicates.
  """
  page_node: PaginationNode

  inner: list[Cursor]
  inner_idx: int = 0

  filter_value: Any = None
  queried_entities: int = 0
  stop: bool = False
  page_count: int = 0
  keys: set[str] = field(default_factory=set)

  def __init__(self, page_node: PaginationNode) -> None:
    self.page_node = page_node
    self.inner = list(page_node.inner | map(Cursor))
    self.reset()

  @property
  def is_leaf(self):
    return len(self.inner) == 0

  def update(self, data: dict) -> None:
    """ Moves ``self`` cursor forward according to previous response data ``data``

    Args:
      data (dict): Previous response data

    Raises:
      StopIteration: _description_
    """
    # Current node step
    index_field_data = list(extract_data([*self.page_node.key_path, self.page_node.filter_field], data) | traverse)
    num_entities = len(index_field_data)
    filter_value = index_field_data[-1] if len(index_field_data) > 0 else None

    id_data = list(extract_data([*self.page_node.key_path, 'id'], data) | traverse)
    for key in id_data:
      if key not in self.keys:
        self.keys.add(key)

    self.page_count = self.page_count + 1
    self.queried_entities = len(self.keys)

    if filter_value:
      self.filter_value = filter_value

    if (
      (self.is_leaf and num_entities < PAGE_SIZE)
      or (not self.is_leaf and num_entities == 0)
      or (self.queried_entities == self.page_node.first_value)
    ):
      raise StopIteration(self)

  def step(self, data: dict) -> None:
    """ Updates either ``self`` cursor or inner state machine depending on
    whether the inner state machine has reached its limit

    Args:
      data (dict): _description_
    """
    if self.is_leaf:
      self.update(data)
    else:
      try:
        self.inner[self.inner_idx].step(data)
      except StopIteration:
        if self.inner_idx < len(self.inner) - 1:
          self.inner_idx = self.inner_idx + 1
        else:
          self.update(data)
          self.inner_idx = 0

        self.inner[self.inner_idx].reset()

  def args(self) -> dict:
    """ Returns the pagination arguments for the current state of the state machine

    Returns:
        dict: _description_
    """
    if self.is_leaf:
      if self.filter_value is None:
        return {
          # `first`
          f'first{self.page_node.node_idx}': self.page_node.first_value - self.queried_entities
          if self.page_node.first_value - self.queried_entities < PAGE_SIZE
          else PAGE_SIZE,

          # `skip`
          f'skip{self.page_node.node_idx}': self.page_node.skip_value if self.page_count == 0 else 0,
        }
      else:
        return {
          # `first`
          f'first{self.page_node.node_idx}': self.page_node.first_value - self.queried_entities
          if self.page_node.first_value - self.queried_entities < PAGE_SIZE
          else PAGE_SIZE,

          # `skip`
          f'skip{self.page_node.node_idx}': self.page_node.skip_value if self.page_count == 0 else 0,

          # `filter`
          f'lastOrderingValue{self.page_node.node_idx}': self.filter_value
        }
    else:
      if self.filter_value is None:
        args = {
          # `first`
          f'first{self.page_node.node_idx}': 1,

          # `skip`
          f'skip{self.page_node.node_idx}': self.page_node.skip_value if self.page_count == 0 else 0,
        }
      else:
        args = {
          # `first`
          f'first{self.page_node.node_idx}': 1,

          # `skip`
          f'skip{self.page_node.node_idx}': self.page_node.skip_value if self.page_count == 0 else 0,

          # `filter`
          f'lastOrderingValue{self.page_node.node_idx}': self.filter_value
        }

      inner_args = self.inner[self.inner_idx].args()
      return args | inner_args

  def reset(self):
    """ Reset state machine
    """
    self.inner_idx = 0
    self.filter_value = self.page_node.filter_value
    self.queried_entities = 0
    self.stop = False
    self.page_count = 0
    self.keys = set()


def trim_document(document: Document, pagination_args: dict[str, Any]) -> Document:
  """ Returns a new Document containing only the selection subtrees of
  ``document`` whose arguments are present in ``pagination_args``.

  Args:
    document (Document): The GraphQL document to be trimmed based on provided
      arguments.
    pagination_args (dict[str, Any]): The pagination arguments

  Returns:
    Document: A new document containing only the selection subtrees of
      ``document`` for which the pagination arguments are set in
      ``pagination_args``.
  """

  def trim_where_input_object(input_object: InputValue.Object) -> InputValue.Object:
    def f(keyval):
      (key, value) = keyval
      match value:
        case InputValue.Variable(name) if name in pagination_args and pagination_args[name] is None:
          return None
        case InputValue.Variable(name) if name not in pagination_args:
          return None
        case _:
          return (key, value)

    return InputValue.Object(dict(
      list(input_object.value.items())
      | map(f)
      | where(lambda keyval: keyval is not None)
    ))

  def trim_selection(selection: Selection) -> Optional[Selection]:
    try:
      # Check if pagination node by checking for `first` argument
      arg = next(selection.arguments | where(lambda arg: arg.name == 'first'))

      # Return selection if argument in current page variables
      if arg.value.name in pagination_args:
        return Selection(
          selection.fmeta,
          selection.alias,
          list(
            selection.arguments
            | map(lambda arg: Argument(name=arg.name, value=trim_where_input_object(arg.value)) if arg.name == 'where' else arg)
          ),
          list(
            selection.selection
            | map(trim_selection)
            | where(lambda val: val is not None)
          )
        )
      else:
        return None
    except StopIteration:
      # If does not contain `first` argument, then not a pagination node
      return Selection(
        selection.fmeta,
        selection.alias,
        selection.arguments,
        list(
          selection.selection
          | map(trim_selection)
          | where(lambda val: val is not None)
        )
      )

  return Document(
    url=document.url,
    query=Query(
      name=document.query.name,
      selection=list(
        document.query.selection
        | map(trim_selection)
        | where(lambda val: val is not None)
      ),
      variables=list(
        document.query.variables
        | where(lambda vardef: vardef.name in pagination_args)
      )
      # variables=[VariableDefinition(key, TypeRef.Named('Int')) for key in pagination_args] + document.query.variables
    ),
    fragments=document.fragments,
    variables=document.variables | pagination_args
  )


def merge(
  data1: list[Any] | dict[str, Any] | Any,
  data2: list[Any] | dict[str, Any] | Any
) -> list[Any] | dict[str, Any] | Any:
  """ Merges ``data1`` and ``data2`` and returns the combined result.

  ``data1`` and ``data2`` must be of the same type. Either both are
  ``dict``, ``list`` or anything else.

  Args:
    data1 (list[Any] | dict[str, Any] | Any): First data blob
    data2 (list[Any] | dict[str, Any] | Any): Second data blob

  Returns:
      list[Any] | dict[str, Any] | Any: Combined data blob
  """
  match (data1, data2):
    case (list() as l1, list() as l2):
      return union(
        l1,
        l2,
        lambda data: data['id'],
        combine=merge
      )
      # return data1 + data2

    case (dict() as d1, dict() as d2):
      data = {}
      for key in d1:
        if key in d2:
          data[key] = merge(d1[key], d2[key])
        else:
          data[key] = d1[key]

      for key in d2:
        if key not in data:
          data[key] = d2[key]

      return data

    case (dict(), _) | (_, dict()) | (list(), _) | (_, list()):
      raise TypeError(f'merge: incompatible data types! type(data1): {type(data1)} != type(data2): {type(data2)}')

    case (val1, _):
      return val1

  assert False  # Suppress mypy missing return statement warning


def paginate(schema: SchemaMeta, doc: Document) -> dict[str, Any]:
  """ Executes the request document `doc` based on the GraphQL schema `schema` and returns
  the response as a JSON dictionary.

  Args:
    schema (SchemaMeta): The GraphQL schema on which the request document is based
    doc (Document): The request document

  Returns:
    dict[str, Any]: The response data as a JSON dictionary
  """
  new_doc, pagination_nodes = preprocess_document(schema, doc)

  if pagination_nodes == []:
    return client.query(doc.url, doc.graphql, variables=doc.variables)
  else:
    data: dict[str, Any] = {}
    for page_node in pagination_nodes:
      arg_gen = Cursor(page_node)

      while True:
        try:
          args = arg_gen.args()
          trimmed_doc = trim_document(new_doc, args)
          page_data = client.query(trimmed_doc.url, trimmed_doc.graphql, variables=trimmed_doc.variables | args)
          data = merge(data, page_data)
          arg_gen.step(page_data)
        except StopIteration:
          break

    return data


def paginate_iter(schema: SchemaMeta, doc: Document) -> Iterator[dict[str, Any]]:
  """ Executes the request document `doc` based on the GraphQL schema `schema` and returns
  the response as a JSON dictionary.

  Args:
    schema (SchemaMeta): The GraphQL schema on which the request document is based
    doc (Document): The request document

  Returns:
    dict[str, Any]: The response data as a JSON dictionary
  """
  new_doc, pagination_nodes = preprocess_document(schema, doc)

  if pagination_nodes == []:
    yield client.query(doc.url, doc.graphql, variables=doc.variables)
  else:
    # data: dict[str, Any] = {}
    for page_node in pagination_nodes:
      cursor = Cursor(page_node)

      while True:
        try:
          args = cursor.args()
          trimmed_doc = trim_document(new_doc, args)
          page_data = client.query(trimmed_doc.url, trimmed_doc.graphql, variables=trimmed_doc.variables | args)
          yield page_data
          cursor.step(page_data)
        except StopIteration:
          break
        except Exception as exn:
          raise PaginationError(exn.args[0], cursor)
