"""Regression tests for Nexus Telegram provider and callback reliability."""
import importlib.util
import io
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError


BOT_DIR = Path(__file__).resolve().parent
if str(BOT_DIR) not in sys.path:
    sys.path.insert(0, str(BOT_DIR))


def load_bot(tmp_path, monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    monkeypatch.setenv("TELEGRAM_ADMIN_CHAT_ID", "12345")
    monkeypatch.setenv("NEXUS_MEMORY_DB", str(tmp_path / f"memory-{uuid.uuid4().hex}.sqlite3"))
    name = "nexus_bot_reliability_test_" + uuid.uuid4().hex
    spec = importlib.util.spec_from_file_location(name, BOT_DIR / "bot.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_gemini_catalog_uses_current_interactions_models(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch)
    model_ids = [model for model, _label in module.GEMINI_MODELS]

    assert "gemini-3.8-flash" in model_ids
    assert "gemini-3.7-flash" in model_ids
    assert "gemini-3.1-pro-preview" in model_ids
    assert not any(model.startswith("gemini-2.5-") for model in model_ids)
    assert "gemini-4-argon" not in model_ids


def test_gemini_fallback_selects_one_different_model(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch)

    assert module.gemini_fallback_model("gemini-3.8-flash") == "gemini-3.7-flash"
    assert module.gemini_fallback_model("gemini-2.5-flash") == "gemini-3.8-flash"
    assert module.gemini_fallback_model("gemini-3.1-pro-preview") != "gemini-3.1-pro-preview"


def test_callback_action_runs_when_acknowledgement_fails(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch)
    actions = []

    def fail_acknowledgement(method, params=None, timeout=35):
        assert method == "answerCallbackQuery"
        raise HTTPError(
            "https://api.telegram.org/",
            400,
            "Bad Request",
            {},
            io.BytesIO(b'{"description":"query is too old"}'),
        )

    monkeypatch.setattr(module, "api", fail_acknowledgement)
    monkeypatch.setattr(module, "on_callback", lambda *args: actions.append(args))

    module.process_callback({
        "id": "callback-123",
        "data": "menu",
        "message": {"message_id": 77, "chat": {"id": 12345}},
    })

    assert actions == [(12345, 77, "menu")]


def test_non_admin_callback_is_not_executed(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch)
    actions = []
    monkeypatch.setattr(module, "api", lambda *args, **kwargs: {})
    monkeypatch.setattr(module, "on_callback", lambda *args: actions.append(args))

    module.process_callback({
        "id": "callback-456",
        "data": "menu",
        "message": {"message_id": 88, "chat": {"id": 99999}},
    })

    assert actions == []
