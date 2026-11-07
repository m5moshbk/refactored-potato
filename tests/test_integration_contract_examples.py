"""Validate the repository's documented event example against the shared schema.

Uses only the Python standard library; no network, provider, database, or host calls.
"""
import json
import re
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "contracts" / "event-envelope.schema.json").read_text(encoding="utf-8"))
DOCUMENT = (ROOT / "docs" / "INTEGRATION_CONTRACT.md").read_text(encoding="utf-8")


class IntegrationContractExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        match = re.search(r"```json\s*(\{.*?\})\s*```", DOCUMENT, re.DOTALL)
        if not match:
            raise AssertionError("No fenced JSON event example found in docs/INTEGRATION_CONTRACT.md")
        cls.example = json.loads(match.group(1))

    def test_example_contains_all_required_envelope_fields(self):
        self.assertTrue(set(SCHEMA["required"]).issubset(self.example))
        self.assertTrue(set(self.example).issubset(SCHEMA["properties"]))

    def test_event_type_matches_schema_pattern(self):
        pattern = SCHEMA["properties"]["event_type"]["pattern"]
        self.assertRegex(self.example["event_type"], pattern)

    def test_timestamp_is_parseable_utc_iso8601(self):
        value = self.example["occurred_at"]
        self.assertTrue(value.endswith("Z"))
        datetime.fromisoformat(value.replace("Z", "+00:00"))

    def test_source_uses_only_declared_fields(self):
        source_schema = SCHEMA["properties"]["source"]
        self.assertTrue(set(source_schema["required"]).issubset(self.example["source"]))
        self.assertTrue(set(self.example["source"]).issubset(source_schema["properties"]))

    def test_classification_is_allowed(self):
        self.assertIn(
            self.example["classification"],
            SCHEMA["properties"]["classification"]["enum"],
        )

    def test_payload_uses_only_declared_metadata_fields(self):
        payload_schema = SCHEMA["properties"]["payload"]
        self.assertTrue(set(self.example["payload"]).issubset(payload_schema["properties"]))
        self.assertTrue(
            set(self.example["payload"]).isdisjoint(
                {"path", "file_path", "filename", "raw_content", "token", "password"}
            )
        )

    def test_evidence_items_use_only_declared_fields(self):
        if "evidence" not in self.example:
            return
        evidence_schema = SCHEMA["properties"]["evidence"]["items"]
        for item in self.example["evidence"]:
            self.assertTrue(set(evidence_schema["required"]).issubset(item))
            self.assertTrue(set(item).issubset(evidence_schema["properties"]))


if __name__ == "__main__":
    unittest.main()
