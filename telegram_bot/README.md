# بوت فهرس M5mOsH Nexus

بوت Telegram للقراءة والاستعراض فقط، يعرض المستودعات والأقسام والغرض وطريقة الاستخدام والمكونات وروابط GitHub.

## الأوامر
- /start أو /help
- /sections
- /repos
- /stores
- /tools
- /unclassified
- /repo اسم-المستودع
- /search كلمة

## نشر Render
- Runtime: Python
- Build command: echo "No third-party dependencies"
- Start command: python telegram_bot/bot.py
- Health path: /health
- Environment variables: TELEGRAM_BOT_TOKEN (مطلوب لتفعيل الأوامر)، TELEGRAM_ADMIN_CHAT_ID (اختياري لكن موصى به للتقييد).

لا تضع رمز البوت في GitHub. أضفه من إعدادات Environment في Render فقط. من دون الرمز تعمل نقطة الصحة فقط.

## ملاحظة الدقة
الكتالوج أولي؛ المستودعات التي لم تُراجع ملفاتها موسومة بحاجة للتصنيف. البوت يعرض ملف catalog.json ولا يجلب بيانات GitHub الحية لكل استعلام. لا يدعم الحذف أو النشر أو تعديل المستودعات.
