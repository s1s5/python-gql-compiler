from gql import Client
from gql.transport.local_schema import LocalSchemaTransport

from . import custom_scalars, graphql_server


class LocalSchemaTest:
    async def asyncSetUp(self):
        transport = LocalSchemaTransport(schema=graphql_server.schema._schema)
        self.client = Client(
            transport=transport,
            fetch_schema_from_transport=True,
            parse_results=True,
            serialize_variables=True,
        )
        async with self.client:
            custom_scalars.register_parsers(self.client.schema)
