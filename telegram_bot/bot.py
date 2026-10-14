#!/usr/bin/env python3
"""M5mOsH Nexus Telegram catalog with interactive inline navigation; read-only."""
import json, os, time, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from store_audit import audit_store

ROOT = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ROOT, "catalog.json"), encoding="utf-8") as f:
    CATALOG = json.load(f)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
ADMIN = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
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
        [button("📁 مستودعات GitHub", "repos:0")],
        [button("☁️ خدمات Render", "services:0")],
        [button("🛍️ فحص متجر عميل", "store_audit_help")],
        [button("🧭 مشاريعي", "projects"), button("🗂️ تصنيف المجالات", "categories")],
        [button("🔎 بحث", "search_help"), button("📊 ملخص الفهرس", "overview")],
        [button("❔ المساعدة والأوامر", "help"), button("ℹ️ حول البوت", "about")],
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



LIVE_STATUS = {
    "github": "لم يُفحص بعد",
    "render": "لم يُفحص بعد",
    "last_refresh": None,
    "errors": []
}

def _json_get(url, headers=None, timeout=15):
    req = Request(url, headers={"User-Agent": "M5mOsH-Nexus-Live-Inventory/1.0",
                                "Accept": "application/json", **(headers or {})})
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))

def refresh_live_inventory():
    """Refresh in-memory catalog from live APIs. Read-only; never changes remote projects."""
    errors = []
    gh_token = os.getenv("GITHUB_TOKEN", "").strip()
    render_key = os.getenv("RENDER_API_KEY", "").strip()
    now = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    if gh_token:
        try:
            found = []
            for page in range(1, 6):
                data = _json_get(
                    "https://api.github.com/user/repos?per_page=100&page=" + str(page) +
                    "&sort=updated&direction=desc",
                    {"Authorization": "Bearer " + gh_token,
                     "X-GitHub-Api-Version": "2022-11-28"})
                if not isinstance(data, list):
                    raise ValueError("Unexpected GitHub API response")
                for r in data:
                    owner = (r.get("owner") or {}).get("login", "")
                    full_name = r.get("full_name", "")
                    found.append({
                        "name": r.get("name", full_name.rsplit("/", 1)[-1]),
                        "full_name": full_name,
                        "url": r.get("html_url", ""),
                        "category": "بحاجة للتصنيف",
                        "purpose": (r.get("description") or "الغرض غير موثق؛ يلزم فحص README والملفات."),
                        "usage": "بيانات مستودع حية من GitHub؛ لم يُنفّذ الكود أو يُختبر.",
                        "default_branch": r.get("default_branch", "غير معروف"),
                        "private": bool(r.get("private", False)),
                        "updated_at": r.get("updated_at", ""),
                        "status": "بيانات GitHub مباشرة؛ لا تعني أن المشروع يعمل",
                        "owner": owner
                    })
                if len(data) < 100:
                    break
            if found:
                CATALOG["repositories"] = found
                LIVE_STATUS["github"] = "مباشر: " + str(len(found)) + " مستودع"
            else:
                LIVE_STATUS["github"] = "نجح الاتصال؛ لا توجد مستودعات ظاهرة"
        except Exception as exc:
            LIVE_STATUS["github"] = "فشل التحديث"
            errors.append("GitHub: " + type(exc).__name__)
    else:
        LIVE_STATUS["github"] = "يتطلب GITHUB_TOKEN في Render للوصول إلى المستودعات الخاصة"

    if render_key:
        try:
            data = _json_get("https://api.render.com/v1/services?limit=100",
                             {"Authorization": "Bearer " + render_key})
            if not isinstance(data, list):
                raise ValueError("Unexpected Render API response")
            found = []
            for entry in data:
                s = entry.get("service", entry) if isinstance(entry, dict) else {}
                if not isinstance(s, dict):
                    continue
                details = s.get("serviceDetails") or {}
                env_details = details.get("envSpecificDetails") or {}
                repo_url = s.get("repo", "") or ""
                repo = repo_url.replace("https://github.com/", "").removesuffix(".git")
                url = s.get("url", "")
                suspended = s.get("suspended")
                status = "معلّقة" if suspended else "غير معلّقة حسب Render؛ يلزم فحص التطبيق"
                found.append({
                    "name": s.get("name", "خدمة Render"),
                    "type": s.get("type", "غير معروف"),
                    "url": url,
                    "repo": repo,
                    "branch": s.get("branch", "غير معروف"),
                    "runtime": details.get("runtime", s.get("type", "غير معروف")),
                    "status": status,
                    "purpose": "بيانات خدمة مباشرة من Render؛ الحالة لا تثبت صحة الوظائف.",
                    "dashboard": s.get("dashboardUrl", ""),
                    "service_id": s.get("id", ""),
                    "updated_at": s.get("updatedAt", "")
                })
            CATALOG["services"] = found
            LIVE_STATUS["render"] = "مباشر: " + str(len(found)) + " خدمة"
        except Exception as exc:
            LIVE_STATUS["render"] = "فشل التحديث"
            errors.append("Render: " + type(exc).__name__)
    else:
        LIVE_STATUS["render"] = "يتطلب RENDER_API_KEY في Render"

    LIVE_STATUS["last_refresh"] = now
    LIVE_STATUS["errors"] = errors
    print("Live inventory refresh:", "GitHub=" + LIVE_STATUS["github"],
          "Render=" + LIVE_STATUS["render"], "errors=" + str(errors), flush=True)
    return LIVE_STATUS

def live_status_text():
    return ("📡 حالة الجرد الحي — قراءة فقط\\n"
            + "GitHub: " + LIVE_STATUS["github"] + "\\n"
            + "Render: " + LIVE_STATUS["render"] + "\\n"
            + "آخر محاولة: " + str(LIVE_STATUS["last_refresh"] or "لم تبدأ") + "\\n"
            + ("ملاحظات: " + ", ".join(LIVE_STATUS["errors"]) if LIVE_STATUS["errors"] else
               "لا توجد أخطاء مسجلة في آخر محاولة.")
            + "\\n\\nلا تُعدّل هذه الميزة المستودعات أو الخدمات؛ إنها تقرأ بياناتها فقط.")

def live_inventory_worker():
    while True:
        try:
            refresh_live_inventory()
        except Exception as exc:
            print("Live inventory worker error:", type(exc).__name__, flush=True)
        time.sleep(900)

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


def category_list():
    return sorted({r.get("category", "بحاجة للتصنيف") for r in repos()})

def category_keyboard():
    rows = []
    for idx, category in enumerate(category_list()):
        count = sum(1 for r in repos() if r.get("category", "بحاجة للتصنيف") == category)
        rows.append([button(f"{category} ({count})"[:48], "category:" + str(idx))])
    rows.append([button("🏠 القائمة الرئيسية", "menu")])
    return rows

def category_repositories(index):
    categories = category_list()
    if not 0 <= index < len(categories):
        return "هذا التصنيف غير متاح.", [[button("🗂️ التصنيفات", "categories")]]
    category = categories[index]
    selected = [(i, r) for i, r in enumerate(repos())
                if r.get("category", "بحاجة للتصنيف") == category]
    rows = [[button(r.get("name", "مستودع")[:48], "repo:" + str(i))]
            for i, r in selected[:30]]
    rows.append([button("⬅️ التصنيفات", "categories"), button("🏠 الرئيسية", "menu")])
    return f"🗂️ المجال: {category}\nالمستودعات المسجلة: {len(selected)}", rows

def overview():
    categories = category_list()
    counts = []
    for category in categories:
        count = sum(1 for r in repos() if r.get("category", "بحاجة للتصنيف") == category)
        counts.append(f"• {category}: {count}")
    return ("📊 ملخص الفهرس (بيانات مسجلة وليست فحصًا حيًا)\n"
            f"مستودعات GitHub: {len(repos())}\nخدمات Render المسجلة: {len(services())}\n\n"
            + "\n".join(counts))


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
        edit(chat_id, message_id, "🗂️ اختر مجالًا لعرض المستودعات التابعة له. التصنيف أولي وقد يحتاج مراجعة.", category_keyboard())
    elif data.startswith("category:"):
        try:
            idx = int(data.split(":", 1)[1])
            text, keyboard = category_repositories(idx)
            edit(chat_id, message_id, text, keyboard)
        except (ValueError, IndexError):
            edit(chat_id, message_id, "تعذر فتح التصنيف.", category_keyboard())
    elif data == "store_audit_help":
        edit(chat_id, message_id, "🛍️ فحص متجر عميل\\nأرسل رابط المتجر في هذه المحادثة مع طلب فحصه. تشمل المراجعة الظاهرة: الدفع، صفحات المنتجات، تجربة الجوال، الشحن والاسترجاع، التواصل، عناصر الثقة، SEO، والصور. الفحص الأولي لا يسجل الدخول ولا يختبر معاملة دفع.", [[button("🏠 القائمة الرئيسية", "menu")]])
    elif data == "overview":
        edit(chat_id, message_id, overview(), [[button("🏠 القائمة الرئيسية", "menu")]])
    elif data == "live_inventory":
        edit(chat_id, message_id, live_status_text(), [[button("🔄 إعادة المحاولة", "live_inventory_refresh")], [button("🏠 القائمة الرئيسية", "menu")]])
    elif data == "live_inventory_refresh":
        refresh_live_inventory()
        edit(chat_id, message_id, live_status_text(), [[button("🔄 إعادة المحاولة", "live_inventory_refresh")], [button("🏠 القائمة الرئيسية", "menu")]])
    elif data == "help":
        edit(chat_id, message_id,
             "❔ المساعدة\nيمكن استخدام الأزرار دون كتابة أوامر. الأوامر الاختيارية:\n/start أو /menu — القائمة الرئيسية\n/repos — المستودعات\n/services — خدمات Render\n/projects — المشاريع\n/search كلمة — البحث\n/help — المساعدة",
             [[button("🏠 القائمة الرئيسية", "menu")]])
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



def ask_gpt(user_text):
    """Answer natural-language messages with Gemini; no tools or external actions."""
    if not GEMINI_API_KEY:
        return ("مساعد الذكاء الاصطناعي غير مفعّل: أضف GEMINI_API_KEY في Render Environment "
                "ثم أعد النشر. لا ترسل المفتاح داخل تيليجرام.")
    payload = {
        "systemInstruction": {"parts": [{"text":
            "أنت مساعد M5mOsH Nexus باللغة العربية. أجب بوضوح واختصار. "
            "أنت لا تملك أدوات تنفيذ أو وصولًا مباشرًا إلى GitHub أو Render أو ملفات الجهاز. "
            "لا تدّعِ أنك نفذت أو فحصت أو نشرت شيئًا. إذا طُلب إجراء خارجي، وضّح أن هذا الإصدار يجيب فقط ولا ينفذ الإجراء. "
            "بيانات الكتالوج ليست بالضرورة مباشرة أو محدثة."}]},
        "contents": [{"role": "user", "parts": [{"text": user_text[:6000]}]}],
        "generationConfig": {"maxOutputTokens": 700}
    }
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/" + GEMINI_MODEL + ":generateContent"
    req = Request(endpoint,
                  data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                  headers={"x-goog-api-key": GEMINI_API_KEY,
                           "Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=40) as response:
            result = json.loads(response.read().decode("utf-8"))
        parts = []
        for candidate in result.get("candidates", []):
            content = candidate.get("content") or {}
            for part in content.get("parts", []):
                if part.get("text"):
                    parts.append(part["text"])
            if parts:
                break
        answer = "\n".join(parts).strip()
        if not answer:
            feedback = result.get("promptFeedback") or {}
            reason = feedback.get("blockReason", "unknown")
            print("Gemini empty response: block_reason=" + str(reason), flush=True)
            return "لم يُرجع Gemini نصًا. جرّب صياغة أخرى أو تحقق من إعدادات النموذج."
        return answer[:3900]
    except HTTPError as exc:
        details = {}
        try:
            body = json.loads(exc.read().decode("utf-8", errors="replace"))
            details = body.get("error", {}) if isinstance(body, dict) else {}
        except Exception:
            pass
        print("Gemini HTTP error:",
              "status=" + str(exc.code),
              "status_text=" + str(details.get("status", "unknown")),
              "message=" + str(details.get("message", "unknown"))[:180],
              flush=True)
        if exc.code == 429:
            return "تجاوز البوت حد استخدام Gemini أو الحصة المتاحة. انتظر إعادة ضبط الحد أو تحقق من AI Studio."
        if exc.code in (400, 403, 404):
            return "تعذر استخدام Gemini: تحقق من صلاحية GEMINI_API_KEY واسم GEMINI_MODEL في Render."
        return "تعذر الاتصال بـ Gemini. راجع سجل Render لرمز الخطأ دون مشاركة المفتاح."
    except URLError as exc:
        print("Gemini network error:", type(exc.reason).__name__, flush=True)
        return "تعذر الوصول إلى خدمة Gemini بسبب مشكلة اتصال. حاول لاحقًا."
    except Exception as exc:
        print("Gemini request error:", type(exc).__name__, flush=True)
        return "تعذر الاتصال بـ Gemini. راجع سجل Render لتشخيص الخطأ."


def handle_message(chat_id, text, forwarded=False):
    if not ADMIN or str(chat_id) != ADMIN:
        send(chat_id, "هذا البوت خاص، ولم تُمنح هذه المحادثة صلاحية الاستخدام.")
        return
    raw_text = (text or "").strip()
    if forwarded and raw_text:
        prompt = ("حلل رسالة أو محادثة عميل متجر إلكتروني لأجل مساعدتي في تقديم خدمة مهنية. " 
                  "استخرج: احتياج العميل المؤكد، ما يحتاج سؤالًا توضيحيًا، فرص الخدمات المناسبة دون وعود غير مؤكدة، " 
                  "ومسودة رد سعودي مهني قصيرة. لا تفترض معلومات غير مذكورة، ولا تكرر أرقام الهاتف أو البيانات الشخصية غير اللازمة. " 
                  "النص المنقول من العميل:\\n" + raw_text[:5000])
        send(chat_id, ask_gpt(prompt), [[button("🛍️ فحص متجر العميل", "store_audit_help")], [button("🏠 القائمة الرئيسية", "menu")]])
        return
    cmd, _, arg = raw_text.partition(" ")
    cmd = cmd.split("@")[0].lower()
    if cmd in ("/start", "/help", "/مساعدة", "/menu"):
        send(chat_id, "🧭 M5mOsH Nexus\nاختر المجال من الأزرار. كتابة الأوامر اختيارية وليست مطلوبة للتنقل.", menu())
    elif cmd in ("/repos", "/المستودعات"):
        send(chat_id, f"📦 المستودعات المسجلة: {len(repos())}", page_keyboard("repo", 0, len(repos())))
    elif cmd in ("/services", "/خدمات"):
        send(chat_id, f"☁️ خدمات Render المسجلة: {len(services())}\nهذه بيانات الكتالوج وليست فحصًا حيًا.", page_keyboard("service", 0, len(services())))
    elif cmd in ("/projects", "/المشاريع"):
        send(chat_id, project_summary(), [[button("🏠 القائمة الرئيسية", "menu")]])
    elif cmd in ("/sitecheck",):
        if not arg.strip():
            send(chat_id, "أرسل رابط المتجر: /sitecheck https://example.com")
        else:
            try:
                send(chat_id, audit_store(arg.strip()), [[button("🛍️ فحص متجر آخر", "store_audit_help")], [button("🏠 الرئيسية", "menu")]])
            except ValueError as exc:
                send(chat_id, "تعذر الفحص: " + str(exc))
    elif cmd in ("/inventory", "/الجرد"):
        refresh_live_inventory()
        send(chat_id, live_status_text(), [[button("🔄 إعادة المحاولة", "live_inventory_refresh")], [button("🏠 القائمة الرئيسية", "menu")]])
    elif cmd in ("/help", "/مساعدة"):
        send(chat_id, "الأوامر اختيارية؛ استخدم أزرار القائمة للتنقل.\n/start أو /menu، /repos، /services، /projects، /search كلمة، /help", menu())
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
            rows = [
                [button(("📦 " if k == "repo" else "☁️ ") + name[:48], k + ":" + str(idx))]
                for k, idx, name in found[:18]
            ]
            rows.append([button("🏠 القائمة الرئيسية", "menu")])
            send(chat_id, f"🔎 النتائج: {len(found)} — أعرض أول {min(18, len(found))}", rows)
    else:
        send(chat_id, ask_gpt((text or "").strip()))


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
                            if ADMIN and str(chat["id"]) == ADMIN:
                                on_callback(chat["id"], msg.get("message_id"), callback["data"])
                    except Exception as exc:
                        print("Telegram callback error:", type(exc).__name__, flush=True)
                    continue
                msg = item.get("message") or item.get("edited_message")
                if msg and msg.get("chat") and msg.get("text"):
                    forwarded = bool(msg.get("forward_origin") or msg.get("forward_date") or msg.get("forward_from"))
                    handle_message(msg["chat"]["id"], msg["text"], forwarded=forwarded)
        except HTTPError as exc:
            # Never log the request URL: Telegram URLs contain the bot token.
            details = {}
            try:
                body = json.loads(exc.read().decode("utf-8", errors="replace"))
                details = body.get("description", "") if isinstance(body, dict) else ""
            except Exception:
                pass
            description = str(details)[:180]
            if exc.code == 409:
                print("Telegram polling HTTP 409: conflict; another getUpdates poller may be active. " +
                      description, flush=True)
            else:
                print("Telegram polling HTTP error: status=" + str(exc.code) +
                      " description=" + description, flush=True)
            time.sleep(8 if exc.code == 409 else 5)
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
    threading.Thread(target=live_inventory_worker, daemon=True).start()
    if TOKEN:
        threading.Thread(target=polling, daemon=True).start()
        print("Telegram polling started; inline menu enabled.", flush=True)
    else:
        print("TELEGRAM_BOT_TOKEN missing; health only until configured.", flush=True)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
