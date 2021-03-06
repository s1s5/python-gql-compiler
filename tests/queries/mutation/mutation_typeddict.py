# @generated AUTOGENERATED file. Do not Change!
# flake8: noqa
# fmt: off
# isort: skip_file

import typing
from gql import gql, Client


AddStarshipInput__required = typing.TypedDict("AddStarshipInput__required", {"name": str})
AddStarshipInput__not_required = typing.TypedDict("AddStarshipInput__not_required", {}, total=False)


class AddStarshipInput(AddStarshipInput__required, AddStarshipInput__not_required):
    pass


AddStarship__addStarship = typing.TypedDict("AddStarship__addStarship", {"id": str, "name": str})


AddStarshipResponse = typing.TypedDict("AddStarshipResponse", {"addStarship": AddStarship__addStarship})


_AddStarshipInput__required = typing.TypedDict("_AddStarshipInput__required", {"input": AddStarshipInput})
_AddStarshipInput__not_required = typing.TypedDict("_AddStarshipInput__not_required", {}, total=False)


class _AddStarshipInput(_AddStarshipInput__required, _AddStarshipInput__not_required):
    pass


class AddStarship:
    Response: typing.TypeAlias = AddStarshipResponse
    Input: typing.TypeAlias = _AddStarshipInput
    _query = gql('''
        mutation AddStarship($input: AddStarshipInput!) {
          addStarship(input: $input) {
            id name
          }
        }
    ''')
    @classmethod
    def execute(cls, client: Client, variable_values: _AddStarshipInput) -> AddStarshipResponse:
        return client.execute(  # type: ignore
            cls._query, variable_values=variable_values
        )
    @classmethod
    def execute_async(cls, client: Client, variable_values: _AddStarshipInput) -> typing.Awaitable[AddStarshipResponse]:
        return client.execute_async(  # type: ignore
            cls._query, variable_values=variable_values
        )
