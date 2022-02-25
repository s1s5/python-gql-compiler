import unittest

from ..queries.recursive.query_typeddict import GetRecursive
from ..testbase import LocalSchemaTest


class TestRequest(LocalSchemaTest, unittest.IsolatedAsyncioTestCase):
    def test_sync_get(self):
        result_1 = GetRecursive.execute(self.client, {"episode": "NEWHOPE"})
        self.assertEqual(
            result_1,
            {
                "hero": {
                    "__typename": "Human",
                    "name": "luke",
                    "friends": [
                        {"__typename": "Human", "name": "obi"},
                        {"__typename": "Droid", "id": "d-2", "name": "R2-D2"},
                    ],
                }
            },
        )
        result_2 = GetRecursive.execute(self.client, {"episode": "JEDI"})
        self.assertEqual(
            result_2,
            {
                "hero": {
                    "__typename": "Droid",
                    "name": "C-3PO",
                    "friends": [
                        {
                            "__typename": "Human",
                            "id": "h-2",
                            "name": "obi",
                            "starships": [{"name": "darkstar"}],
                        },
                        {
                            "__typename": "Droid",
                            "id": "d-2",
                            "name": "R2-D2",
                            "friends": [{"name": "luke"}, {"name": "C-3PO"}],
                        },
                    ],
                    "primaryFunction": "search",
                }
            },
        )

    async def test_async_get(self):
        result_1 = await GetRecursive.execute_async(self.client, {"episode": "NEWHOPE"})
        self.assertEqual(
            result_1,
            {
                "hero": {
                    "__typename": "Human",
                    "name": "luke",
                    "friends": [
                        {"__typename": "Human", "name": "obi"},
                        {"__typename": "Droid", "id": "d-2", "name": "R2-D2"},
                    ],
                }
            },
        )
        result_2 = await GetRecursive.execute_async(self.client, {"episode": "JEDI"})
        self.assertEqual(
            result_2,
            {
                "hero": {
                    "__typename": "Droid",
                    "name": "C-3PO",
                    "friends": [
                        {
                            "__typename": "Human",
                            "id": "h-2",
                            "name": "obi",
                            "starships": [{"name": "darkstar"}],
                        },
                        {
                            "__typename": "Droid",
                            "id": "d-2",
                            "name": "R2-D2",
                            "friends": [{"name": "luke"}, {"name": "C-3PO"}],
                        },
                    ],
                    "primaryFunction": "search",
                }
            },
        )
