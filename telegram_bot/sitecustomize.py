import json, os, time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
TOKEN=os.getenv("TELEGRAM_BOT_TOKEN","").strip()
ADMIN=os.getenv("TELEGRAM_ADMIN_CHAT_ID","").strip()
NOTIFICATIONS_ENABLED=os.getenv("NEXUS_NOTIFICATIONS_ENABLED","1").strip().lower() in ("1","true","yes","on")
API="https://api.telegram.org/bot"+TOKEN+"/"
def call(method,params):
    if not TOKEN:return False
    try:
        req=Request(API+method,data=urlencode(params).encode(),headers={"Content-Type":"application/x-www-form-urlencoded"})
        with urlopen(req,timeout=12) as r:data=json.loads(r.read().decode())
        return bool(data.get("ok"))
    except Exception as exc:
        print("Nexus profile setup error:",method,type(exc).__name__,flush=True);return False

def notify_admin(text):
    if not (NOTIFICATIONS_ENABLED and TOKEN and ADMIN):return False
    try:
        req=Request(API+"sendMessage",data=urlencode({"chat_id":ADMIN,"text":text[:3900],"disable_web_page_preview":"true"}).encode(),headers={"Content-Type":"application/x-www-form-urlencoded"})
        with urlopen(req,timeout=12) as r:data=json.loads(r.read().decode())
        return bool(data.get("ok"))
    except Exception as exc:
        print("Nexus notification error:",type(exc).__name__,flush=True);return False
PROFILE={
 "":("M5mOsH Nexus","مركز تحكم ذكي للمشاريع والمستودعات والجرد والتشخيص.","M5mOsH Nexus — مركز تحكم ذكي للمشاريع والمستودعات وخدمات Render، الجرد الحي، التشخيص، الذاكرة وفحص المتاجر. لا يدّعي نجاحًا غير مُتحقق، ويتحول تلقائيًا إلى وضع مجاني احتياطي عند تعذر مزود AI."),
 "ar":("M5mOsH Nexus | مركز التحكم","مركز تحكم ذكي للمشاريع والمستودعات والجرد والتشخيص.","مركز التحكم الذكي M5mOsH Nexus: مشاريع، GitHub، Render، جرد حي، تشخيص، ذاكرة، وفحص المتاجر. لا نعرض نجاحًا غير مُتحقق. عند تعذر مزود الذكاء الاصطناعي يعمل وضع Nexus المجاني الاحتياطي تلقائيًا."),
 "en":("M5mOsH Nexus | Control Center","Smart control center for projects, repositories, inventory and diagnostics.","M5mOsH Nexus is a control center for GitHub, Render, live inventory, diagnostics, memory and storefront audits. It avoids unverified success claims and automatically falls back to free local mode when an AI provider is unavailable.")}
for lang,(name,short,desc) in PROFILE.items():
    call("setMyName",{"name":name,"language_code":lang})
    call("setMyShortDescription",{"short_description":short,"language_code":lang})
    call("setMyDescription",{"description":desc,"language_code":lang})
COMMANDS=[("start","بدء Nexus"),("menu","القائمة الرئيسية"),("help","المساعدة"),("status","الحالة"),("diagnostics","تشخيص البوت"),("inventory","الجرد الحي"),("repos","مستودعات GitHub"),("services","خدمات Render"),("projects","المشاريع"),("notes","ملاحظات المشاريع"),("memory","الذاكرة"),("clear","مسح ذاكرة المحادثة"),("models","محركات ونماذج AI"),("audit","فحص متجر للقراءة فقط"),("search","بحث الفهرس"),("web","بحث الويب"),("about","حول Nexus")]
for lang in ("","ar"):
    call("setMyCommands",{"commands":json.dumps([{"command":c,"description":d} for c,d in COMMANDS],ensure_ascii=False),"language_code":lang})
call("setChatMenuButton",{"menu_button":json.dumps({"type":"commands"})})
if NOTIFICATIONS_ENABLED and TOKEN and ADMIN:
    commit=os.getenv("RENDER_GIT_COMMIT","")[:12] or "غير معروف"
    service=os.getenv("RENDER_SERVICE_NAME","M5mOsH Nexus")
    notify_admin("🟢 تنبيه Nexus\nبدأت الخدمة تشغيلها.\nالخدمة: "+service[:120]+"\nالإصدار: "+commit+"\nالوقت: "+time.strftime("%Y-%m-%d %H:%M:%S UTC",time.gmtime()))
print("Nexus Telegram profile bootstrap completed",flush=True)
