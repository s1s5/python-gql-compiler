from gql import Client
from gql.transport.local_schema import LocalSchemaTransport

from . import graphql_server


class LocalSchemaTest:
    def setUp(self):
        transport = LocalSchemaTransport(schema=graphql_server.schema._schema)
        self.client = Client(
            transport=transport,
            fetch_schema_from_transport=True,
            parse_results=True,
            serialize_variables=True,
        )
