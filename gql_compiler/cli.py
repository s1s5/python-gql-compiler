import glob
import os
from enum import Enum
from typing import Dict, List, Optional, Tuple

from graphql import GraphQLSchema
from graphql.language import FragmentDefinitionNode, OperationDefinitionNode
from graphql.language.ast import DocumentNode
from graphql.language.parser import parse

# from graphql.utilities.find_deprecated_usages import find_deprecated_usages

# from .constant import ENUM_DIRNAME, INPUT_DIRNAME
from .parser import InvalidQueryError, Parser

# from .renderer import Renderer
# from .utils_codegen import CodeChunk, camel_case_to_lower_case


def assert_rendered_file(file_name: str, file_content: str, rendered: str) -> None:
    assert (
        rendered == file_content
    ), f"""Generated file name {file_name} does
            not match compilation result:
            existing file:
            {file_content}
            compilation result:
            {rendered}"""


def safe_remove(fname: str) -> None:
    try:
        os.remove(fname)
    except BaseException:
        pass


def add_init_file(pkg_name: str) -> None:
    init_file_path = os.path.join(pkg_name, "__init__.py")
    if not os.path.exists(init_file_path):
        with open(init_file_path, "w") as outfile:
            buffer = CodeChunk()
            buffer.write("#!/usr/bin/env python3")
            buffer.write("")
            outfile.write(str(buffer))


def verify_or_write_rendered(filename: str, rendered: str, verify: bool) -> None:
    if verify:
        with open(filename, "r") as f:
            file_content = f.read()
            assert_rendered_file(filename, file_content, rendered)
    else:
        with open(filename, "w") as outfile:
            outfile.write(rendered)


def make_python_package(pkg_name: str) -> None:
    if not os.path.exists(pkg_name):
        os.makedirs(pkg_name)
    add_init_file(pkg_name)


def root_no_ext(filename):
    root, _s = os.path.splitext(filename)
    return root


def get_import_path(filename, target_dirname):
    importpath = (
        root_no_ext(os.path.relpath(filename, target_dirname))
        .replace("../../../", "....")
        .replace("../../", "...")
        .replace("../", "..")
        .replace("/", ".")
    )
    if not importpath.startswith("."):
        return "." + importpath
    return importpath


# def process_file(
#     filename: str,
#     query: str,
#     schema: GraphQLSchema,
#     parser: QueryParser,
#     renderer,  # : DataclassesRenderer,
#     fragment_library: Dict[str, Tuple[str, str]],
#     enum_dir_path: str,
#     input_dir_path: str,
#     config_path: Optional[str],
#     verify: bool = False,
# ) -> None:
#     full_fragments = "".join(
#         [query for fragment_filename, query in fragment_library.values() if fragment_filename != filename]
#     )

#     target_filename = "".join([root_no_ext(filename), ".py"])
#     target_dirname = os.path.dirname(filename)

#     try:
#         parsed = parser.parse(query, full_fragments)
#         fragment_name_to_importpath = {
#             name: get_import_path(details[0], target_dirname) for name, details in fragment_library.items()
#         }

#         enum_name_to_importpath = {}
#         enums = renderer.render_enums(parsed)
#         for enum_name, code in enums.items():
#             target_enum_filename = os.path.join(enum_dir_path, "".join([camel_case_to_lower_case(enum_name), ".py"]))
#             verify_or_write_rendered(target_enum_filename, code, verify)
#             enum_name_to_importpath[enum_name] = get_import_path(target_enum_filename, target_dirname)

#         input_name_to_importpath = {}
#         input_objects = renderer.render_input_objects(
#             parsed,
#             get_import_path(config_path, input_dir_path) if config_path else None,
#         )
#         for input_object_name, code in input_objects.items():
#             target_input_object_filename = os.path.join(
#                 input_dir_path,
#                 "".join([camel_case_to_lower_case(input_object_name), ".py"]),
#             )
#             verify_or_write_rendered(target_input_object_filename, code, verify)
#             input_name_to_importpath[input_object_name] = get_import_path(target_input_object_filename, target_dirname)

#         rendered = renderer.render(
#             parsed,
#             fragment_name_to_importpath,
#             enum_name_to_importpath,
#             input_name_to_importpath,
#             get_import_path(config_path, target_dirname) if config_path else None,
#         )
#         verify_or_write_rendered(target_filename, rendered, verify)
#     except (InvalidQueryError, AssertionError):
#         if verify:
#             print(f"Failed to verify graphql file {filename}")
#         else:
#             print(f"Failed to process graphql file {filename}")
#         safe_remove(target_filename)
#         raise


def run(
    schema: GraphQLSchema,
    queries_dir: str,
    graphql_file: List[str],
    config_path: Optional[str] = None,
) -> None:
    query_parser = Parser(schema)
    # query_renderer = Renderer(schema, config_path)
    if queries_dir:
        graphql_file = graphql_file + list(glob.glob(os.path.join(queries_dir, "**/*.graphql"), recursive=True))

    operation_library: List[Tuple[str, OperationDefinitionNode]] = []
    fragment_library: Dict[str, Tuple[str, FragmentDefinitionNode]] = {}

    for filename in graphql_file:
        parsed_query = parse(open(filename, "r").read())
        for definition in parsed_query.definitions:
            if isinstance(definition, OperationDefinitionNode):
                assert definition.name
                operation_library.append((filename, definition))
            elif isinstance(definition, FragmentDefinitionNode):
                assert definition.name
                fragment_library[definition.name.value] = (filename, definition)
            # import code
            # code.interact(local=locals())

    # for filename, query in fragment_library.values():
    #     process_file(
    #         filename,
    #         query,
    #         schema,
    #         query_parser,
    #         query_renderer,
    #         fragment_library,
    #         enum_dir_path,
    #         input_dir_path,
    #         config_path,
    #         verify,
    #     )
    
    for filename, query in operation_library:
        parsed = query_parser.parse(query)
        print(parsed)

        import code
        code.interact(local=locals())

        # process_file(
        #     filename,
        #     query,
        #     schema,
        #     query_parser,
        #     query_renderer,
        #     fragment_library,
        #     enum_dir_path,
        #     input_dir_path,
        #     config_path,
        #     verify,
        # )
