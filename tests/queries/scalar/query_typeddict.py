# @generated AUTOGENERATED file. Do not Change!
# flake8: noqa
# fmt: off
# isort: skip_file

import typing
from gql import gql, Client


GetScalarResponse = typing.TypedDict("GetScalarResponse", {"hello": str})


_GetScalarInput__required = typing.TypedDict("_GetScalarInput__required", {})
_GetScalarInput__not_required = typing.TypedDict("_GetScalarInput__not_required", {}, total=False)


class _GetScalarInput(_GetScalarInput__required, _GetScalarInput__not_required):
    pass


class GetScalar:
    Response: typing.TypeAlias = GetScalarResponse
    Input: typing.TypeAlias = _GetScalarInput
    _query = gql('''
        query GetScalar {
          hello
        }
    ''')
    @classmethod
    def execute(cls, client: Client, variable_values: _GetScalarInput = {}) -> GetScalarResponse:
        return client.execute(  # type: ignore
            cls._query, variable_values=variable_values
        )
    @classmethod
    def execute_async(cls, client: Client, variable_values: _GetScalarInput = {}) -> typing.Awaitable[GetScalarResponse]:
        return client.execute_async(  # type: ignore
            cls._query, variable_values=variable_values
        )
