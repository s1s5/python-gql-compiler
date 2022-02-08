import os
from typing import List, Union
import importlib.util
from dataclasses import dataclass
from importlib.abc import Loader
from typing import Any, Callable, Dict, List, Optional, Type
from xmlrpc.client import boolean

from graphql import (
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
from .utils import camel_case_to_lower_case

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
    def __init__(self, schema: GraphQLSchema) -> None:
        self.schema = schema
        self.scalar_map = {
            'ID': 'str',
            'Int': 'int',
            'Float': 'float',
            'Boolean': 'bool',
        }
        # self.config_path = config_path
        self.custom_scalars = {}
        # if config_path is not None:
        #     spec = importlib.util.spec_from_file_location("config", config_path)
        #     config = importlib.util.module_from_spec(spec)
        #     assert isinstance(spec.loader, Loader)
        #     spec.loader.exec_module(config)
        #     assert hasattr(config, "custom_scalars"), "Custom scalars is not in config"
        #     self.custom_scalars = getattr(config, "custom_scalars")

    def render(
        self,
        parsed_query_list: List[ParsedQuery],
        # fragment_name_to_importpath: Dict[str, str],
        # enum_name_to_importpath: Dict[str, str],
        # input_name_to_importpath: Dict[str, str],
        # config_importpath: Optional[str],
    ) -> str:
        buffer = CodeChunk()
        self.__write_file_header(buffer)
        # buffer.write("from dataclasses import dataclass, field as _field")
        # self.__render_customer_scalars_imports(buffer, config_importpath)
        # buffer.write("from gql.compiler.runtime.variables import encode_variables")
        buffer.write("import typing")
        buffer.write("from gql import gql, Client")
        # buffer.write("from gql.transport.exceptions import TransportQueryError")
        # buffer.write("from functools import partial")
        # buffer.write("from numbers import Number")
        # buffer.write("from typing import Any, AsyncGenerator, Dict, List, Generator, Optional")
        # buffer.write("from dataclasses_json import DataClassJsonMixin, config")

        for query in parsed_query_list:
            for class_name, class_type in reversed(query.used_input_types.items()):
                self.render_input(buffer, class_name, class_type)

            for class_name, class_info in reversed(query.type_map.items()):
                self.render_model(buffer, class_name, class_info)
            self.render_model(buffer, f"{query.name}Response", query)

            self.render_input_type(buffer, f"{query.name}Input", query.variable_map)

            buffer.write("")
            buffer.write("")
            with buffer.write_block(f"class {query.name}:"):
                with buffer.write_block("_query = gql('''"):
                    buffer.write_lines(self.get_query_body(query).splitlines())
                buffer.write("''')")
                if query.query.operation in (OperationType.QUERY, OperationType.MUTATION):
                    self.write_execute_method(buffer, query)
                else:
                    pass
        # for fragment_name in sorted(set(parsed_query.used_fragments)):
        #     importpath = fragment_name_to_importpath[fragment_name]
        #     buffer.write(f"from {importpath} import {fragment_name}, " f"QUERY as {fragment_name}Query")
        #     buffer.write("")
        # enum_names = set()
        # for enum in parsed_query.enums:
        #     enum_names.add(enum.name)
        # if enum_names:
        #     buffer.write("from gql.compiler.runtime.enum_utils import enum_field_metadata")
        #     for enum_name in sorted(enum_names):
        #         importpath = enum_name_to_importpath[enum_name]
        #         buffer.write(f"from {importpath} import {enum_name}")
        #     buffer.write("")
        # input_object_names = set()
        # for input_object in parsed_query.input_objects:
        #     input_object_names.add(input_object.name)
        # if input_object_names:
        #     for input_object_name in sorted(input_object_names):
        #         importpath = input_name_to_importpath[input_object_name]
        #         buffer.write(f"from {importpath} import {input_object_name}")
        #     buffer.write("")

        # sorted_objects = sorted(
        #     parsed_query.objects,
        #     key=lambda obj: 1 if isinstance(obj, ParsedOperation) else 0,
        # )
        # for obj in sorted_objects:
        #     buffer.write("")
        #     self.__render_operation(parsed_query, buffer, obj, config_importpath)

        # if parsed_query.fragment_objects:
        #     buffer.write("# fmt: off")
        #     if parsed_query.used_fragments:
        #         queries = [f"{fragment_name}Query" for fragment_name in sorted(set(parsed_query.used_fragments))]
        #         buffer.write(f'QUERY: List[str] = {" + ".join(queries)} + ["""')
        #     else:
        #         buffer.write('QUERY: List[str] = ["""')
        #     buffer.write(parsed_query.query)
        #     buffer.write('"""]')
        #     buffer.write("")

        # for fragment_obj in parsed_query.fragment_objects:
        #     self.__render_fragment(parsed_query, buffer, fragment_obj)

        return str(buffer)

    def get_query_body(self, query: ParsedQuery) -> str:
        body = query.query.loc.source.body  # type: ignore
        return body[query.query.loc.start : query.query.loc.end]  # type: ignore

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

        buffer.write(f'{name}__required = typing.TypedDict("{name}__required", {"{"}{", ".join(r)}{"}"})')
        buffer.write(
            f'{name}__not_required = typing.TypedDict("{name}__not_required", {"{"}{", ".join(nr)}{"}"}, total=False)'
        )
        with buffer.write_block(f"class {name}({name}__required, {name}__not_required):"):
            buffer.write("pass")

    def render_model(self, buffer: CodeChunk, name: str, parsed_field: Union[ParsedField, ParsedQuery]):
        r = [
            f'"{field_name}": {self.type_to_string(field_value.type)}'
            for field_name, field_value in parsed_field.fields.items()
        ]
        buffer.write(f'{name} = typing.TypedDict("{name}", {"{"}{", ".join(r)}{"}"})')

    def type_to_string(self, type_: GraphQLOutputType, isnull: boolean = True) -> str:
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

        buffer.write(f'{name}__required = typing.TypedDict("{name}__required", {"{"}{", ".join(r)}{"}"})')
        buffer.write(
            f'{name}__not_required = typing.TypedDict("{name}__not_required", {"{"}{", ".join(nr)}{"}"}, total=False)'
        )
        with buffer.write_block(f"class {name}({name}__required, {name}__not_required):"):
            buffer.write("pass")

    def write_execute_method(
        self,
        buffer: CodeChunk,
        query: ParsedQuery,
    ) -> None:
        buffer.write("# fmt: off")
        buffer.write("@classmethod")
        var_list: List[str] = []
        for variable in query.query.variable_definitions:
            var_type_str = self.node_type_to_string(variable.type)
            var_list.append(f"{variable.variable.name.value}: {var_type_str}")

        default_variable_values = ""
        if all(x.is_undefinedable for x in query.variable_map.values()):
            default_variable_values = " = {}"

        with buffer.write_block(
            f"def execute(cls, client: Client, variable_values: {query.name}Input{default_variable_values})"
            f" -> {query.name}Response:"
        ):
            buffer.write("return client.execute(  # type: ignore")
            buffer.write("    cls._query, variable_values=variable_values")
            buffer.write(")")
        buffer.write("")

    # def render_enums(self, parsed_query: ParsedQuery) -> Dict[str, str]:
    #     result = {}

    #     for enum in parsed_query.enums + parsed_query.internal_enums:
    #         buffer = CodeChunk()
    #         self.__write_file_header(buffer)
    #         buffer.write("from enum import Enum")
    #         buffer.write("")
    #         buffer.write("")
    #         with buffer.write_block(f"class {enum.name}(Enum):"):
    #             for value_name, value in enum.values.items():
    #                 if isinstance(value, str):
    #                     value = f'"{value}"'

    #                 buffer.write(f"{value_name} = {value}")
    #             buffer.write('MISSING_ENUM = ""')
    #             buffer.write("")
    #             buffer.write("@classmethod")
    #             with buffer.write_block(f'def _missing_(cls, value: object) -> "{enum.name}":'):
    #                 buffer.write("return cls.MISSING_ENUM")
    #         buffer.write("")
    #         result[enum.name] = str(buffer)

    #     return result

    # def render_input_objects(self, parsed_query: ParsedQuery, config_importpath: Optional[str]) -> Dict[str, str]:
    #     result = {}

    #     for input_object in parsed_query.input_objects + parsed_query.internal_inputs:
    #         buffer = CodeChunk()
    #         self.__write_file_header(buffer)
    #         buffer.write("from dataclasses import dataclass, field as _field")
    #         buffer.write("from functools import partial")
    #         self.__render_customer_scalars_imports(buffer, config_importpath)
    #         buffer.write("from numbers import Number")
    #         buffer.write("from typing import Any, AsyncGenerator, Dict, List, Generator," " Optional")
    #         buffer.write("")
    #         buffer.write("from dataclasses_json import DataClassJsonMixin, config")
    #         buffer.write("")
    #         enum_names = set()
    #         for enum in input_object.input_enums:
    #             enum_names.add(enum.name)
    #         if enum_names:
    #             buffer.write("from gql.compiler.runtime.enum_utils import enum_field_metadata")
    #             for enum_name in sorted(enum_names):
    #                 buffer.write(f"from ..enum.{camel_case_to_lower_case(enum_name)}" f" import {enum_name}")
    #             buffer.write("")
    #         input_object_names = set()
    #         for input_dep in input_object.inputs:
    #             input_object_names.add(input_dep.name)
    #         if input_object_names:
    #             for input_object_name in sorted(input_object_names):
    #                 buffer.write(
    #                     f"from ..input.{camel_case_to_lower_case(input_object_name)} " f"import {input_object_name}"
    #                 )
    #             buffer.write("")

    #         buffer.write("")
    #         self.__render_object(parsed_query, buffer, input_object, True)
    #         result[input_object.name] = str(buffer)

    #     return result

    # def __render_object(
    #     self,
    #     parsed_query: ParsedQuery,
    #     buffer: CodeChunk,
    #     obj: ParsedObject,
    #     is_input: bool = False,
    # ) -> None:
    #     class_parents = "(DataClassJsonMixin)" if not obj.parents else f'({", ".join(obj.parents)})'

    #     buffer.write("@dataclass(frozen=True)")
    #     with buffer.write_block(f"class {obj.name}{class_parents}:"):
    #         # render child objects
    #         children_names = set()
    #         for key, child_object in obj.children.items():
    #             if child_object.name not in children_names:
    #                 self.__render_object(parsed_query, buffer, child_object, is_input)
    #             children_names.add(child_object.name)

    #         # render fields
    #         fields = obj.fields
    #         if is_input:
    #             fields = self.__sort_fields(parsed_query, obj.fields)

    #         for field in fields:
    #             self.__render_field(parsed_query, buffer, field, is_input, None)

    #         # pass if not children or fields
    #         if not (obj.children or obj.fields):
    #             buffer.write("pass")

    #     buffer.write("")

    # def __render_fragment(self, parsed_query: ParsedQuery, buffer: CodeChunk, obj: ParsedObject) -> None:
    #     class_parents = "(DataClassJsonMixin)" if not obj.parents else f'({", ".join(obj.parents)})'

    #     buffer.write("@dataclass(frozen=True)")
    #     with buffer.write_block(f"class {obj.name}{class_parents}:"):

    #         # render child objects
    #         children_names = set()
    #         for child_object in obj.children.values():
    #             if child_object.name not in children_names:
    #                 self.__render_object(parsed_query, buffer, child_object)
    #             children_names.add(child_object.name)

    #         # render fields
    #         for field in obj.fields:
    #             self.__render_field(parsed_query, buffer, field, False, None)

    #     buffer.write("")

    # def __render_operation(
    #     self,
    #     parsed_query: ParsedQuery,
    #     buffer: CodeChunk,
    #     parsed_op: ParsedOperation,
    #     config_importpath: Optional[str],
    # ) -> None:
    #     buffer.write("# fmt: off")
    #     if len(parsed_query.used_fragments):
    #         queries = [f"{fragment_name}Query" for fragment_name in sorted(set(parsed_query.used_fragments))]
    #         buffer.write(f'QUERY: List[str] = {" + ".join(queries)} + ["""')
    #     else:
    #         buffer.write('QUERY: List[str] = ["""')
    #     buffer.write(parsed_query.query)
    #     buffer.write('"""')
    #     buffer.write("]")
    #     buffer.write("")
    #     buffer.write("")

    #     # response_type = []
    #     with buffer.write_block(f"class {parsed_op.name}:"):
    #         # Render children
    #         for child_object in parsed_op.children.values():
    #             self.__render_object(parsed_query, buffer, child_object)

    #         # Execution functions
    #         if parsed_op.variables:
    #             vars_args = ", *, " + ", ".join([self.__render_variable_definition(var) for var in parsed_op.variables])
    #             variables_dict = "{" + ", ".join(f'"{var.name}": {var.name}' for var in parsed_op.variables) + "}"
    #         else:
    #             vars_args = ""
    #             variables_dict = "{}"

    #         assert len(parsed_op.children) == 1

    #         # child = parsed_op.children[0]
    #         # query = child.fields[0]
    #         # print(child.fields)
    #         # print(dir(child))
    #         # print(query.type)
    #         # for f, i in zip(child.fields, child.children):
    #         #     print('>', f.name, i.fields)

    #         # child = parsed_op.children[0]
    #         # assert len(child.fields) == 1
    #         # query = child.fields[0]

    #         # for query in child.fields:
    #         #     query_result_type = f"{query.type}"
    #         #     if query_result_type in DEFAULT_MAPPING.keys():
    #         #         query_result_type = DEFAULT_MAPPING.get(
    #         #             query_result_type, query_result_type
    #         #         )
    #         #     elif query_result_type in self.custom_scalars.keys():
    #         #         query_result_type = self.custom_scalars.get(
    #         #             query_result_type, query_result_type
    #         #         ).type.__name__
    #         #     else:
    #         #         query_result_type = f"{parsed_op.name}Data.{query_result_type}"
    #         #     if query.nullable:
    #         #         query_result_type = f"Optional[{query_result_type}]"
    #         #     if query.is_list:
    #         #         query_result_type = f"List[{query_result_type}]"
    #         #     response_type.append({
    #         #         'field_name': query.name,
    #         #         'result_type': query_result_type,
    #         #     })

    #         # query_result_type = f'{parsed_op.name}Response'
    #         query_result_type = f"{parsed_op.name}Data"
    #         if parsed_op.type in ["query", "mutation"]:
    #             self.__write_execute_method(
    #                 buffer,
    #                 vars_args,
    #                 query_result_type,
    #                 variables_dict,
    #                 parsed_op.name,
    #                 config_importpath,
    #             )
    #             self.__write_async_execute_method(
    #                 buffer,
    #                 vars_args,
    #                 query_result_type,
    #                 variables_dict,
    #                 parsed_op.name,
    #                 config_importpath,
    #             )
    #         else:
    #             self.__write_subscribe_method(
    #                 buffer,
    #                 vars_args,
    #                 query_result_type,
    #                 variables_dict,
    #                 parsed_op.name,
    #                 config_importpath,
    #             )
    #             self.__write_async_subscribe_method(
    #                 buffer,
    #                 vars_args,
    #                 query_result_type,
    #                 variables_dict,
    #                 parsed_op.name,
    #                 config_importpath,
    #             )

    # with buffer.write_block(f"class {parsed_op.name}Response:"):
    #     for field in response_type:
    #         buffer.write(f'{field["field_name"]}: {field["result_type"]}')

    # def __render_customer_scalars_imports(self, buffer: CodeChunk, config_importpath: Optional[str]) -> None:
    #     if not config_importpath:
    #         return
    #     scalar_types = set()
    #     for _, custom_scalar in self.custom_scalars.items():
    #         if custom_scalar.type.__module__ != "builtins":
    #             scalar_types.add(custom_scalar.type.__name__)
    #     types_import_line = ", " + ", ".join(scalar_types) if scalar_types else ""
    #     buffer.write(f"from {config_importpath} import custom_scalars{types_import_line}")

    # @staticmethod
    # def __write_async_execute_method(
    #     buffer: CodeChunk,
    #     vars_args: str,
    #     query_result_type: str,
    #     variables_dict: str,
    #     operation_name: str,
    #     config_importpath: Optional[str],
    # ) -> None:
    #     buffer.write("# fmt: off")
    #     buffer.write("@classmethod")
    #     with buffer.write_block(
    #         f"async def execute_async(cls, client: Client{vars_args})" f" -> {query_result_type}:"
    #     ):
    #         buffer.write(f"variables: Dict[str, Any] = {variables_dict}")
    #         scalars = ", custom_scalars" if config_importpath else ""
    #         buffer.write(f"new_variables = encode_variables(variables{scalars})")
    #         buffer.write("response_text = await client.execute_async(")
    #         buffer.write('    gql("".join(set(QUERY))), variable_values=new_variables')
    #         buffer.write(")")
    #         buffer.write(f"res = cls.{operation_name}Data.from_dict(response_text)")
    #         buffer.write(f"return res")
    #     buffer.write("")

    # @staticmethod
    # def __write_subscribe_method(
    #     buffer: CodeChunk,
    #     vars_args: str,
    #     query_result_type: str,
    #     variables_dict: str,
    #     operation_name: str,
    #     config_importpath: Optional[str],
    # ) -> None:
    #     buffer.write("# fmt: off")
    #     buffer.write("@classmethod")
    #     with buffer.write_block(
    #         f"def subscribe(cls, client: Client{vars_args})"
    #         f" -> Generator[{query_result_type}, None, None]:"
    #     ):
    #         buffer.write(f"variables: Dict[str, Any] = {variables_dict}")
    #         scalars = ", custom_scalars" if config_importpath else ""
    #         buffer.write(f"new_variables = encode_variables(variables{scalars})")
    #         buffer.write("subscription = client.subscribe(")
    #         buffer.write('    gql("".join(set(QUERY))), variable_values=new_variables')
    #         buffer.write(")")
    #         with buffer.write_block("for response_text in subscription:"):
    #             buffer.write(f"res = cls.{operation_name}Data.from_dict(response_text)")
    #             buffer.write(f"yield res")
    #     buffer.write("")

    # @staticmethod
    # def __write_async_subscribe_method(
    #     buffer: CodeChunk,
    #     vars_args: str,
    #     query_result_type: str,
    #     variables_dict: str,
    #     operation_name: str,
    #     config_importpath: Optional[str],
    # ) -> None:
    #     buffer.write("# fmt: off")
    #     buffer.write("@classmethod")
    #     with buffer.write_block(
    #         f"async def subscribe_async(cls, client: Client{vars_args})"
    #         f" -> AsyncGenerator[{query_result_type}, None]:"
    #     ):
    #         buffer.write(f"variables: Dict[str, Any] = {variables_dict}")
    #         scalars = ", custom_scalars" if config_importpath else ""
    #         buffer.write(f"new_variables = encode_variables(variables{scalars})")
    #         buffer.write("subscription = client.subscribe_async(")
    #         buffer.write('    gql("".join(set(QUERY))), variable_values=new_variables')
    #         buffer.write(")")
    #         with buffer.write_block("async for response_text in subscription:"):
    #             buffer.write(f"res = cls.{operation_name}Data.from_dict(response_text)")
    #             buffer.write(f"yield res")
    #     buffer.write("")

    # @staticmethod
    # def __sort_fields(parsed_query: ParsedQuery, fields: List[ParsedField]) -> List[ParsedField]:
    #     def sort_key(field) -> int:
    #         if field.nullable:
    #             return 2
    #         return 0

    #     return sorted(fields, key=sort_key)

    # def __render_variable_definition(self, var: ParsedVariableDefinition):
    #     var_type = DEFAULT_MAPPING.get(var.type, var.type)

    #     if var.type in self.custom_scalars.keys():
    #         var_type = self.custom_scalars[var.type].type.__name__

    #     if var.is_list:
    #         return f"{var.name}: List[{var_type}] = []"

    #     if not var.nullable:
    #         return f"{var.name}: {var_type}"

    #     return f'{var.name}: Optional[{var_type}] = {var.default_value or "None"}'

    # def __render_field(
    #     self,
    #     parsed_query: ParsedQuery,
    #     buffer: CodeChunk,
    #     field: ParsedField,
    #     is_input: bool,
    #     child,
    # ) -> None:
    #     enum_names = [e.name for e in parsed_query.enums + parsed_query.internal_enums]
    #     is_enum = field.type in enum_names
    #     suffix = ""
    #     # if child.fields:
    #     #     field_type = "HOGE"

    #     #     print(field)

    #     #     for f, c in zip(child.fields, child.children):
    #     #         print(f, c, c.name)

    #     #     self.__render_object(
    #     #         parsed_query, buffer, child, is_input
    #     #     )
    #     # else:
    #     # field_type = DEFAULT_MAPPING.get(field.type, field.type)

    #     field_type = DEFAULT_MAPPING.get(field.type, field.type)
    #     if field.is_list:
    #         field_type = f"List[{field_type}]"

    #     if is_enum:
    #         suffix = f" = _field(metadata=enum_field_metadata({field_type}))"

    #     if field_type in self.custom_scalars.keys():
    #         if (
    #             self.custom_scalars[field_type].encoder
    #             or self.custom_scalars[field_type].decoder
    #             or self.custom_scalars[field_type].mm_field
    #         ):
    #             suffix = (
    #                 " = _field(metadata=config("
    #                 f'encoder=custom_scalars["{field_type}"].encoder, '
    #                 f'decoder=custom_scalars["{field_type}"].decoder, '
    #                 f'mm_field=custom_scalars["{field_type}"].mm_field))'
    #             )
    #         field_type = self.custom_scalars[field_type].type.__name__

    #     if field.nullable:
    #         if is_input:
    #             suffix = f" = {field.default_value}"
    #         buffer.write(f"{field.name}: Optional[{field_type}]{suffix}")
    #     else:
    #         buffer.write(f"{field.name}: {field_type}{suffix}")

    @staticmethod
    def __write_file_header(buffer: CodeChunk) -> None:
        # buffer.write("#!/usr/bin/env python3")
        buffer.write("# @" + "generated AUTOGENERATED file. Do not Change!")
        buffer.write("")
