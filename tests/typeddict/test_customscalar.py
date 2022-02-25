import datetime
import unittest

from ..queries.customscalar.query_typeddict import GetCustomScalar
from ..testbase import LocalSchemaTest


class TestRequest(LocalSchemaTest, unittest.IsolatedAsyncioTestCase):
    def test_sync_get(self):
        result = GetCustomScalar.execute(self.client)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue(isinstance(result["today"], datetime.date))

    async def test_async_get(self):
        result = await GetCustomScalar.execute_async(self.client)
        self.assertTrue(isinstance(result, dict))
        self.assertTrue(isinstance(result["today"], datetime.date))
