# بوت فهرس M5mOsH Nexus | M5mOsH Nexus Catalog Bot

## العربية

بوت Telegram للقراءة والاستعراض فقط، يعرض المستودعات والأقسام والغرض وطريقة الاستخدام والمكونات وروابط GitHub. لا يحذف أو يعدّل أو ينشر مستودعات.

### الأوامر
- `/start` أو `/help`
- `/sections`
- `/repos`
- `/stores`
- `/tools`
- `/unclassified`
- `/services` — خدمات Render
- `/service اسم-الخدمة` — تفاصيل الخدمة المسجلة
- `/projects`
- `/repo اسم-المستودع`
- `/search كلمة`

### إعداد Render
- Runtime: Python
- Build command: `echo "No third-party dependencies"`
- Start command: `python telegram_bot/bot.py`
- Health path: `/health`
- `TELEGRAM_BOT_TOKEN`: مطلوب لتلقي أوامر Telegram.
- `TELEGRAM_ADMIN_CHAT_ID`: مطلوب للسماح لمحادثة الإدارة.
- `NEXUS_PUBLIC_MODE`: الافتراضي `0`؛ لا يُفعّل دردشة AI العامة إلا إذا ضبطته صراحة إلى `1`.
- `NEXUS_PUBLIC_DAILY_LIMIT`: حد الرسائل لكل محادثة عند تفعيل الوضع العام؛ لا يمثل حدًا عالميًا للتكاليف.

لا تضع رمز البوت أو مفاتيح AI في GitHub. أضف الأسرار من إعدادات Environment في Render فقط. إذا غاب الرمز، تعمل نقطة الصحة فقط. إذا غاب معرّف الإدارة، لا تُمنح أي محادثة صلاحية الإدارة.

### الدقة والخصوصية
الكتالوج أولي؛ المستودعات التي لم تُراجع ملفاتها موسومة بحاجة للتصنيف. البوت يعرض `catalog.json` ولا يجلب بيانات GitHub الحية لكل استعلام. لا ترسل كلمات مرور أو مفاتيح أو بيانات عملاء في الدردشة. ذاكرة المحادثة محلية وقد لا تبقى بعد إعادة نشر Render ما لم يُضبط تخزين دائم.

### الاختبارات
من جذر المستودع:

```bash
python -m pip install pytest
python -m pytest -q telegram_bot/test_bot_access.py
```

## English

A read-only Telegram catalog bot for repositories, sections, purposes, usage notes, components, and GitHub links. It does not delete, modify, or publish repositories.

### Render configuration
- Runtime: Python
- Build command: `echo "No third-party dependencies"`
- Start command: `python telegram_bot/bot.py`
- Health path: `/health`
- `TELEGRAM_BOT_TOKEN`: required to receive Telegram commands.
- `TELEGRAM_ADMIN_CHAT_ID`: required to authorize an admin chat.
- `NEXUS_PUBLIC_MODE`: defaults to `0`; public AI chat is opt-in and requires setting it to `1`.
- `NEXUS_PUBLIC_DAILY_LIMIT`: per-chat limit when public mode is enabled; it is not a global cost limit.

Never commit the Telegram token or AI keys to GitHub. Add secrets through Render Environment settings only. Without a bot token, only health checks work. Without an admin chat ID, no chat is granted admin access.

### Accuracy and privacy
The catalog is preliminary; unreviewed repositories are marked for classification. The bot reads `catalog.json` and does not fetch live GitHub data for every query. Do not send passwords, API keys, or customer data in chat. Conversation memory is local and may not survive Render redeploys unless persistent storage is configured.

### Tests
From the repository root:

```bash
python -m pip install pytest
python -m pytest -q telegram_bot/test_bot_access.py
```

## بصمة المشروع | Project fingerprint
- Owner: Ahmed jafari
- Signature / rights tag: M5mOsH
- Contact: +99507190799
