import codecs
import tempfile
import unittest

import yaml

import main


class Test(unittest.TestCase):
    def test_cli(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = tempfile.NamedTemporaryFile()

            yaml.safe_dump(
                {
                    "output_path": tmpdir + "/{basename_without_ext}.py",
                },
                codecs.getwriter("utf-8")(config_file),
            )
            config_file.flush()
            main._entry_point(
                [
                    "-s",
                    "./tests/schema.graphql",
                    "-q",
                    "./tests/queries/",
                    "-c",
                    config_file.name,
                ]
            )
