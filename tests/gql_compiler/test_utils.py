import unittest

from gql_compiler import utils


class Test(unittest.TestCase):
    def test_camel_case_to_snake(self):
        self.assertEqual(utils.camel_case_to_snake("TestCase"), "test_case")
