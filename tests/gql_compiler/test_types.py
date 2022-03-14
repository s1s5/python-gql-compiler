import unittest

from gql_compiler import types


class Test(unittest.TestCase):
    def test_type(self):
        a: types.Config = {  # noqa
            "output_path": "",
            "scalar_map": {},
            "query_ext": "",
            "output_type": "dataclass",
        }
