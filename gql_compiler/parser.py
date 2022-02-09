from ast import type_ignore
from dataclasses import dataclass, field
import copy
from collections import OrderedDict
from re import M
from typing import Any, List, Mapping, Optional, Set, Union, cast, Dict, Tuple
from xmlrpc.client import boolean

from graphql import (
    GraphQLEnumType,
    GraphQLInputObjectType,
    GraphQLIsTypeOfFn,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLSchema,
    InlineFragmentNode,
    ListTypeNode,
    NamedTypeNode,
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
from graphql.type import GraphQLScalarType, GraphQLInterfaceType, GraphQLUnionType
from graphql.validation.rules.no_unused_fragments import NoUnusedFragmentsRule
from graphql.validation.specified_rules import specified_rules

GraphQLOutputType = Union[
    GraphQLScalarType,
    GraphQLObjectType,
    GraphQLInterfaceType,
    GraphQLUnionType,
    GraphQLEnumType,
    #    GraphQLWrappingType,
]


@dataclass
class ParsedField:
    name: str
    type: GraphQLOutputType
    # is_list: bool
    # nullable: bool
    # default_value: Any = None
    node: Union[FieldNode, InlineFragmentNode]
    fields: Dict[str, "ParsedField"] = field(default_factory=dict)
    inline_fragments: Dict[str, "ParsedField"] = field(default_factory=dict)
    interface: Optional["ParsedField"] = None


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


def strip_output_type_attribute(type_info: GraphQLOutputType) -> GraphQLOutputType:
    if isinstance(type_info, GraphQLNonNull):
        return strip_output_type_attribute(type_info.of_type)  # type: ignore
    if isinstance(type_info, GraphQLList):
        return strip_output_type_attribute(type_info.of_type)  # type: ignore
    return type_info


def strip_type_node_attribute(type_: TypeNode) -> NamedTypeNode:
    if isinstance(type_, ListTypeNode):
        return strip_type_node_attribute(type_.type)
    elif isinstance(type_, NonNullTypeNode):
        return strip_type_node_attribute(type_.type)
    elif isinstance(type_, NamedTypeNode):
        return type_
    raise Exception(f"Unknown type node {type_}")


@dataclass
class ParsedQueryVariable:
    is_undefinedable: boolean
    type_node: TypeNode


@dataclass
class ParsedQuery:
    query: OperationDefinitionNode

    name: str = field(default_factory=str)
    variable_definitions: Tuple[VariableDefinitionNode] = field(default_factory=tuple)
    fields: Dict[str, ParsedField] = field(default_factory=dict)
    type_map: Dict[str, ParsedField] = field(default_factory=OrderedDict)

    used_input_types: Dict[str, GraphQLInputObjectType] = field(default_factory=dict)
    used_enums: Dict[str, GraphQLEnumType] = field(default_factory=dict)
    variable_map: Dict[str, ParsedQueryVariable] = field(default_factory=OrderedDict)
    type_name_mapping: Dict[str, Set[str]] = field(default_factory=dict)


NodeT = Union[ParsedField, ParsedQuery]


class FieldToTypeMatcherVisitor(Visitor):
    def __init__(self, schema: GraphQLSchema, type_info: TypeInfo, query: OperationDefinitionNode):
        super().__init__()
        self.schema = schema
        self.type_info = type_info
        self.query = query
        self.parsed = ParsedQuery(query=self.query)
        self.dfs_path: List[NodeT] = []

    def push(self, obj: NodeT):
        self.dfs_path.append(obj)

    def pop(self) -> NodeT:
        return self.dfs_path.pop()

    @property
    def current(self) -> NodeT:
        return self.dfs_path[-1]

    def register_input_type_recursive(self, name: str):
        scalar_type = self.schema.type_map[name]
        if isinstance(scalar_type, GraphQLInputObjectType):
            self.parsed.used_input_types[name] = scalar_type
            for field_type in scalar_type.fields.values():  # type: ignore
                field_type = strip_output_type_attribute(field_type.type)
                self.register_input_type_recursive(field_type.name)
        elif isinstance(scalar_type, GraphQLEnumType):
            self.parsed.used_enums[scalar_type.name] = scalar_type

    # Document
    def enter_operation_definition(self, node: OperationDefinitionNode, *_):
        self.parsed.variable_definitions = node.variable_definitions
        for variable in node.variable_definitions:
            key = variable.variable.name.value
            is_undefinedable = bool(variable.default_value) or (
                not isinstance(variable.type, NonNullTypeNode)
            )
            stripped_type = strip_type_node_attribute(variable.type)
            self.register_input_type_recursive(stripped_type.name.value)
            # scalar_type = self.schema.type_map[stripped_type.name.value]
            # if isinstance(scalar_type, GraphQLInputObjectType):
            #     self.parsed.used_input_types[stripped_type.name.value] = scalar_type

            # print(key, is_undefinedable)
            self.parsed.variable_map[key] = ParsedQueryVariable(
                is_undefinedable=is_undefinedable, type_node=variable.type
            )

        self.parsed.name = node.name.value if node.name else ""
        self.push(self.parsed)
        return node

    # def enter_selection_set(self, node: SelectionSetNode, *_):
    #     print("selection_set", node)

    #     return node

    # def leave_selection_set(self, node: SelectionSetNode, *_):
    #     # self.pop()
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

    def get_available_typename(self, type_: Union[GraphQLObjectType, GraphQLInterfaceType]) -> Set[str]:
        if isinstance(type_, GraphQLObjectType):
            return set([type_.name])
        elif isinstance(type_, GraphQLInterfaceType):
            names = [type_.name]
            for key, value in self.schema.type_map.items():
                if not hasattr(value, "interfaces"):
                    continue
                if type_.name in [x.name for x in value.interfaces]:  # type: ignore
                    names.append(key)
            return set(names)
        raise Exception(f"Unexpected type {type_}")

    def enter_inline_fragment(self, node: InlineFragmentNode, *_):
        print("enter_inline_fragment")
        name = node.type_condition.name.value
        type_info: GraphQLOutputType = copy.deepcopy(self.type_info.get_type())  # type: ignore
        current = self.current
        if not isinstance(current, ParsedField):
            raise Exception("Unexpected")
        field = ParsedField(node=node, name=name, type=type_info, interface=current)
        stripped_type_info = strip_output_type_attribute(type_info)

        if isinstance(stripped_type_info, (GraphQLObjectType, GraphQLInterfaceType)):
            type_name = "__".join([x.name for x in self.dfs_path] + [name])
            self.parsed.type_name_mapping[type_name] = self.get_available_typename(stripped_type_info)
            stripped_type_info.name = type_name
            self.parsed.type_map[type_name] = field

        current.inline_fragments[name] = field
        self.push(field)

        return node

    def leave_inline_fragment(self, node: InlineFragmentNode, *_):
        child = self.current
        self.pop()
        parent = self.current
        if isinstance(child, ParsedField) and isinstance(parent, ParsedField):
            child_type_name = strip_output_type_attribute(child.type).name
            parent_type_name = strip_output_type_attribute(parent.type).name
            m = self.parsed.type_name_mapping
            m[parent_type_name] = m[parent_type_name] - m[child_type_name]
        return node

    # Field

    def enter_field(self, node: FieldNode, *_):
        name = node.alias.value if node.alias else node.name.value
        type_info: GraphQLOutputType = copy.deepcopy(self.type_info.get_type())  # type: ignore
        assert type_info
        # print("enter_field", name, node, node.name.value, type_info)
        # print(node.alias, node.name.value, type_info, type(type_info))
        stripped_type_info = strip_output_type_attribute(type_info)

        # self.register_new_type(name, type_info, node)
        field = ParsedField(node=node, name=name, type=type_info)

        if isinstance(stripped_type_info, (GraphQLObjectType, GraphQLInterfaceType)):
            type_name = "__".join([x.name for x in self.dfs_path] + [name])
            self.parsed.type_name_mapping[type_name] = self.get_available_typename(stripped_type_info)
            stripped_type_info.name = type_name
            self.parsed.type_map[type_name] = field
        elif isinstance(stripped_type_info, GraphQLEnumType):
            self.parsed.used_enums[stripped_type_info.name] = stripped_type_info

        self.current.fields[name] = field
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
        # print("leave field", node, node.name.value)
        self.pop()
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


class Parser:
    def __init__(self, schema: GraphQLSchema):
        self.schema = schema

    def parse(
        self, query: OperationDefinitionNode, full_fragments: str = "", should_validate: bool = True
    ) -> ParsedQuery:
        # query_document_ast = parse("".join([full_fragments, query]))
        # document_ast = parse(query)

        # if should_validate:
        #     errors = validate(
        #         self.schema,
        #         query,
        #         [rule for rule in specified_rules if rule is not NoUnusedFragmentsRule],
        #     )
        #     if errors:
        #         raise InvalidQueryError(errors)

        type_info = TypeInfo(self.schema)
        visitor = FieldToTypeMatcherVisitor(self.schema, type_info, query)
        visit(query, TypeInfoVisitor(type_info, visitor))
        result = visitor.parsed
        return result
