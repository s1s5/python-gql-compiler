import datetime
from typing import Any, Dict, Optional
from graphql.utilities import value_from_ast_untyped
from graphql import GraphQLScalarType, ValueNode
from gql.utilities import update_schema_scalar


def serialize_date(value: Any) -> str:
    return value.isoformat()


def parse_date_value(value: Any) -> datetime.date:
    return datetime.date.fromisoformat(value)


def parse_date_literal(value_node: ValueNode, variables: Optional[Dict[str, Any]] = None) -> datetime.date:
    ast_value = value_from_ast_untyped(value_node, variables)
    return parse_date_value(ast_value)


DateScalar = GraphQLScalarType(
    name="Date",
    serialize=serialize_date,
    parse_value=parse_date_value,
    parse_literal=parse_date_literal,
)


def register_parsers(schema):
    update_schema_scalar(schema, "Date", DateScalar)
