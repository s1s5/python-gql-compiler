import argparse
import glob
import os
from typing import List

from graphql import GraphQLSchema, build_ast_schema
from graphql.language.parser import parse

from gql_compiler import cli


def compile_schema_library(schema_filepaths: List[str]) -> GraphQLSchema:
    full_schema = ''
    for schema_filepath in schema_filepaths:
        with open(schema_filepath) as schema_file:
            full_schema = full_schema + schema_file.read()

    return build_ast_schema(parse(full_schema))


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
    parser.add_argument(
        "-g",
        "--graphql-file",
        help="path where all queries file",
        type=str,
        nargs='*'
    )
    parser.add_argument("--config_path", help="path where custom scalars are configured", type=str)
    args = parser.parse_args()
    schema = compile_schema_library(args.schema)

    cli.run(
        schema=schema,
        queries_dir=args.queries_dir,
        graphql_file=args.graphql_file,
        config_path=args.config_path,
    )


if __name__ == "__main__":
    __entry_point()
