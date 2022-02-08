from dataclasses import dataclass, field
from typing import Any, List, Mapping, Union, cast, Dict, Tuple

from graphql import (
    GraphQLEnumType,
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLSchema,
    ListTypeNode,
    NonNullTypeNode,
    OperationDefinitionNode,
    TypeInfo,
    TypeInfoVisitor,
    TypeNode,
    Visitor,
    is_enum_type,
    is_scalar_type,
    parse,
    validate,
    visit,
)
from graphql.language import ExecutableDefinitionNode, VariableDefinitionNode, SelectionSetNode, FieldNode
from graphql.validation.rules.no_unused_fragments import NoUnusedFragmentsRule
from graphql.validation.specified_rules import specified_rules


@dataclass
class ParsedField:
    name: str
    # type: str
    # is_list: bool
    # nullable: bool
    # default_value: Any = None
    node: FieldNode
    fields: Dict[str, "ParsedField"] = field(default_factory=dict)


# @dataclass
# class ParsedEnum:
#     name: str
#     values: Mapping[str, Any]


# @dataclass
# class ParsedObject:
#     name: str
#     fields: List[ParsedField] = field(default_factory=list)
#     parents: List[str] = field(default_factory=list)
#     children: Dict[str, "ParsedObject"] = field(default_factory=dict)
#     inputs: Dict[str, "ParsedObject"] = field(default_factory=dict)
#     input_enums: List[ParsedEnum] = field(default_factory=list)


@dataclass
class ParsedQuery:
    query: ExecutableDefinitionNode

    name: str = field(default_factory=str)
    variable_definitions: Tuple[VariableDefinitionNode] = field(default_factory=tuple)
    fields: Dict[str, ParsedField] = field(default_factory=dict)


NodeT = Union[ParsedField, ParsedQuery]


class FieldToTypeMatcherVisitor(Visitor):
    def __init__(self, schema: GraphQLSchema, type_info: TypeInfo, query: ExecutableDefinitionNode):
        super().__init__()
        self.schema = schema
        self.type_info = type_info
        self.query = query
        self.parsed = ParsedQuery(query=self.query)
        self.dfs_path: List[NodeT] = []

    def push(self, obj: NodeT):
        self.dfs_path.append(obj)

    def pull(self) -> NodeT:
        return self.dfs_path.pop()

    @property
    def current(self) -> NodeT:
        return self.dfs_path[-1]

    # Document
    def enter_operation_definition(self, node: OperationDefinitionNode, *_):
        self.parsed.variable_definitions = node.variable_definitions
        self.push(self.parsed)
        return node

    # def enter_selection_set(self, node: SelectionSetNode, *_):
    #     print("selection_set", node)

    #     return node

    # def leave_selection_set(self, node: SelectionSetNode, *_):
    #     # self.pull()
    #     return node

    # Fragments
    # def enter_fragment_definition(self, node, *_):
    #     print("fragment_definition", node)
    #     # Same as operation definition
    #     obj = ParsedObject(name=node.name.value)
    #     self.parsed.fragment_objects.append(obj)  # pylint:disable=no-member
    #     self.push(obj)
    #     return node

    # def enter_fragment_spread(self, node, *_):
    #     self.current.parents.append(node.name.value)
    #     self.parsed.used_fragments.append(node.name.value)
    #     return node

    # def enter_inline_fragment(self, node, *_):
    #     return node
    #
    # def leave_inline_fragment(self, node, *_):
    #     return node

    # Field

    def enter_field(self, node: FieldNode, *_):
        print("enter_field", node, node.name.value)
        field = ParsedField(node=node, name=node.name.value)
        self.current.fields[node.name.value] = field
        self.push(field)
        # import code
        # code.interact(local=locals())
        # name = node.alias.value if node.alias else node.name.value
        # graphql_type = self.type_info.get_type()

        # field, obj_type, parsed_enum = self.__parse_field(name, graphql_type)
        # if parsed_enum is not None:
        #     self.parsed.enums.append(parsed_enum)  # pylint:disable=no-member

        # self.current.fields.append(field)

        # if obj_type is not None:
        #     obj = ParsedObject(name=str(obj_type))
        #     self.current.children[name] = obj
        #     self.push(obj)

        return node

    def leave_field(self, node: FieldNode, *_):
        print("leave field", node, node.name.value)
        self.pull()
        return node

    # def __parse_field(self, name, graphql_type):
    #     (
    #         type_name,
    #         is_list,
    #         nullable,
    #         underlying_graphql_type,
    #     ) = self.__scalar_type_to_python(graphql_type)

    #     parsed_field = ParsedField(name=name, type=type_name, is_list=is_list, nullable=nullable)
    #     parsed_enum = None

    #     if not is_scalar_type(underlying_graphql_type):
    #         if is_enum_type(underlying_graphql_type):
    #             enum_type = cast(GraphQLEnumType, self.schema.type_map[underlying_graphql_type.name])
    #             parsed_enum = ParsedEnum(
    #                 name=enum_type.name,
    #                 values={name: value.value or name for name, value in enum_type.values.items()},
    #             )
    #         else:
    #             return parsed_field, underlying_graphql_type, parsed_enum

    #     return parsed_field, None, parsed_enum

    # @staticmethod
    # def __scalar_type_to_python(scalar):
    #     nullable = True
    #     is_list = False
    #     if isinstance(scalar, GraphQLNonNull):
    #         nullable = False
    #         scalar = scalar.of_type

    #     if isinstance(scalar, GraphQLList):
    #         scalar = scalar.of_type
    #         if isinstance(scalar, GraphQLNonNull):
    #             scalar = scalar.of_type
    #             nullable = False
    #         is_list = True

    #     return scalar.name, is_list, nullable, scalar

    # @staticmethod
    # def __variable_type_to_python(var_type: TypeNode):
    #     nullable = True
    #     is_list = False
    #     if isinstance(var_type, NonNullTypeNode):
    #         nullable = False
    #         var_type = var_type.type
    #     if isinstance(var_type, ListTypeNode):
    #         is_list = True
    #         var_type = var_type.type
    #         if isinstance(var_type, NonNullTypeNode):
    #             nullable = False
    #             var_type = var_type.type
    #     print(var_type)
    #     print(dir(var_type))
    #     name: str = var_type.name.value  # type: ignore
    #     return name, nullable, is_list, var_type


class InvalidQueryError(Exception):
    def __init__(self, errors):
        self.errors = errors
        message = "\n".join(str(err) for err in errors)
        super().__init__(message)


class QueryParser:
    def __init__(self, schema: GraphQLSchema):
        self.schema = schema

    def parse(
        self, query: ExecutableDefinitionNode, full_fragments: str = "", should_validate: bool = True
    ) -> ParsedQuery:
        # query_document_ast = parse("".join([full_fragments, query]))
        # document_ast = parse(query)

        # if should_validate:
        #     errors = validate(
        #         self.schema,
        #         query_document_ast,
        #         [rule for rule in specified_rules if rule is not NoUnusedFragmentsRule],
        #     )
        #     if errors:
        #         raise InvalidQueryError(errors)

        type_info = TypeInfo(self.schema)
        visitor = FieldToTypeMatcherVisitor(self.schema, type_info, query)
        visit(query, TypeInfoVisitor(type_info, visitor))
        result = visitor.parsed
        return result
