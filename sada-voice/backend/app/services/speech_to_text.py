"""Speech-to-text capability boundary.

The first release uses the browser's speech-recognition interface where supported.
No server-side provider is called and no uploaded audio is written to disk.
"""


class SpeechToTextService:
    async def transcribe_audio(self, file_bytes: bytes, file_name: str) -> dict:
        raise RuntimeError(
            "Server-side speech recognition is disabled until a reviewed provider "
            "or a self-hosted model is configured."
        )
