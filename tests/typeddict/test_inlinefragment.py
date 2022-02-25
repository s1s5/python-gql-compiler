import unittest

from ..queries.inlinefragment.query_typeddict import GetInlineFragment
from ..testbase import LocalSchemaTest


class TestRequest(LocalSchemaTest, unittest.IsolatedAsyncioTestCase):
    def test_sync_get(self):
        result_1 = GetInlineFragment.execute(self.client, {"e": "EMPIRE"})
        self.assertEqual(
            result_1,
            {"hero": {"__typename": "Human", "id": "h-2", "name": "obi", "totalCredits": 3}},
        )
        result_2 = GetInlineFragment.execute(self.client, {"e": "JEDI"})
        self.assertEqual(
            result_2,
            {"hero": {"__typename": "Droid", "id": "d-1", "name": "C-3PO", "primaryFunction": "search"}},
        )

    async def test_async_get(self):
        result_1 = await GetInlineFragment.execute_async(self.client, {"e": "EMPIRE"})
        self.assertEqual(
            result_1,
            {"hero": {"__typename": "Human", "id": "h-2", "name": "obi", "totalCredits": 3}},
        )
        result_2 = await GetInlineFragment.execute_async(self.client, {"e": "JEDI"})
        self.assertEqual(
            result_2,
            {"hero": {"__typename": "Droid", "id": "d-1", "name": "C-3PO", "primaryFunction": "search"}},
        )
