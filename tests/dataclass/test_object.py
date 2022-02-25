import unittest

from ..queries.object.query_dataclass import GetObject
from ..testbase import LocalSchemaTest


class TestRequest(LocalSchemaTest, unittest.IsolatedAsyncioTestCase):
    def test_sync_get(self):
        result = GetObject.execute(self.client, {"id": "d-1"})
        self.assertEqual(
            result,
            GetObject.Response(
                **{
                    "droid": {
                        "id": "d-1",
                        "name": "C-3PO",
                        "appearsIn": ["NEWHOPE"],
                        "primaryFunction": "search",
                    }
                }
            ),
        )

    async def test_async_get(self):
        result = await GetObject.execute_async(self.client, {"id": "d-1"})
        self.assertEqual(
            result,
            GetObject.Response(
                **{
                    "droid": {
                        "id": "d-1",
                        "name": "C-3PO",
                        "appearsIn": ["NEWHOPE"],
                        "primaryFunction": "search",
                    }
                }
            ),
        )
