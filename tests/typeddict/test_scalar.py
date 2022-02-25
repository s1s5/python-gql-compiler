import unittest

from ..queries.scalar.query_typeddict import GetScalar
from ..testbase import LocalSchemaTest


class TestRequest(LocalSchemaTest, unittest.IsolatedAsyncioTestCase):
    def test_sync_get(self):
        result = GetScalar.execute(self.client)
        self.assertEqual(result, {"hello": "hello world"})

    async def test_async_get(self):
        result = await GetScalar.execute_async(self.client)
        self.assertEqual(result, {"hello": "hello world"})
