import argparse
import glob
import os
from typing import List, Optional, Set
import json

import yaml
from graphql import GraphQLSchema, build_ast_schema, get_introspection_query
from graphql.utilities.print_schema import print_schema
from graphql.language.parser import parse
from gql.utilities import build_client_schema
import requests

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
    "query_ext": "graphql",
}


def compile_schema_library(schema_filepaths: List[str]) -> GraphQLSchema:
    full_schema = ""
    for schema_filepath in schema_filepaths:
        if schema_filepath.startswith("http"):
            res = requests.post(
                schema_filepath,
                headers={"Content-Type": "application/json"},
                data=json.dumps({"query": get_introspection_query()}),
            )
            res.raise_for_status()
            full_schema = full_schema + print_schema(build_client_schema(res.json()["data"]))
        else:
            with open(schema_filepath) as schema_file:
                full_schema = full_schema + schema_file.read()

    return build_ast_schema(parse(full_schema))


def extract_query_files(queries: List[str], config: Config) -> List[str]:
    results: Set[str] = set()
    for f_or_d in queries:
        if not os.path.exists(f_or_d):
            continue
        if os.path.isfile(f_or_d):
            results.add(f_or_d)
        if os.path.isdir(f_or_d):
            results.update(glob.glob(os.path.join(f_or_d, f'**/*.{config["query_ext"]}')))
    return list(results)


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
        help="the graphql schemas storage path or url",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "-q",
        "--query",
        help="path where query file or all queries files are stored",
        type=str,
        nargs="+",
    )
    parser.add_argument("--config", help="path where config yaml file", type=str)
    args = parser.parse_args()
    schema = compile_schema_library(args.schema)
    config = load_config_file(args.config)
    query_files = extract_query_files(args.query, config)

    cli.run(
        schema=schema,
        query_files=query_files,
        config=config,
    )


if __name__ == "__main__":
    __entry_point()
