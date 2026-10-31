import hashlib

class VoicePrintService:
    def create_fingerprint(self, audio_bytes: bytes) -> str:
        return hashlib.sha256(audio_bytes).hexdigest()

    def compare(self, reference_hash: str, candidate_hash: str) -> float:
        if reference_hash == candidate_hash:
            return 1.0
        return 0.0
