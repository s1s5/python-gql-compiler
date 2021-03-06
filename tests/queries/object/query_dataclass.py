# @generated AUTOGENERATED file. Do not Change!
# flake8: noqa
# fmt: off
# isort: skip_file

import typing
import copy
from dataclasses import dataclass
from gql import gql, Client


def rewrite_typename(value: typing.Any):
    if isinstance(value, dict) and '__typename' in value:
        value = copy.copy(value)
        value['_typename'] = value.pop('__typename')
    return value

Episode = typing.Literal["NEWHOPE", "EMPIRE", "JEDI"]


@dataclass
class GetObject__droid:
    id: str
    name: str
    appearsIn: typing.List[Episode]
    primaryFunction: str


@dataclass
class GetObjectResponse:
    droid: GetObject__droid
    def __init__(self, droid):
        self.droid = GetObject__droid(**rewrite_typename(droid))


_GetObjectInput__required = typing.TypedDict("_GetObjectInput__required", {"id": str})
_GetObjectInput__not_required = typing.TypedDict("_GetObjectInput__not_required", {}, total=False)


class _GetObjectInput(_GetObjectInput__required, _GetObjectInput__not_required):
    pass


class GetObject:
    Response: typing.TypeAlias = GetObjectResponse
    Input: typing.TypeAlias = _GetObjectInput
    _query = gql('''
        query GetObject($id: ID!) {
          droid(id: $id) {
            id name appearsIn primaryFunction
          }
        }
    ''')
    @classmethod
    def execute(cls, client: Client, variable_values: _GetObjectInput) -> GetObjectResponse:
        return cls.Response(**rewrite_typename(client.execute(  # type: ignore
            cls._query, variable_values=variable_values
        )))
    @classmethod
    async def execute_async(cls, client: Client, variable_values: _GetObjectInput) -> GetObjectResponse:
        return cls.Response(**rewrite_typename(await client.execute_async(  # type: ignore
            cls._query, variable_values=variable_values
        )))
