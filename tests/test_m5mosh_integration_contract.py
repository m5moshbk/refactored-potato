"""Read-only structural tests for the M5mOsH integration contract.

These tests validate the contract artifact itself. They do not call networks,
providers, databases, hosting APIs, or production services.
"""
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "contracts" / "event-envelope.schema.json"


class IntegrationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_schema_uses_supported_json_schema_draft(self):
        self.assertEqual(
            self.schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )

    def test_envelope_rejects_unknown_top_level_properties(self):
        self.assertIs(self.schema["additionalProperties"], False)
        self.assertEqual(
            set(self.schema["required"]),
            {"event_id", "event_type", "occurred_at", "source", "classification", "payload"},
        )

    def test_source_and_payload_are_closed_objects(self):
        properties = self.schema["properties"]
        self.assertIs(properties["source"]["additionalProperties"], False)
        self.assertIs(properties["payload"]["additionalProperties"], False)

    def test_payload_is_metadata_only(self):
        payload_fields = set(self.schema["properties"]["payload"]["properties"])
        self.assertEqual(
            payload_fields,
            {"status", "counts", "fingerprints", "duration_ms", "result_code"},
        )
        forbidden = {
            "path", "file_path", "filename", "raw_content",
            "secret", "token", "password", "email", "phone",
        }
        self.assertTrue(payload_fields.isdisjoint(forbidden))

    def test_evidence_classification_keeps_provenance_states_distinct(self):
        self.assertEqual(
            set(self.schema["properties"]["classification"]["enum"]),
            {"discovered", "observed", "verified", "historical", "planned"},
        )

    def test_fingerprints_are_sha256_only(self):
        fingerprint_schema = self.schema["properties"]["payload"]["properties"]["fingerprints"]
        self.assertEqual(
            fingerprint_schema["items"]["pattern"],
            "^sha256:[a-f0-9]{64}$",
        )

    def test_evidence_items_reject_unknown_fields(self):
        evidence = self.schema["properties"]["evidence"]
        self.assertIs(evidence["items"]["additionalProperties"], False)
        self.assertEqual(
            set(evidence["items"]["required"]),
            {"evidence_id", "kind", "captured_at"},
        )


if __name__ == "__main__":
    unittest.main()
