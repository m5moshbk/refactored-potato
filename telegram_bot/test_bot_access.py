import importlib.util
import sys
import uuid
from pathlib import Path


BOT_DIR = Path(__file__).resolve().parent
if str(BOT_DIR) not in sys.path:
    sys.path.insert(0, str(BOT_DIR))


def load_bot(tmp_path, monkeypatch, public_mode=None, admin="", daily_limit=1):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    monkeypatch.setenv("TELEGRAM_ADMIN_CHAT_ID", admin)
    monkeypatch.setenv("NEXUS_MEMORY_DB", str(tmp_path / f"memory-{uuid.uuid4().hex}.sqlite3"))
    monkeypatch.setenv("NEXUS_PUBLIC_DAILY_LIMIT", str(daily_limit))
    if public_mode is None:
        monkeypatch.delenv("NEXUS_PUBLIC_MODE", raising=False)
    else:
        monkeypatch.setenv("NEXUS_PUBLIC_MODE", public_mode)

    name = "nexus_bot_test_" + uuid.uuid4().hex
    spec = importlib.util.spec_from_file_location(name, BOT_DIR / "bot.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def stub_send(monkeypatch, module):
    sent = []

    def fake_send(chat_id, text, keyboard=None, **kwargs):
        sent.append((str(chat_id), text, keyboard))

    monkeypatch.setattr(module, "send", fake_send)
    return sent


def test_public_ai_chat_is_disabled_by_default(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch)
    sent = stub_send(monkeypatch, module)

    assert module.PUBLIC_BOT_MODE is False
    module.handle_message("999", "/services")

    assert len(sent) == 1
    assert "المشرف فقط" in sent[0][1]


def test_admin_can_still_use_the_bot_when_public_mode_is_off(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch, admin="12345")
    sent = stub_send(monkeypatch, module)

    module.handle_message("12345", "/start")

    assert sent
    assert all("المشرف فقط" not in message for _, message, _ in sent)


def test_public_ai_requires_explicit_opt_in(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch, public_mode="1")
    sent = stub_send(monkeypatch, module)
    answers = []
    monkeypatch.setattr(module, "ask_gpt_resilient", lambda text, chat_id=None: answers.append(text) or "synthetic CI answer")
    monkeypatch.setattr(module, "remember_turn", lambda *args: None)
    monkeypatch.setattr(module, "remember_explicit_project_context", lambda *args: None)

    module.handle_message("999", "hello from CI")

    assert answers == ["hello from CI"]
    assert sent[-1][1] == "synthetic CI answer"


def test_public_mode_daily_limit_is_enforced_per_chat(tmp_path, monkeypatch):
    module = load_bot(tmp_path, monkeypatch, public_mode="1", daily_limit=1)
    sent = stub_send(monkeypatch, module)
    calls = []
    monkeypatch.setattr(module, "ask_gpt_resilient", lambda text, chat_id=None: calls.append(text) or "answer")
    monkeypatch.setattr(module, "remember_turn", lambda *args: None)
    monkeypatch.setattr(module, "remember_explicit_project_context", lambda *args: None)

    module.handle_message("999", "first")
    module.handle_message("999", "second")

    assert calls == ["first"]
    assert "حد الاستخدام اليومي" in sent[-1][1]
