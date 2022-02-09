# @generated AUTOGENERATED file. Do not Change!

import typing
from gql import gql, Client
import datetime


GetScalarResponse = typing.TypedDict("GetScalarResponse", {"hello": str})


GetScalarInput__required = typing.TypedDict("GetScalarInput__required", {})
GetScalarInput__not_required = typing.TypedDict("GetScalarInput__not_required", {}, total=False)


class GetScalarInput(GetScalarInput__required, GetScalarInput__not_required):
    pass


class GetScalar:
    _query = gql('''
        query GetScalar {
          hello
        }
    ''')
    @classmethod
    def execute(cls, client: Client, variable_values: GetScalarInput = {}) -> GetScalarResponse:
        return client.execute(  # type: ignore
            cls._query, variable_values=variable_values
        )
    @classmethod
    def execute_async(cls, client: Client, variable_values: GetScalarInput = {}) -> GetScalarResponse:
        return client.execute_async(  # type: ignore
            cls._query, variable_values=variable_values
        )
Episode = typing.Literal["NEWHOPE", "EMPIRE", "JEDI"]


GetObject__droid = typing.TypedDict("GetObject__droid", {"id": str, "name": str, "appearsIn": typing.List[Episode], "primaryFunction": str})


GetObjectResponse = typing.TypedDict("GetObjectResponse", {"droid": GetObject__droid})


GetObjectInput__required = typing.TypedDict("GetObjectInput__required", {"id": str})
GetObjectInput__not_required = typing.TypedDict("GetObjectInput__not_required", {}, total=False)


class GetObjectInput(GetObjectInput__required, GetObjectInput__not_required):
    pass


class GetObject:
    _query = gql('''
        query GetObject($id: ID!) {
          droid(id: $id) {
            id name appearsIn primaryFunction
          }
        }
    ''')
    @classmethod
    def execute(cls, client: Client, variable_values: GetObjectInput) -> GetObjectResponse:
        return client.execute(  # type: ignore
            cls._query, variable_values=variable_values
        )
    @classmethod
    def execute_async(cls, client: Client, variable_values: GetObjectInput) -> GetObjectResponse:
        return client.execute_async(  # type: ignore
            cls._query, variable_values=variable_values
        )
Episode = typing.Literal["NEWHOPE", "EMPIRE", "JEDI"]


GetInterface__hero = typing.TypedDict("GetInterface__hero", {"id": str, "name": str})


GetInterfaceResponse = typing.TypedDict("GetInterfaceResponse", {"hero": GetInterface__hero})


GetInterfaceInput__required = typing.TypedDict("GetInterfaceInput__required", {"e": Episode})
GetInterfaceInput__not_required = typing.TypedDict("GetInterfaceInput__not_required", {}, total=False)


class GetInterfaceInput(GetInterfaceInput__required, GetInterfaceInput__not_required):
    pass


class GetInterface:
    _query = gql('''
        query GetInterface($e: Episode!) {
          hero(episode: $e) {
            id name
          }
        }
    ''')
    @classmethod
    def execute(cls, client: Client, variable_values: GetInterfaceInput) -> GetInterfaceResponse:
        return client.execute(  # type: ignore
            cls._query, variable_values=variable_values
        )
    @classmethod
    def execute_async(cls, client: Client, variable_values: GetInterfaceInput) -> GetInterfaceResponse:
        return client.execute_async(  # type: ignore
            cls._query, variable_values=variable_values
        )
Episode = typing.Literal["NEWHOPE", "EMPIRE", "JEDI"]


GetInlineFragment__hero__Droid = typing.TypedDict("GetInlineFragment__hero__Droid", {"__typename": typing.Literal["Droid"], "id": str, "name": str, "primaryFunction": str})


GetInlineFragment__hero__Human = typing.TypedDict("GetInlineFragment__hero__Human", {"__typename": typing.Literal["Human"], "id": str, "name": str, "totalCredits": int})


__GetInlineFragment__hero = typing.TypedDict("__GetInlineFragment__hero", {"__typename": typing.Literal["Character"], "id": str, "name": str})
GetInlineFragment__hero = typing.Union[__GetInlineFragment__hero, GetInlineFragment__hero__Human, GetInlineFragment__hero__Droid]


GetInlineFragmentResponse = typing.TypedDict("GetInlineFragmentResponse", {"hero": GetInlineFragment__hero})


GetInlineFragmentInput__required = typing.TypedDict("GetInlineFragmentInput__required", {"e": Episode})
GetInlineFragmentInput__not_required = typing.TypedDict("GetInlineFragmentInput__not_required", {}, total=False)


class GetInlineFragmentInput(GetInlineFragmentInput__required, GetInlineFragmentInput__not_required):
    pass


class GetInlineFragment:
    _query = gql('''
        query GetInlineFragment($e: Episode!) {
          hero(episode: $e) {
            __typename id name
            ... on Human { totalCredits }
            ... on Droid { primaryFunction }
          }
        }
    ''')
    @classmethod
    def execute(cls, client: Client, variable_values: GetInlineFragmentInput) -> GetInlineFragmentResponse:
        return client.execute(  # type: ignore
            cls._query, variable_values=variable_values
        )
    @classmethod
    def execute_async(cls, client: Client, variable_values: GetInlineFragmentInput) -> GetInlineFragmentResponse:
        return client.execute_async(  # type: ignore
            cls._query, variable_values=variable_values
        )


GetCustomScalarResponse = typing.TypedDict("GetCustomScalarResponse", {"today": datetime.date})


GetCustomScalarInput__required = typing.TypedDict("GetCustomScalarInput__required", {})
GetCustomScalarInput__not_required = typing.TypedDict("GetCustomScalarInput__not_required", {}, total=False)


class GetCustomScalarInput(GetCustomScalarInput__required, GetCustomScalarInput__not_required):
    pass


class GetCustomScalar:
    _query = gql('''
        query GetCustomScalar {
          today
        }
    ''')
    @classmethod
    def execute(cls, client: Client, variable_values: GetCustomScalarInput = {}) -> GetCustomScalarResponse:
        return client.execute(  # type: ignore
            cls._query, variable_values=variable_values
        )
    @classmethod
    def execute_async(cls, client: Client, variable_values: GetCustomScalarInput = {}) -> GetCustomScalarResponse:
        return client.execute_async(  # type: ignore
            cls._query, variable_values=variable_values
        )


GetUnion__search__Starship = typing.TypedDict("GetUnion__search__Starship", {"__typename": typing.Literal["Starship"], "name": str})


GetUnion__search__Droid__friends = typing.TypedDict("GetUnion__search__Droid__friends", {"name": str})


GetUnion__search__Droid = typing.TypedDict("GetUnion__search__Droid", {"__typename": typing.Literal["Droid"], "friends": typing.List[typing.Optional[GetUnion__search__Droid__friends]]})


GetUnion__search__Human = typing.TypedDict("GetUnion__search__Human", {"__typename": typing.Literal["Human"], "totalCredits": int})


__GetUnion__search = typing.TypedDict("__GetUnion__search", {"__typename": typing.Literal["SearchResult"]})
GetUnion__search = typing.Union[__GetUnion__search, GetUnion__search__Human, GetUnion__search__Droid, GetUnion__search__Starship]


GetUnionResponse = typing.TypedDict("GetUnionResponse", {"search": typing.List[GetUnion__search]})


GetUnionInput__required = typing.TypedDict("GetUnionInput__required", {"text": str})
GetUnionInput__not_required = typing.TypedDict("GetUnionInput__not_required", {}, total=False)


class GetUnionInput(GetUnionInput__required, GetUnionInput__not_required):
    pass


class GetUnion:
    _query = gql('''
        query GetUnion($text: String!) {
          search(text: $text) {
            __typename
            ... on Human { totalCredits }
            ... on Droid { friends { name } }
            ... on Starship { name }
          }
        }
    ''')
    @classmethod
    def execute(cls, client: Client, variable_values: GetUnionInput) -> GetUnionResponse:
        return client.execute(  # type: ignore
            cls._query, variable_values=variable_values
        )
    @classmethod
    def execute_async(cls, client: Client, variable_values: GetUnionInput) -> GetUnionResponse:
        return client.execute_async(  # type: ignore
            cls._query, variable_values=variable_values
        )
