import asyncio
import datetime

import client_queries
import custom_scalars
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.websockets import WebsocketsTransport

transport = AIOHTTPTransport(url="http://localhost:8000")
client = Client(transport=transport, fetch_schema_from_transport=True, parse_results=True)


async def register_parsers():
    async with client:  # force fetch schema
        custom_scalars.register_parsers(client.schema)


asyncio.run(register_parsers())

result0 = client_queries.GetScalar.execute(client)
assert result0 == {"hello": "hello world"}


async def execute_async():
    result0 = await client_queries.GetScalar.execute_async(client)
    assert result0 == {"hello": "hello world"}


asyncio.run(execute_async())


result1 = client_queries.GetObject.execute(client, {"id": "d-1"})
assert result1 == {
    "droid": {"id": "d-1", "name": "C-3PO", "appearsIn": ["NEWHOPE"], "primaryFunction": "search"}
}

result2 = client_queries.GetInterface.execute(client, {"e": "NEWHOPE"})
assert result2 == {"hero": {"id": "h-1", "name": "luke"}}

result3 = client_queries.GetInlineFragment.execute(client, {"e": "EMPIRE"})
assert result3 == {"hero": {"__typename": "Human", "id": "h-2", "name": "obi", "totalCredits": 3}}

result3 = client_queries.GetInlineFragment.execute(client, {"e": "JEDI"})
assert result3 == {"hero": {"__typename": "Droid", "id": "d-1", "name": "C-3PO", "primaryFunction": "search"}}

result4 = client_queries.GetCustomScalar.execute(client)
assert result4 == {"today": datetime.datetime.now().date()}

result5 = client_queries.GetUnion.execute(client, {"text": "luke"})
assert result5 == {"search": [{"__typename": "Human", "totalCredits": 3}]}

result5 = client_queries.GetUnion.execute(client, {"text": "R2"})
assert result5 == {"search": [{"__typename": "Droid", "friends": [{"name": "luke"}, {"name": "C-3PO"}]}]}

result5 = client_queries.GetUnion.execute(client, {"text": "dark"})
assert result5 == {"search": [{"__typename": "Starship", "name": "darkstar"}]}

result6 = client_queries.GetRecursive.execute(client, {"episode": "NEWHOPE"})
assert result6 == {
    "hero": {
        "__typename": "Human",
        "name": "luke",
        "friends": [
            {"__typename": "Human", "name": "obi"},
            {"__typename": "Droid", "id": "d-2", "name": "R2-D2"},
        ],
    }
}

result6 = client_queries.GetRecursive.execute(client, {"episode": "JEDI"})
assert result6 == {
    "hero": {
        "__typename": "Droid",
        "name": "C-3PO",
        "friends": [
            {"__typename": "Human", "id": "h-2", "name": "obi", "starships": [{"name": "darkstar"}]},
            {
                "__typename": "Droid",
                "id": "d-2",
                "name": "R2-D2",
                "friends": [{"name": "luke"}, {"name": "C-3PO"}],
            },
        ],
        "primaryFunction": "search",
    }
}

result7 = client_queries.AddStarship.execute(client, {"input": {"name": "HOGE"}})
assert result7 == {"addStarship": {"id": "s-3", "name": "HOGE"}}

schema = client.schema

async_transport = WebsocketsTransport(url="ws://localhost:8000")
client = Client(transport=async_transport, schema=schema)  # fetch_schema_from_transportには対応していない
result8 = [x for x in client_queries.AllHuman.subscribe(client)]
assert result8 == [{"allHuman": {"id": "h-1", "name": "luke"}}, {"allHuman": {"id": "h-2", "name": "obi"}}]


async def async_subscription_test():
    transport = WebsocketsTransport(url="ws://localhost:8000")
    client = Client(transport=transport, schema=schema)
    result8 = [x async for x in client_queries.AllHuman.subscribe_async(client)]
    assert result8 == (
        [{"allHuman": {"id": "h-1", "name": "luke"}}, {"allHuman": {"id": "h-2", "name": "obi"}}]
    )


asyncio.run(async_subscription_test())
