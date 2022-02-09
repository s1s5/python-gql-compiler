import glob
import os
from typing import Dict, List, Optional
from collections import defaultdict

from graphql import GraphQLSchema, validate
from graphql.language import FragmentDefinitionNode, OperationDefinitionNode
from graphql.language.parser import parse
from graphql.validation.rules.no_unused_fragments import NoUnusedFragmentsRule
from graphql.validation.specified_rules import specified_rules

from .parser import Parser
from .renderer import Renderer


def run(
    schema: GraphQLSchema,
    queries_dir: str,
    graphql_file: List[str],
    config_path: Optional[str] = None,
) -> None:
    query_parser = Parser(schema)
    query_renderer = Renderer(schema)
    if queries_dir:
        graphql_file = graphql_file + list(
            glob.glob(os.path.join(queries_dir, "**/*.graphql"), recursive=True)
        )

    operation_library: Dict[str, List[OperationDefinitionNode]] = defaultdict(list)
    fragment_library: Dict[str, List[FragmentDefinitionNode]] = defaultdict(list)

    rules = [rule for rule in specified_rules if rule is not NoUnusedFragmentsRule]
    for filename in graphql_file:
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
        print(query_renderer.render(parsed_list))

        import code

        code.interact(local=locals())
