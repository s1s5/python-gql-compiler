# @generated AUTOGENERATED file. Do not Change!
# flake8: noqa
# fmt: off
# isort: skip_file

import typing
from gql import gql, Client


AllHumanSubsc__allHuman = typing.TypedDict("AllHumanSubsc__allHuman", {"id": str, "name": str})


AllHumanSubscResponse = typing.TypedDict("AllHumanSubscResponse", {"allHuman": AllHumanSubsc__allHuman})


_AllHumanSubscInput__required = typing.TypedDict("_AllHumanSubscInput__required", {})
_AllHumanSubscInput__not_required = typing.TypedDict("_AllHumanSubscInput__not_required", {}, total=False)


class _AllHumanSubscInput(_AllHumanSubscInput__required, _AllHumanSubscInput__not_required):
    pass


class AllHumanSubsc:
    Response: typing.TypeAlias = AllHumanSubscResponse
    Input: typing.TypeAlias = _AllHumanSubscInput
    _query = gql('''
        subscription AllHumanSubsc {
          allHuman {
            id name
          }
        }
    ''')
    @classmethod
    def subscribe(cls, client: Client, variable_values: _AllHumanSubscInput = {}) -> typing.Iterable[AllHumanSubscResponse]:
        for r in client.subscribe(cls._query, variable_values=variable_values):  # type: ignore
            yield r  # type: ignore
    @classmethod
    async def subscribe_async(cls, client: Client, variable_values: _AllHumanSubscInput = {}) -> typing.AsyncIterable[AllHumanSubscResponse]:
        async for r in client.subscribe_async(cls._query, variable_values=variable_values):  # type: ignore
            yield r  # type: ignore
