import asyncio

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

schema = client.schema

async_transport = WebsocketsTransport(url="ws://localhost:8000")
client = Client(transport=async_transport, schema=schema)  # fetch_schema_from_transportには対応していない
result8 = [x for x in client_queries.AllHuman.subscribe(client)]
print(result8)
