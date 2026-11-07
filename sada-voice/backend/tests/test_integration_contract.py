import asyncio
import unittest

from app.routes.health import health


class VoiceNexusIntegrationContractTests(unittest.TestCase):
    def test_health_route_is_liveness_only(self):
        result = asyncio.run(health())

        self.assertEqual(result, {
            "status": "ok",
            "service": "sada-voice",
        })


if __name__ == "__main__":
    unittest.main()
