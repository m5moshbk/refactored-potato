# بوت فهرس M5mOsH Nexus

بوت Telegram للقراءة والاستعراض فقط، يعرض المستودعات والأقسام والغرض وطريقة الاستخدام والمكونات وروابط GitHub.

## الأوامر
- /start أو /help
- /sections
- /repos
- /stores
- /tools
- /unclassified
- /services — خدمات Render
- /service اسم-الخدمة — تفاصيل الخدمة ورابطها ولوحة إدارتها
- /projects — المشاريع الأساسية
- /repo اسم-المستودع
- /search كلمة (يبحث في المستودعات والخدمات)

## نشر Render
- Runtime: Python
- Build command: echo "No third-party dependencies"
- Start command: python telegram_bot/bot.py
- Health path: /health
- Environment variables: TELEGRAM_BOT_TOKEN (مطلوب لتفعيل الأوامر)، TELEGRAM_ADMIN_CHAT_ID (اختياري لكن موصى به للتقييد).

لا تضع رمز البوت في GitHub. أضفه من إعدادات Environment في Render فقط. من دون الرمز تعمل نقطة الصحة فقط.

## ملاحظة الدقة
الكتالوج أولي؛ المستودعات التي لم تُراجع ملفاتها موسومة بحاجة للتصنيف. البوت يعرض ملف catalog.json ولا يجلب بيانات GitHub الحية لكل استعلام. لا يدعم الحذف أو النشر أو تعديل المستودعات.


## معنى Environment في Render

Environment هي إعدادات تشغيل خاصة بالخدمة. أضفها من صفحة Render الخاصة بالخدمة، ولا تحفظ قيم الأسرار في GitHub:
- `TELEGRAM_BOT_TOKEN`: رمز البوت من BotFather، مطلوب لتلقي أوامر Telegram.
- `TELEGRAM_ADMIN_CHAT_ID`: اختياري؛ عند ضبطه لا يجيب البوت إلا للمحادثة ذات هذا المعرّف.

## نطاق الفهرس

الكتالوج يضم مستودعات GitHub الـ34 التي ظهرت في الجرد، و18 خدمة Render ظاهرة في مساحة العمل وقت آخر جرد. يشمل ذلك معاينات فروع متعددة وخدمات موقوفة؛ وجودها في القائمة لا يعني أنها تعمل. الأوامر للقراءة فقط ولا تنفذ deploy أو restart أو حذفًا أو تعديلًا.
