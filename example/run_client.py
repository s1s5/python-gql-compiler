import asyncio
import datetime

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

result0 = client_queries.GetScalar.execute(client)
assert result0 == {"hello": "hello world"}


result1 = client_queries.GetObject.execute(client, {"id": "d-1"})
assert result1 == {'droid': {'id': 'd-1', 'name': 'C-3PO', 'appearsIn': ['NEWHOPE'], 'primaryFunction': 'search'}}

result2 = client_queries.GetInterface.execute(client, {"e": "NEWHOPE"})
assert result2 == {'hero': {'id': 'h-1', 'name': 'luke'}}

result3 = client_queries.GetInlineFragment.execute(client, {"e": "EMPIRE"})
assert result3 == {'hero': {'__typename': 'Human', 'id': 'h-2', 'name': 'obi', 'totalCredits': 3}}

result3 = client_queries.GetInlineFragment.execute(client, {"e": "JEDI"})
assert result3 == {'hero': {'__typename': 'Droid', 'id': 'd-1', 'name': 'C-3PO', 'primaryFunction': 'search'}}

result4 = client_queries.GetCustomScalar.execute(client)
assert result4 == {'today': datetime.date(2022, 2, 9)}

result5 = client_queries.GetUnion.execute(client, {"text": "luke"})
assert result5 == {'search': [{'__typename': 'Human', 'totalCredits': 3}]}

result5 = client_queries.GetUnion.execute(client, {"text": "R2"})
assert result5 == {'search': [{'__typename': 'Droid', 'friends': [{'name': 'luke'}, {'name': 'C-3PO'}]}]}

result5 = client_queries.GetUnion.execute(client, {"text": "dark"})
assert result5 == {'search': [{'__typename': 'Starship', 'name': 'darkstar'}]}
