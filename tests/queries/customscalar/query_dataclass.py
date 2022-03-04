# @generated AUTOGENERATED file. Do not Change!
# flake8: noqa
# fmt: off
# isort: skip_file

import typing
import copy
from dataclasses import dataclass
from gql import gql, Client
import datetime


def rewrite_typename(value: typing.Any):
    if isinstance(value, dict) and '__typename' in value:
        value = copy.copy(value)
        value['_typename'] = value.pop('__typename')
    return value



@dataclass
class GetCustomScalarResponse:
    today: datetime.date


_GetCustomScalarInput__required = typing.TypedDict("_GetCustomScalarInput__required", {})
_GetCustomScalarInput__not_required = typing.TypedDict("_GetCustomScalarInput__not_required", {}, total=False)


class _GetCustomScalarInput(_GetCustomScalarInput__required, _GetCustomScalarInput__not_required):
    pass


class GetCustomScalar:
    Response: typing.TypeAlias = GetCustomScalarResponse
    Input: typing.TypeAlias = _GetCustomScalarInput
    _query = gql('''
        query GetCustomScalar {
          today
        }
    ''')
    @classmethod
    def execute(cls, client: Client, variable_values: _GetCustomScalarInput = {}) -> GetCustomScalarResponse:
        return cls.Response(**rewrite_typename(client.execute(  # type: ignore
            cls._query, variable_values=variable_values
        )))
    @classmethod
    async def execute_async(cls, client: Client, variable_values: _GetCustomScalarInput = {}) -> GetCustomScalarResponse:
        return cls.Response(**rewrite_typename(await client.execute_async(  # type: ignore
            cls._query, variable_values=variable_values
        )))
