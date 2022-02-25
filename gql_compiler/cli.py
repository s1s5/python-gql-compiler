import os
from collections import defaultdict
from typing import Dict, List

from graphql import GraphQLSchema, validate
from graphql.language import FragmentDefinitionNode, OperationDefinitionNode
from graphql.language.parser import parse
from graphql.validation.rules.no_unused_fragments import NoUnusedFragmentsRule
from graphql.validation.specified_rules import specified_rules

from .parser import Parser
from .renderer import Renderer
from .types import Config


def run(
    schema: GraphQLSchema,
    query_files: List[str],
    config: Config,
) -> None:
    query_parser = Parser(schema)
    query_renderer = Renderer(
        schema, scalar_map=config["scalar_map"], render_as_typed_dict=config["output_type"] == "typeddict"
    )

    operation_library: Dict[str, List[OperationDefinitionNode]] = defaultdict(list)
    fragment_library: Dict[str, List[FragmentDefinitionNode]] = defaultdict(list)

    rules = [rule for rule in specified_rules if rule is not NoUnusedFragmentsRule]
    for filename in query_files:
        parsed_query = parse(open(filename, "r").read())
        errors = validate(schema, parsed_query, rules)
        if errors:
            raise Exception(errors)
        for definition in parsed_query.definitions:
            if isinstance(definition, OperationDefinitionNode):
                assert definition.name
                operation_library[filename].append(definition)
            elif isinstance(definition, FragmentDefinitionNode):
                assert definition.name
                fragment_library[filename].append(definition)

    for filename, definition_list in operation_library.items():
        parsed_list = [query_parser.parse(definition) for definition in definition_list]

        if config.get("output_path"):
            dirname = os.path.dirname(filename)
            basename = os.path.basename(filename)
            basename_without_ext, ext = os.path.splitext(basename)
            dst_path = config["output_path"].format(
                dirname=dirname, basename=basename, basename_without_ext=basename_without_ext, ext=ext
            )
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            with open(dst_path, "w") as fp:
                print(query_renderer.render(parsed_list), file=fp)
