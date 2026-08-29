import copy
import json
import unittest
from pathlib import Path

from tools.validate_remote_sources import REGISTRY_PATH, validate


class RemoteSourceRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_committed_registry_is_valid(self):
        self.assertEqual(validate(self.registry), [])

    def test_rejects_duplicate_source_ids(self):
        data = copy.deepcopy(self.registry)
        data["sources"][1]["id"] = data["sources"][0]["id"]

        self.assertTrue(any("unique" in error for error in validate(data)))

    def test_rejects_automated_source_without_site_scope(self):
        data = copy.deepcopy(self.registry)
        data["sources"][0]["websearch_scope"] = "remoteok.com"

        self.assertTrue(any("site: websearch_scope" in error for error in validate(data)))

    def test_rejects_unknown_focus_profile(self):
        data = copy.deepcopy(self.registry)
        data["sources"][0]["focus"].append("unknown")

        self.assertTrue(any("defined query profiles" in error for error in validate(data)))


if __name__ == "__main__":
    unittest.main()