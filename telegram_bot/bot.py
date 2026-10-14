#!/usr/bin/env python3
"""Read-only Telegram catalog for M5mOsH Nexus."""
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

def api(method, params=None, timeout=35):
    if not TOKEN:
        return {}
    url = "https://api.telegram.org/bot" + TOKEN + "/" + method
    req = Request(url, data=urlencode(params or {}).encode(), headers={"Content-Type":"application/x-www-form-urlencoded"})
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))

def send(chat_id, text):
    for start in range(0, len(text), 3900):
        api("sendMessage", {"chat_id":chat_id,"text":text[start:start+3900],"disable_web_page_preview":"true"}, 20)

def repos():
    return CATALOG.get("repositories", [])

def services():
    return CATALOG.get("services", [])

def find_repo(term):
    term = term.strip().lower().replace("https://github.com/","").strip("/")
    return next((r for r in repos() if term in r["name"].lower() or term in r["full_name"].lower()), None)

def card(r):
    return ("📦 " + r["name"] + "\nالقسم: " + r.get("category","بحاجة للتصنيف") +
    "\nالغرض: " + r.get("purpose","غير موثق") + "\nالاستخدام: " + r.get("usage","راجع الملفات") +
    "\nالأقسام/المكونات: " + "، ".join(r.get("sections",[])) +
    "\nالفرع الافتراضي: " + r.get("default_branch","غير معروف") +
    "\nالحالة: " + r.get("status","غير مفحوص") + "\nالرابط: " + r["url"])

def handle(chat_id, text):
    if ADMIN and str(chat_id) != ADMIN:
        send(chat_id, "هذا البوت مقيّد بالمحادثة الإدارية المحددة."); return
    cmd, _, arg = (text or "").strip().partition(" ")
    cmd = cmd.split("@")[0].lower()
    if cmd in ("/start","/help","/مساعدة"):
        send(chat_id, "M5mOsH Nexus — فهرس موحّد للقراءة فقط\n\n/start /help\n/sections — الأقسام\n/repos — مستودعات GitHub\n/stores — المتاجر\n/tools — الأدوات\n/unclassified — بحاجة للتصنيف\n/services — خدمات Render\n/service اسم — تفاصيل خدمة\n/projects — المشاريع الأساسية والمحلية\n/repo اسم — تفاصيل مستودع\n/search كلمة — بحث في المستودعات والخدمات\n\nلا ينفذ البوت حذفًا أو نشرًا أو تغييرات.")
    elif cmd in ("/sections","/أقسام"):
        counts = {}
        for r in repos():
            k = r.get("category","بحاجة للتصنيف"); counts[k] = counts.get(k,0)+1
        send(chat_id, "أقسام Nexus:\n" + "\n".join("• "+k+": "+str(v) for k,v in sorted(counts.items())))
    elif cmd in ("/repos","/المستودعات"):
        send(chat_id, "المستودعات ("+str(len(repos()))+"):\n" + "\n".join("• "+r["name"]+" — "+r["category"]+"\n"+r["url"] for r in repos()))
    elif cmd in ("/stores","/متاجر"):
        rs = [r for r in repos() if r.get("category")=="متاجر"]
        send(chat_id, "قسم المتاجر:\n" + "\n\n".join(card(r) for r in rs))
    elif cmd in ("/tools","/أدوات"):
        rs = [r for r in repos() if r.get("category")=="أدوات"]
        send(chat_id, "قسم الأدوات:\n" + "\n\n".join(card(r) for r in rs))
    elif cmd in ("/unclassified","/غير_مصنف"):
        rs = [r for r in repos() if r.get("category")=="بحاجة للتصنيف"]
        send(chat_id, "تحتاج فحصًا:\n" + "\n".join("• "+r["name"]+" — "+r["url"] for r in rs))
    elif cmd in ("/services","/خدمات"):
        send(chat_id, "خدمات Render ("+str(len(services()))+"):\n" + "\n\n".join("• "+s["name"]+" — "+s["type"]+"\nالحالة: "+s["status"]+"\n"+s["url"] for s in services()))
    elif cmd in ("/service","/خدمة"):
        q = arg.strip().lower()
        s = next((x for x in services() if q and (q in x["name"].lower() or q in x.get("url","").lower())), None)
        send(chat_id, ("خدمة: "+s["name"]+"\nالنوع: "+s["type"]+"\nالغرض: "+s["purpose"]+"\nالحالة: "+s["status"]+"\nالمستودع: "+s["repo"]+"\nالفرع: "+s["branch"]+"\nالتشغيل: "+s["runtime"]+"\nالرابط: "+s["url"]+"\nلوحة Render: "+s["dashboard"]) if s else "لم أجد خدمة بهذا الاسم. استخدم /services.")
    elif cmd in ("/projects","/المشاريع"):
        names = ["SADA","Sawa-Play-Monitor","m5moshbk-Elite-Console-X","super-duper-octo-adventure","Tamara-Business-Site","refactored-potato","bizweb-platform","Crispy-Seeka"]
        rs = [r for n in names for r in repos() if r["name"].lower()==n.lower()]
        local = CATALOG.get("workspace_projects", [])
        local_text = "\n\n".join("• "+p["name"]+" — "+p["category"]+"\nالغرض: "+p["purpose"]+"\nالحالة: "+p["status"] for p in local)
        repo_text = "\n\n".join(card(r) for r in rs) if rs else "لا توجد مستودعات أساسية مطابقة في الكتالوج."
        send(chat_id, "المشاريع الأساسية:\n" + repo_text + "\n\nمشاريع محلية/غير مرتبطة بمستودع:\n" + local_text + "\n\nخدمات Render: استخدم /services")
    elif cmd in ("/repo","/مستودع"):
        r = find_repo(arg)
        send(chat_id, card(r) if r else "لم أجد المستودع. استخدم /repos أو /search كلمة.")
    elif cmd in ("/search","/بحث"):
        q = arg.strip().lower()
        rs = [r for r in repos() if q and (q in r["name"].lower() or q in r["purpose"].lower() or q in r["category"].lower())]
        ss = [s for s in services() if q and (q in s["name"].lower() or q in s["purpose"].lower() or q in s["url"].lower())]
        parts = [card(r) for r in rs[:5]] + [("خدمة: "+s["name"]+" — "+s["status"]+"\n"+s["url"]) for s in ss[:5]]
        send(chat_id, "نتائج البحث:\n" + "\n\n".join(parts) if parts else "لا توجد نتائج.")
    else:
        send(chat_id, "أمر غير معروف؛ استخدم /help.")

def polling():
    global OFFSET
    while True:
        try:
            result = api("getUpdates", {"timeout":25,"offset":OFFSET}, 35)
            for item in result.get("result",[]):
                OFFSET = max(OFFSET, int(item.get("update_id",0))+1)
                msg = item.get("message") or item.get("edited_message")
                if msg and msg.get("chat") and msg.get("text"):
                    handle(msg["chat"]["id"], msg["text"])
        except Exception as exc:
            print("Telegram polling error:", type(exc).__name__, flush=True)
            time.sleep(5)

class Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        if self.path not in ("/","/health","/healthz"):
            self.send_response(404); self.end_headers(); return
        body = json.dumps({"ok":True,"service":"m5mosh-nexus-telegram-catalog","bot_configured":bool(TOKEN),"repositories":len(repos())}).encode()
        self.send_response(200); self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body))); self.end_headers()
    def do_GET(self):
        if self.path not in ("/","/health","/healthz"):
            self.send_response(404); self.end_headers(); return
        body = json.dumps({"ok":True,"service":"m5mosh-nexus-telegram-catalog","bot_configured":bool(TOKEN),"repositories":len(repos())}).encode()
        self.send_response(200); self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, fmt, *args):
        print("HTTP:", fmt % args, flush=True)

def main():
    if TOKEN:
        threading.Thread(target=polling,daemon=True).start()
        print("Telegram polling started.",flush=True)
    else:
        print("TELEGRAM_BOT_TOKEN missing; health only until configured.",flush=True)
    HTTPServer(("0.0.0.0",PORT),Handler).serve_forever()

if __name__ == "__main__":
    main()
