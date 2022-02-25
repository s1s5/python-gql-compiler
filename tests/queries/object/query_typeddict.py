# @generated AUTOGENERATED file. Do not Change!
# flake8: noqa
# fmt: off
# isort: skip_file

import typing
from gql import gql, Client
Episode = typing.Literal["NEWHOPE", "EMPIRE", "JEDI"]


GetObject__droid = typing.TypedDict("GetObject__droid", {"id": str, "name": str, "appearsIn": typing.List[Episode], "primaryFunction": str})


GetObjectResponse = typing.TypedDict("GetObjectResponse", {"droid": GetObject__droid})


_GetObjectInput__required = typing.TypedDict("_GetObjectInput__required", {"id": str})
_GetObjectInput__not_required = typing.TypedDict("_GetObjectInput__not_required", {}, total=False)


class _GetObjectInput(_GetObjectInput__required, _GetObjectInput__not_required):
    pass


class GetObject:
    Response = GetObjectResponse
    Input = _GetObjectInput
    _query = gql('''
        query GetObject($id: ID!) {
          droid(id: $id) {
            id name appearsIn primaryFunction
          }
        }
    ''')
    @classmethod
    def execute(cls, client: Client, variable_values: _GetObjectInput) -> GetObjectResponse:
        return client.execute(  # type: ignore
            cls._query, variable_values=variable_values
        )
    @classmethod
    def execute_async(cls, client: Client, variable_values: _GetObjectInput) -> typing.Awaitable[GetObjectResponse]:
        return client.execute_async(  # type: ignore
            cls._query, variable_values=variable_values
        )
