"""Regression tests for Nexus Telegram provider and callback recovery."""
import importlib.util
import io
import json
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError


BOT_DIR = Path(__file__).resolve().parent
if str(BOT_DIR) not in sys.path:
    sys.path.insert(0, str(BOT_DIR))


def load_bot(tmp_path, monkeypatch, provider="gemini"):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    monkeypatch.setenv("TELEGRAM_ADMIN_CHAT_ID", "12345")
    monkeypatch.setenv("NEXUS_AI_PROVIDER", provider)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.8-flash")
    monkeypatch.setenv("NEXUS_MEMORY_DB", str(tmp_path / f"memory-{uuid.uuid4().hex}.sqlite3"))
    name = "nexus_bot_regression_" + uuid.uuid4().hex
    spec = importlib.util.spec_from_file_location(name, BOT_DIR / "bot.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_legacy_saved_gemini_model_falls_back_to_supported_default(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch)
    module.init_memory()
    module._set_setting("12345", "gemini_model", "gemini-2.5-flash")

    assert "gemini-2.5-flash" not in [model for model, _ in module.GEMINI_MODELS]
    assert module.get_ai_model("12345", "gemini") == "gemini-3.8-flash"


def test_gemini_overload_retries_without_search_on_alternate_model(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch)
    calls = []

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"output_text": "Recovered response"}).encode("utf-8")

    def fake_urlopen(request, timeout=0):
        payload = json.loads(request.data.decode("utf-8"))
        calls.append(payload)
        if len(calls) == 1:
            raise HTTPError(
                request.full_url, 503, "Service Unavailable", None,
                io.BytesIO(b'{"error":{"message":"temporarily overloaded"}}')
            )
        return FakeResponse()

    monkeypatch.setattr(module, "urlopen", fake_urlopen)
    answer = module.ask_gpt("hello", chat_id=None)

    assert answer.startswith("Recovered response")
    assert len(calls) == 2
    assert calls[1]["model"] == "gemini-3.6-flash"
    assert "tools" not in calls[1]


def test_callback_action_runs_even_if_acknowledgement_is_expired(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch)
    actions = []
    update_calls = {"count": 0}

    def fake_api(method, params=None, timeout=35):
        if method == "getUpdates":
            update_calls["count"] += 1
            if update_calls["count"] == 1:
                return {"result": [{
                    "update_id": 1,
                    "callback_query": {
                        "id": "expired-callback",
                        "data": "diagnostics",
                        "message": {"message_id": 77, "chat": {"id": 12345}}
                    }
                }]}
            raise KeyboardInterrupt()
        if method == "answerCallbackQuery":
            raise HTTPError(
                "https://api.telegram.org/bot<redacted>/answerCallbackQuery",
                400, "Bad Request", None,
                io.BytesIO(b'{"description":"query is too old"}')
            )
        return {}

    monkeypatch.setattr(module, "api", fake_api)
    monkeypatch.setattr(module, "on_callback", lambda *args: actions.append(args))

    try:
        module.polling()
    except KeyboardInterrupt:
        pass

    assert actions == [(12345, 77, "diagnostics")]


def test_gemini_quota_429_does_not_retry_an_alternate_model(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch)
    calls = []

    def fake_urlopen(request, timeout=0):
        calls.append(json.loads(request.data.decode("utf-8")))
        raise HTTPError(
            request.full_url, 429, "Too Many Requests", None,
            io.BytesIO(b'{"error":{"message":"quota exhausted"}}')
        )

    monkeypatch.setattr(module, "urlopen", fake_urlopen)
    answer = module.ask_gpt("hello", chat_id=None)

    assert len(calls) == 1
    assert "429" in answer
    assert "المحاولات الإضافية" in answer


def test_openai_to_gemini_fallback_is_request_scoped(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch, provider="openai")
    module.init_memory()
    module.set_ai_provider("12345", "openai")
    module.GEMINI_API_KEY = "test-key"
    calls = []

    def fake_ask(user_text, chat_id=None, provider_override=None):
        calls.append(provider_override)
        if len(calls) == 1:
            return "تعذر الاتصال بالمحرك المحدد"
        return "Gemini temporary answer"

    monkeypatch.setattr(module, "ask_gpt", fake_ask)
    answer = module.ask_gpt_resilient("hello", chat_id="12345")

    assert calls == [None, "gemini"]
    assert answer.endswith("Gemini temporary answer")
    assert module.get_ai_provider("12345") == "openai"


def test_failed_gemini_never_falls_back_to_openai(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch, provider="gemini")
    module.init_memory()
    module.set_ai_provider("12345", "gemini")
    module.OPENAI_API_KEY = "test-openai-key"
    calls = []

    def fake_ask(user_text, chat_id=None, provider_override=None):
        calls.append(provider_override)
        return "وصل المحرك المحدد إلى حد الحصة (HTTP 429)"

    monkeypatch.setattr(module, "ask_gpt", fake_ask)
    answer = module.ask_gpt_resilient("hello", chat_id="12345")

    assert calls == [None]
    assert "وضع Nexus المجاني الاحتياطي" in answer
    assert module.get_ai_provider("12345") == "gemini"



def test_gemini_quota_429_persists_cooldown(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch)
    calls = []

    def fake_urlopen(request, timeout=0):
        calls.append(request)
        raise HTTPError(
            request.full_url, 429, "Too Many Requests", None,
            io.BytesIO(b'{"error":{"message":"quota exhausted"}}')
        )

    monkeypatch.setattr(module, "urlopen", fake_urlopen)
    answer = module.ask_gpt("hello", chat_id=None)

    assert len(calls) == 1
    assert "429" in answer
    assert module.gemini_quota_cooldown_remaining() > 0


def test_gemini_cooldown_skips_subsequent_provider_request(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch)
    module.init_memory()
    module.mark_gemini_quota_cooldown()
    calls = []

    def fake_ask(*args, **kwargs):
        calls.append((args, kwargs))
        return "Unexpected provider call"

    monkeypatch.setattr(module, "ask_gpt", fake_ask)
    answer = module.ask_gpt_resilient("مرحبا", chat_id="12345")

    assert calls == []
    assert "وضع Nexus المجاني الاحتياطي" in answer
    assert "إيقاف طلبات Gemini مؤقتًا" in answer


def test_expired_gemini_cooldown_allows_provider_retry(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch)
    module.init_memory()
    module._set_monitor_state(
        "gemini_quota_cooldown_until", module.time.time() - 1
    )
    calls = []

    def fake_ask(*args, **kwargs):
        calls.append((args, kwargs))
        return "Provider recovered"

    monkeypatch.setattr(module, "ask_gpt", fake_ask)
    answer = module.ask_gpt_resilient("hello", chat_id="12345")

    assert answer == "Provider recovered"
    assert len(calls) == 1


def test_openai_fallback_does_not_call_gemini_during_cooldown(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch, provider="openai")
    module.init_memory()
    module.set_ai_provider("12345", "openai")
    module.mark_gemini_quota_cooldown()
    calls = []

    def fake_ask(user_text, chat_id=None, provider_override=None):
        calls.append(provider_override)
        return "تعذر الاتصال بالمحرك المحدد"

    monkeypatch.setattr(module, "ask_gpt", fake_ask)
    answer = module.ask_gpt_resilient("hello", chat_id="12345")

    assert calls == [None]
    assert "وضع Nexus المجاني الاحتياطي" in answer
    assert module.get_ai_provider("12345") == "openai"
