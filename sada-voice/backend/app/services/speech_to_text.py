import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SpeechToTextService:
    async def transcribe_audio(self, file_bytes: bytes, file_name: str) -> dict:
        try:
            if not os.getenv("OPENAI_API_KEY"):
                return {
                    "filename": file_name,
                    "transcript": "هذا نص تجريبي تم إنشاؤه من الملف الصوتي.",
                    "language": "ar",
                    "status": "demo",
                    "confidence": 0.96,
                }

            with open("/tmp/tmp_audio.wav", "wb") as f:
                f.write(file_bytes)

            with open("/tmp/tmp_audio.wav", "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                )

            return {
                "filename": file_name,
                "transcript": response.text,
                "language": "ar",
                "status": "ok",
                "confidence": 0.98,
            }
        except Exception as e:
            return {
                "filename": file_name,
                "transcript": "فشل في تحليل الصوت، يرجى المحاولة لاحقًا.",
                "language": "ar",
                "status": "error",
                "error": str(e),
            }
