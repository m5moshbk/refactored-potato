import unittest

from pydantic import ValidationError

from app.config import Settings


class ProductionSettingsTests(unittest.TestCase):
    def valid_settings(self, **overrides):
        values = {
            "environment": "production",
            "database_url": "postgresql://voice_user:secret@db.example.com/voice",
            "secret_key": "test-only-random-secret-key-with-more-than-32-chars",
            "cors_origins": "https://voice.example.com",
            "debug": False,
            "auto_create_tables": False,
            "access_token_minutes": 30,
            "max_audio_bytes": 15 * 1024 * 1024,
        }
        values.update(overrides)
        return Settings(_env_file=None, **values)

    def test_accepts_exact_https_origin(self):
        settings = self.valid_settings()
        self.assertEqual(settings.allowed_origins, ["https://voice.example.com"])

    def test_rejects_plain_http_origin(self):
        with self.assertRaises(ValidationError):
            self.valid_settings(cors_origins="http://voice.example.com")

    def test_rejects_origin_with_path(self):
        with self.assertRaises(ValidationError):
            self.valid_settings(cors_origins="https://voice.example.com/app")

    def test_rejects_wildcard_origin(self):
        with self.assertRaises(ValidationError):
            self.valid_settings(cors_origins="*")

    def test_rejects_weak_secret(self):
        with self.assertRaises(ValidationError):
            self.valid_settings(secret_key="short")

    def test_rejects_sqlite_in_production(self):
        with self.assertRaises(ValidationError):
            self.valid_settings(database_url="sqlite:///./test.db")


if __name__ == "__main__":
    unittest.main()
