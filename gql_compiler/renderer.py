import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type, Union
from xmlrpc.client import boolean

from graphql import (
    GraphQLEnumType,
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLSchema,
    ListTypeNode,
    NamedTypeNode,
    NonNullTypeNode,
    OperationType,
    TypeNode,
)
from marshmallow.fields import Field as MarshmallowField

from .parser import (
    GraphQLOutputType,
    ParsedField,
    ParsedQuery,
    ParsedQueryVariable,
)

DEFAULT_MAPPING = {
    "ID": "str",
    "String": "str",
    "Int": "int",
    "Float": "Number",
    "Boolean": "bool",
}


class CodeChunk:
    class Block:
        def __init__(self, codegen: "CodeChunk"):
            self.gen = codegen

        def __enter__(self):
            self.gen.indent()
            return self.gen

        def __exit__(self, *_, **__):  # type: ignore
            self.gen.unindent()

    def __init__(self):
        self.lines: List[str] = []
        self.level = 0

    def indent(self):
        self.level += 1

    def unindent(self):
        if self.level > 0:
            self.level -= 1

    @property
    def indent_string(self):
        return self.level * "    "

    def write(self, value: str):
        if value != "":
            value = self.indent_string + value
        self.lines.append(value)

    def write_lines(self, lines: List[str]):
        for line in lines:
            self.lines.append(self.indent_string + line)

    def block(self):
        return self.Block(self)

    def write_block(self, block_header: str):
        self.write(block_header)
        return self.block()

    def __str__(self):
        return os.linesep.join(self.lines)


@dataclass
class CustomScalar:
    name: str
    type: Type[Any]
    encoder: Optional[Callable[..., Any]] = None
    decoder: Optional[Callable[..., Any]] = None
    mm_field: Optional[MarshmallowField] = None


class Renderer:
    def __init__(
        self, schema: GraphQLSchema, custom_scalars: Dict[str, str] = {}, extra_import: str = ""
    ) -> None:
        self.schema = schema
        self.scalar_map = {
            "ID": "str",
            "Int": "int",
            "Float": "float",
            "Boolean": "bool",
            "String": "str",
        }
        self.scalar_map.update(custom_scalars)
        self.extra_import = extra_import

    def render(
        self,
        parsed_query_list: List[ParsedQuery],
    ) -> str:
        buffer = CodeChunk()
        self.__write_file_header(buffer)
        buffer.write("import typing")
        buffer.write("from gql import gql, Client")
        if self.extra_import:
            buffer.write(self.extra_import)

        for query in parsed_query_list:
            for enum_name, enum_type in query.used_enums.items():
                self.render_enum(buffer, enum_name, enum_type)

            for class_name, class_type in reversed(query.used_input_types.items()):
                self.render_input(buffer, class_name, class_type)

            for class_name, class_info in reversed(query.type_map.items()):
                self.render_model(buffer, class_name, class_info, query)

            self.render_model(buffer, f"{query.name}Response", query, query)

            self.render_input_type(buffer, f"{query.name}Input", query.variable_map)

            buffer.write("")
            buffer.write("")
            with buffer.write_block(f"class {query.name}:"):
                with buffer.write_block("_query = gql('''"):
                    buffer.write_lines(self.get_query_body(query).splitlines())
                buffer.write("''')")
                if query.query.operation in (OperationType.QUERY, OperationType.MUTATION):
                    self.write_execute_method(buffer, query, async_=False)
                    self.write_execute_method(buffer, query, async_=True)
                else:
                    self.write_subscribe_method(buffer, query, async_=True)
                    self.write_subscribe_method(buffer, query, async_=True)
        return str(buffer)

    def get_query_body(self, query: ParsedQuery) -> str:
        body = query.query.loc.source.body  # type: ignore
        return body[query.query.loc.start : query.query.loc.end]  # type: ignore

    def render_enum(self, buffer: CodeChunk, name: str, enum_type: GraphQLEnumType):
        enum_list = [f'"{x}"' for x in enum_type.values]
        buffer.write(f"{name} = typing.Literal[{', '.join(enum_list)}]")

    def render_input(self, buffer: CodeChunk, name: str, input_type: GraphQLInputObjectType):
        # TODO: コード共通か
        r: List[str] = []
        nr: List[str] = []
        for key, pqv in input_type.fields.items():  # type: ignore
            type_: GraphQLOutputType = pqv.type  # type: ignore
            s = f'"{key}": {self.type_to_string(type_)}'
            if bool(pqv.default_value) or (not isinstance(type_, GraphQLNonNull)):
                nr.append(s)
            else:
                r.append(s)

        buffer.write("")
        buffer.write("")
        buffer.write(f'{name}__required = typing.TypedDict("{name}__required", {"{"}{", ".join(r)}{"}"})')
        buffer.write(
            f'{name}__not_required = typing.TypedDict("{name}__not_required", {"{"}{", ".join(nr)}{"}"}, total=False)'
        )
        buffer.write("")
        buffer.write("")
        with buffer.write_block(f"class {name}({name}__required, {name}__not_required):"):
            buffer.write("pass")

    def get_field_type_mapping(
        self, parsed_field: Union[ParsedField, ParsedQuery], parsed_query: ParsedQuery
    ) -> Dict[str, str]:
        m = {}
        if isinstance(parsed_field, ParsedField):
            if parsed_field.interface:
                m = self.get_field_type_mapping(parsed_field.interface, parsed_query=parsed_query)
        m.update(
            {
                field_name: self.type_to_string(field_value.type)
                for field_name, field_value in parsed_field.fields.items()
            }
        )
        if isinstance(parsed_field, ParsedField) and "__typename" in m:
            name = parsed_field.type.name
            print(parsed_field, parsed_field.type.name)
            types = [f'"{x}"' for x in parsed_query.type_name_mapping[name]]
            m["__typename"] = f"typing.Literal[{', '.join(types)}]"
        return m

    def render_model(
        self,
        buffer: CodeChunk,
        name: str,
        parsed_field: Union[ParsedField, ParsedQuery],
        parsed_query: ParsedQuery,
    ):
        field_mapping = self.get_field_type_mapping(parsed_field, parsed_query)
        r = [f'"{key}": {value}' for key, value in field_mapping.items()]
        buffer.write("")
        buffer.write("")
        type_str = f'typing.TypedDict("{name}", {"{"}{", ".join(r)}{"}"})'
        if isinstance(parsed_field, ParsedField):
            if parsed_field.inline_fragments:
                type_str = f'typing.TypedDict("__{name}", {"{"}{", ".join(r)}{"}"})'
                buffer.write(f"__{name} = {type_str}")
                types = [f"{parsed_field.type.name}__{x}" for x in parsed_field.inline_fragments]
                type_str = f"typing.Union[__{name}, {', '.join(types)}]"
        buffer.write(f"{name} = {type_str}")

    def type_to_string(
        self,
        type_: GraphQLOutputType,
        isnull: boolean = True,
    ) -> str:
        if isinstance(type_, GraphQLNonNull):
            return self.type_to_string(type_.of_type, isnull=False)  # type: ignore
        elif isinstance(type_, GraphQLList):
            return f"typing.List[{self.type_to_string(type_.of_type)}]"  # type: ignore
        type_name = self.scalar_map.get(type_.name, type_.name)
        if isnull:
            return f"typing.Optional[{type_name}]"
        return type_name

    def node_type_to_string(self, node: TypeNode, isnull: boolean = True) -> str:
        if isinstance(node, ListTypeNode):
            return f"typing.List[{self.node_type_to_string(node.type)}]"
        elif isinstance(node, NonNullTypeNode):
            return self.node_type_to_string(node.type, isnull=False)
        elif isinstance(node, NamedTypeNode):
            type_name = self.scalar_map.get(node.name.value, node.name.value)
            if isnull:
                return f"typing.Optional[{type_name}]"
            return type_name
        raise Exception("Unknown type node")

    def render_input_type(self, buffer: CodeChunk, name: str, variable_map: Dict[str, ParsedQueryVariable]):
        r: List[str] = []
        nr: List[str] = []
        for key, pqv in variable_map.items():
            s = f'"{key}": {self.node_type_to_string(pqv.type_node)}'
            if pqv.is_undefinedable:
                nr.append(s)
            else:
                r.append(s)

        buffer.write("")
        buffer.write("")
        buffer.write(f'{name}__required = typing.TypedDict("{name}__required", {"{"}{", ".join(r)}{"}"})')
        buffer.write(
            f'{name}__not_required = typing.TypedDict("{name}__not_required", {"{"}{", ".join(nr)}{"}"}, total=False)'
        )
        buffer.write("")
        buffer.write("")
        with buffer.write_block(f"class {name}({name}__required, {name}__not_required):"):
            buffer.write("pass")

    def write_execute_method(
        self,
        buffer: CodeChunk,
        query: ParsedQuery,
        async_: bool,
    ) -> None:
        buffer.write("@classmethod")
        var_list: List[str] = []
        for variable in query.query.variable_definitions:
            var_type_str = self.node_type_to_string(variable.type)
            var_list.append(f"{variable.variable.name.value}: {var_type_str}")

        default_variable_values = ""
        if all(x.is_undefinedable for x in query.variable_map.values()):
            default_variable_values = " = {}"
        method_name = f"execute{'_async' if async_ else ''}"
        async_prefix = "async " if async_ else ""
        with buffer.write_block(
            f"{async_prefix}def {method_name}(cls, client: Client, "
            f"variable_values: {query.name}Input{default_variable_values})"
            f" -> {query.name}Response:"
        ):
            buffer.write(f"return client.{method_name}(  # type: ignore")
            buffer.write("    cls._query, variable_values=variable_values")
            buffer.write(")")

    def write_subscribe_method(self, buffer: CodeChunk, query: ParsedQuery, async_: bool) -> None:
        buffer.write("@classmethod")
        var_list: List[str] = []
        for variable in query.query.variable_definitions:
            var_type_str = self.node_type_to_string(variable.type)
            var_list.append(f"{variable.variable.name.value}: {var_type_str}")

        default_variable_values = ""
        if all(x.is_undefinedable for x in query.variable_map.values()):
            default_variable_values = " = {}"
        method_name = f"subscribe{'_async' if async_ else ''}"
        async_prefix = "async " if async_ else ""
        with buffer.write_block(
            f"def {method_name}(cls, client: Client, variable_values: {query.name}Input{default_variable_values})"
            f" -> {query.name}Response:"
        ):
            with buffer.write_block(
                f"{async_prefix}for r in client.{method_name}("
                "cls._query, variable_values=variable_values)  # type: ignore"
            ):
                buffer.write(f"{async_prefix}yield r")

    @staticmethod
    def __write_file_header(buffer: CodeChunk) -> None:
        buffer.write("# @" + "generated AUTOGENERATED file. Do not Change!")
        buffer.write("")
