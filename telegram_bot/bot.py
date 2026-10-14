#!/usr/bin/env python3
"""M5mOsH Nexus Telegram catalog with interactive inline navigation; read-only."""
import json, os, time, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ROOT, "catalog.json"), encoding="utf-8") as f:
    CATALOG = json.load(f)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
ADMIN = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "").strip()
PORT = int(os.getenv("PORT", "10000"))
OFFSET = 0
PAGE_SIZE = 6
API = "https://api.telegram.org/bot"


def api(method, params=None, timeout=35):
    if not TOKEN:
        return {}
    params = dict(params or {})
    for key, value in list(params.items()):
        if isinstance(value, (dict, list)):
            params[key] = json.dumps(value, ensure_ascii=False)
    req = Request(API + TOKEN + "/" + method, data=urlencode(params).encode(),
                  headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urlopen(req, timeout=timeout) as response:
        result = json.loads(response.read().decode("utf-8"))
    if not result.get("ok"):
        raise RuntimeError("Telegram API rejected " + method)
    return result


def button(label, data):
    return {"text": label, "callback_data": data}


def menu():
    return [
        [button("📦 المستودعات", "repos:0"), button("🧩 الأقسام", "categories")],
        [button("☁️ خدمات Render", "services:0"), button("🚀 المشاريع", "projects")],
        [button("🔎 البحث", "search_help"), button("ℹ️ حول Nexus", "about")],
    ]


def send(chat_id, text, keyboard=None):
    params = {"chat_id": chat_id, "text": text[:3900], "disable_web_page_preview": "true"}
    if keyboard:
        params["reply_markup"] = {"inline_keyboard": keyboard}
    api("sendMessage", params, 20)


def edit(chat_id, message_id, text, keyboard=None):
    params = {"chat_id": chat_id, "message_id": message_id, "text": text[:3900],
              "disable_web_page_preview": "true"}
    if keyboard:
        params["reply_markup"] = {"inline_keyboard": keyboard}
    try:
        api("editMessageText", params, 20)
    except Exception as exc:
        if "not modified" not in str(exc).lower():
            raise


def repos():
    return CATALOG.get("repositories", [])


def services():
    return CATALOG.get("services", [])


def repo_card(r):
    return ("📦 " + r.get("name", "مستودع") +
            "\nالتصنيف: " + r.get("category", "بحاجة للتصنيف") +
            "\nالغرض: " + r.get("purpose", "غير موثق") +
            "\nالاستخدام: " + r.get("usage", "راجع الملفات") +
            "\nالحالة: " + r.get("status", "غير مفحوص") +
            "\nالفرع: " + r.get("default_branch", "غير معروف") +
            "\nالرابط: " + r.get("url", ""))


def service_card(s):
    return ("☁️ " + s.get("name", "خدمة") +
            "\nالنوع: " + s.get("type", "غير معروف") +
            "\nالغرض: " + s.get("purpose", "غير موثق") +
            "\nالحالة المسجلة: " + s.get("status", "غير مفحوص") +
            "\nالمستودع: " + s.get("repo", "غير معروف") +
            "\nالرابط: " + s.get("url", "") +
            "\nلوحة Render: " + s.get("dashboard", ""))


def page_keyboard(kind, page, total):
    items = repos() if kind == "repo" else services()
    rows = []
    start, end = page * PAGE_SIZE, min((page + 1) * PAGE_SIZE, total)
    for idx in range(start, end):
        name = items[idx].get("name", "بدون اسم")
        rows.append([button(name[:48], kind + ":" + str(idx))])
    nav = []
    if page > 0:
        nav.append(button("⬅️ السابق", kind + "s:" + str(page - 1)))
    nav.append(button(f"{page + 1}/{max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)}", "noop"))
    if end < total:
        nav.append(button("التالي ➡️", kind + "s:" + str(page + 1)))
    rows.append(nav)
    rows.append([button("🏠 القائمة الرئيسية", "menu")])
    return rows


def category_summary():
    counts = {}
    for r in repos():
        category = r.get("category", "بحاجة للتصنيف")
        counts[category] = counts.get(category, 0) + 1
    return "🧩 أقسام الكتالوج\n\n" + "\n".join(
        "• " + k + ": " + str(v) for k, v in sorted(counts.items()))


def project_summary():
    names = {"SADA", "Sawa-Play-Monitor", "m5moshbk-Elite-Console-X",
             "super-duper-octo-adventure", "Tamara-Business-Site",
             "refactored-potato", "bizweb-platform", "Crispy-Seeka"}
    chosen = [r for r in repos() if r.get("name") in names]
    parts = ["🚀 المشاريع الأساسية — الوصف لا يعني تحققًا وظيفيًا"]
    parts.extend(repo_card(r) for r in chosen[:5])
    local = CATALOG.get("workspace_projects", [])
    if local:
        parts.append("📱 مشاريع مساحة العمل")
        parts.extend("• " + p.get("name", "مشروع") + " — " + p.get("status", "غير مفحوص") for p in local)
    return "\n\n".join(parts)


def on_callback(chat_id, message_id, data):
    if data == "menu":
        edit(chat_id, message_id, "🧭 M5mOsH Nexus\nمركز موحّد لتصفح المشاريع والخدمات — وضع القراءة فقط.", menu())
    elif data == "categories":
        edit(chat_id, message_id, category_summary(), [
            [button("📦 المستودعات", "repos:0")], [button("🏠 القائمة الرئيسية", "menu")]])
    elif data.startswith("repos:"):
        page = max(0, int(data.split(":", 1)[1]))
        edit(chat_id, message_id, f"📦 مستودعات GitHub المسجلة: {len(repos())}\nاختر مستودعًا لعرض التفاصيل.",
             page_keyboard("repo", page, len(repos())))
    elif data.startswith("repo:"):
        idx = int(data.split(":", 1)[1])
        if 0 <= idx < len(repos()):
            edit(chat_id, message_id, repo_card(repos()[idx]), [
                [button("⬅️ العودة للمستودعات", "repos:" + str(idx // PAGE_SIZE))],
                [button("🏠 القائمة الرئيسية", "menu")]])
    elif data.startswith("services:"):
        page = max(0, int(data.split(":", 1)[1]))
        edit(chat_id, message_id, f"☁️ خدمات Render المسجلة: {len(services())}\nبيانات الكتالوج ليست فحصًا حيًا.",
             page_keyboard("service", page, len(services())))
    elif data.startswith("service:"):
        idx = int(data.split(":", 1)[1])
        if 0 <= idx < len(services()):
            edit(chat_id, message_id, service_card(services()[idx]), [
                [button("⬅️ العودة للخدمات", "services:" + str(idx // PAGE_SIZE))],
                [button("🏠 القائمة الرئيسية", "menu")]])
    elif data == "projects":
        edit(chat_id, message_id, project_summary(), [[button("🏠 القائمة الرئيسية", "menu")]])
    elif data == "search_help":
        edit(chat_id, message_id, "🔎 البحث\nأرسل: /search كلمة\nمثال: /search SADA\nيبحث في أسماء المستودعات وأغراضها وتصنيفاتها وخدمات Render.",
             [[button("🏠 القائمة الرئيسية", "menu")]])
    elif data == "about":
        edit(chat_id, message_id, "M5mOsH Nexus — فهرس للمشاريع والمستودعات والخدمات.\nالبوت للقراءة فقط ولا ينشر أو يحذف أو يغيّر الإعدادات. بيانات الخدمات في الكتالوج قد لا تكون محدثة لحظيًا.",
             [[button("🏠 القائمة الرئيسية", "menu")]])


def handle_message(chat_id, text):
    if ADMIN and str(chat_id) != ADMIN:
        send(chat_id, "هذا البوت مقيّد بالمحادثة الإدارية المحددة.")
        return
    cmd, _, arg = (text or "").strip().partition(" ")
    cmd = cmd.split("@")[0].lower()
    if cmd in ("/start", "/help", "/مساعدة", "/menu"):
        send(chat_id, "🧭 أهلًا بك في M5mOsH Nexus\nاختر من القائمة التفاعلية بدل كتابة الأوامر يدويًا.\n\nاختصارات: /repos /services /projects /search كلمة", menu())
    elif cmd in ("/repos", "/المستودعات"):
        send(chat_id, f"📦 المستودعات المسجلة: {len(repos())}", page_keyboard("repo", 0, len(repos())))
    elif cmd in ("/services", "/خدمات"):
        send(chat_id, f"☁️ خدمات Render المسجلة: {len(services())}\nهذه بيانات الكتالوج وليست فحصًا حيًا.", page_keyboard("service", 0, len(services())))
    elif cmd in ("/projects", "/المشاريع"):
        send(chat_id, project_summary(), [[button("🏠 القائمة الرئيسية", "menu")]])
    elif cmd in ("/search", "/بحث"):
        q = arg.strip().casefold()
        if not q:
            send(chat_id, "اكتب كلمة بعد الأمر، مثال: /search SADA")
            return
        found = []
        for kind, items in (("repo", repos()), ("service", services())):
            for idx, item in enumerate(items):
                fields = [item.get("name", ""), item.get("purpose", ""), item.get("category", ""),
                          item.get("full_name", ""), item.get("url", ""), item.get("repo", "")]
                if q in " ".join(fields).casefold():
                    found.append((kind, idx, item.get("name", "عنصر")))
        if not found:
            send(chat_id, "لم أجد نتائج لهذه الكلمة.")
        else:
            rows = [[button(("📦 " if k == "repo" else "☁️ ") + name[:48], k + ":" + str(idx))
                     for k, idx, name in found[:18]]
            rows.append([button("🏠 القائمة الرئيسية", "menu")])
            send(chat_id, f"🔎 النتائج: {len(found)} — أعرض أول {min(18, len(found))}", rows)
    else:
        send(chat_id, "استخدم /start لفتح القائمة التفاعلية، أو /search كلمة للبحث.")


def polling():
    global OFFSET
    while True:
        try:
            result = api("getUpdates", {"timeout": 25, "offset": OFFSET,
                                        "allowed_updates": ["message", "callback_query"]}, 35)
            for item in result.get("result", []):
                OFFSET = max(OFFSET, int(item.get("update_id", 0)) + 1)
                callback = item.get("callback_query")
                if callback:
                    try:
                        api("answerCallbackQuery", {"callback_query_id": callback["id"]}, 10)
                        msg = callback.get("message") or {}
                        chat = msg.get("chat") or {}
                        if chat.get("id") is not None and callback.get("data"):
                            if not ADMIN or str(chat["id"]) == ADMIN:
                                on_callback(chat["id"], msg.get("message_id"), callback["data"])
                    except Exception as exc:
                        print("Telegram callback error:", type(exc).__name__, flush=True)
                    continue
                msg = item.get("message") or item.get("edited_message")
                if msg and msg.get("chat") and msg.get("text"):
                    handle_message(msg["chat"]["id"], msg["text"])
        except Exception as exc:
            print("Telegram polling error:", type(exc).__name__, flush=True)
            time.sleep(5)


class Handler(BaseHTTPRequestHandler):
    def _respond(self, body_enabled):
        if self.path not in ("/", "/health", "/healthz"):
            self.send_response(404)
            self.end_headers()
            return
        body = json.dumps({"ok": True, "service": "m5mosh-nexus-telegram-catalog",
                           "bot_configured": bool(TOKEN), "repositories": len(repos()),
                           "services": len(services()), "interface": "inline-menu-v1"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body_enabled:
            self.wfile.write(body)

    def do_HEAD(self):
        self._respond(False)

    def do_GET(self):
        self._respond(True)

    def log_message(self, fmt, *args):
        print("HTTP:", fmt % args, flush=True)


def main():
    if TOKEN:
        threading.Thread(target=polling, daemon=True).start()
        print("Telegram polling started; inline menu enabled.", flush=True)
    else:
        print("TELEGRAM_BOT_TOKEN missing; health only until configured.", flush=True)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
