import unittest

from ..queries.mutation.mutation_typeddict import AddStarship
from ..testbase import LocalSchemaTest


class TestRequest(LocalSchemaTest, unittest.IsolatedAsyncioTestCase):
    def test_sync_get(self):
        result = AddStarship.execute(self.client, {"input": {"name": "HOGE"}})
        self.assertEqual(result, {"addStarship": {"id": "s-3", "name": "HOGE"}})

    async def test_async_get(self):
        result = await AddStarship.execute_async(self.client, {"input": {"name": "HOGE"}})
        self.assertEqual(result, {"addStarship": {"id": "s-3", "name": "HOGE"}})
