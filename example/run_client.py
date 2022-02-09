import asyncio

from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport

import client_queries
import custom_scalars


transport = AIOHTTPTransport(url="http://localhost:8000")
client = Client(transport=transport, fetch_schema_from_transport=True, parse_results=True)


async def register_parsers():
    async with client:  # force fetch schema
        custom_scalars.register_parsers(client.schema)


asyncio.run(register_parsers())

result = client_queries.GetScalar.execute(client)
assert result == {'hello': 'hello world'}

