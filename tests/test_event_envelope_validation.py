"""Behavioral validation of the shared M5mOsH event-envelope schema."""
import copy
import json
import re
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "contracts" / "event-envelope.schema.json").read_text(encoding="utf-8"))
DOCUMENT = (ROOT / "docs" / "INTEGRATION_CONTRACT.md").read_text(encoding="utf-8")


class EventEnvelopeSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        match = re.search(r"```json\s*(\{.*?\})\s*```", DOCUMENT, re.DOTALL)
        if not match:
            raise AssertionError("No fenced JSON event example found in integration contract")
        cls.example = json.loads(match.group(1))
        Draft202012Validator.check_schema(SCHEMA)
        cls.validator = Draft202012Validator(SCHEMA, format_checker=FormatChecker())

    def assert_rejected(self, event):
        self.assertTrue(
            list(self.validator.iter_errors(event)),
            "Expected the event to violate the canonical schema",
        )

    def test_documented_example_passes_real_json_schema_validation(self):
        self.validator.validate(self.example)

    def test_malformed_timestamp_is_rejected(self):
        event = copy.deepcopy(self.example)
        event["occurred_at"] = "not-a-date"
        self.assert_rejected(event)

    def test_unknown_contract_version_field_is_rejected(self):
        event = copy.deepcopy(self.example)
        event["schema_version"] = "99.0.0"
        self.assert_rejected(event)

    def test_sensitive_or_unknown_payload_fields_are_rejected(self):
        event = copy.deepcopy(self.example)
        event["payload"]["raw_content"] = "must-not-cross-service-boundary"
        self.assert_rejected(event)

    def test_oversized_counts_map_is_rejected(self):
        event = copy.deepcopy(self.example)
        event["payload"]["counts"] = {f"metric_{index}": index for index in range(41)}
        self.assert_rejected(event)

    def test_oversized_evidence_list_is_rejected(self):
        event = copy.deepcopy(self.example)
        item = {
            "evidence_id": "ev-test-0001",
            "kind": "test",
            "captured_at": "2026-11-07T16:00:00Z",
        }
        event["evidence"] = [dict(item, evidence_id=f"ev-test-{index:04d}") for index in range(51)]
        self.assert_rejected(event)

    def test_invalid_fingerprint_is_rejected(self):
        event = copy.deepcopy(self.example)
        event["payload"]["fingerprints"] = ["sha256:not-a-real-fingerprint"]
        self.assert_rejected(event)


if __name__ == "__main__":
    unittest.main()
