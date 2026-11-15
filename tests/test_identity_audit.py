import csv
import json
import unittest

from gamelens.identity_audit import CLIP, audit


class IdentityAuditTests(unittest.TestCase):
    def test_featured_audit_reproduces_published_counts(self):
        with (CLIP / "identity-labels.csv").open(newline="") as labels, (CLIP / "tracks.csv").open(newline="") as tracks:
            actual = audit(csv.DictReader(labels), csv.DictReader(tracks))
        expected = json.loads((CLIP / "identity-audit.json").read_text())
        self.assertEqual(actual, expected)
        self.assertEqual(actual["players"]["White 2"]["across_ambiguity"], 1)
        self.assertTrue(any(item.get("id_changed") and item["frame"] == 34 for item in actual["observations"]))
