import unittest

from ..queries.union.query_dataclass import GetUnion
from ..testbase import LocalSchemaTest


class TestRequest(LocalSchemaTest, unittest.IsolatedAsyncioTestCase):
    def test_sync_get(self):
        result_1 = GetUnion.execute(self.client, {"text": "luke"})
        self.assertEqual(
            result_1, GetUnion.Response(**{"search": [{"__typename": "Human", "totalCredits": 3}]})
        )
        result_1 = GetUnion.execute(self.client, {"text": "R2"})
        self.assertEqual(
            result_1,
            GetUnion.Response(
                **{"search": [{"__typename": "Droid", "friends": [{"name": "luke"}, {"name": "C-3PO"}]}]}
            ),
        )

    async def test_async_get(self):
        result_1 = await GetUnion.execute_async(self.client, {"text": "luke"})
        self.assertEqual(
            result_1, GetUnion.Response(**{"search": [{"__typename": "Human", "totalCredits": 3}]})
        )
        result_1 = await GetUnion.execute_async(self.client, {"text": "R2"})
        self.assertEqual(
            result_1,
            GetUnion.Response(
                **{"search": [{"__typename": "Droid", "friends": [{"name": "luke"}, {"name": "C-3PO"}]}]}
            ),
        )
