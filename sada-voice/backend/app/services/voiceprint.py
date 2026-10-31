"""Voice identity integration boundary.

A cryptographic hash of an audio file is not a speaker embedding and must never
be treated as proof of speaker identity. Biometric enrollment and verification
remain deliberately unavailable until a consent-based model and anti-spoofing
pipeline have been evaluated.
"""


class VoicePrintService:
    def create_fingerprint(self, audio_bytes: bytes) -> str:
        raise NotImplementedError(
            "Voice biometrics are disabled; raw-audio hashes are not biometrics."
        )

    def compare(self, reference_embedding: str, candidate_embedding: str) -> float:
        raise NotImplementedError(
            "Voice biometrics are disabled until a validated speaker model is integrated."
        )
