import argparse
from typing import List, Optional

import yaml
from graphql import GraphQLSchema, build_ast_schema
from graphql.language.parser import parse

from gql_compiler import cli
from gql_compiler.types import Config


DEFAULT_CONFIG: Config = {
    "output_path": "{dirname}/{basename_without_ext}.py",
    "scalar_map": {
        "Date": {
            "import": "import datetime",
            "value": "datetime.date",
        },
        "DateTime": {
            "import": "import datetime",
            "value": "datetime.datetime",
        },
        "Time": {
            "import": "import datetime",
            "value": "datetime.time",
        },
    },
}


def compile_schema_library(schema_filepaths: List[str]) -> GraphQLSchema:
    full_schema = ""
    for schema_filepath in schema_filepaths:
        with open(schema_filepath) as schema_file:
            full_schema = full_schema + schema_file.read()

    return build_ast_schema(parse(full_schema))


def load_config_file(config_file: Optional[str]) -> Config:
    config = DEFAULT_CONFIG
    if config_file:
        config.update(yaml.safe_load(open(config_file)))
    return config


def __entry_point():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--schema",
        help="the graphql schemas storage path",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "-q",
        "--queries-dir",
        help="path where all queries files are stored",
        type=str,
    )
    parser.add_argument("-g", "--graphql-file", help="path where all queries file", type=str, nargs="*")
    parser.add_argument("--config", help="path where config yaml file", type=str)
    args = parser.parse_args()
    schema = compile_schema_library(args.schema)
    config = load_config_file(args.config)

    cli.run(
        schema=schema,
        queries_dir=args.queries_dir,
        graphql_file=args.graphql_file,
        config=config,
    )


if __name__ == "__main__":
    __entry_point()
