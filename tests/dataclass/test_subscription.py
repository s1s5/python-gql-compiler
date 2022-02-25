import unittest

from ..queries.subscription.subscription_dataclass import AllHumanSubsc
from ..testbase import LocalSchemaTest


class TestRequest(LocalSchemaTest, unittest.IsolatedAsyncioTestCase):
    def test_sync_get(self):
        result = [x for x in AllHumanSubsc.subscribe(self.client)]
        self.assertEqual(
            result,
            [
                AllHumanSubsc.Response(**{"allHuman": {"id": "h-1", "name": "luke"}}),
                AllHumanSubsc.Response(**{"allHuman": {"id": "h-2", "name": "obi"}}),
            ],
        )

    async def test_async_get(self):
        result = [x async for x in AllHumanSubsc.subscribe_async(self.client)]
        self.assertEqual(
            result,
            [
                AllHumanSubsc.Response(**{"allHuman": {"id": "h-1", "name": "luke"}}),
                AllHumanSubsc.Response(**{"allHuman": {"id": "h-2", "name": "obi"}}),
            ],
        )
