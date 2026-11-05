# حالة بوت Nexus Telegram | Nexus Telegram Bot Status

> آخر تحديث / Last updated: 2026-10-28 UTC

## العربية
- **المستودع:** `m5moshbk/refactored-potato`
- **فرع الإصلاح المعزول:** `fix/nexus-telegram-public-mode-opt-in`
- **الخدمة الحالية:** [m5mosh-nexus-telegram-catalog](https://m5mosh-nexus-telegram-catalog.onrender.com) تعمل من الفرع `main`. لم تُنشر تغييرات الفرع.
- **التغيير الأمني:** إيقاف دردشة AI العامة افتراضيًا عبر `NEXUS_PUBLIC_MODE=0`؛ يمكن تفعيلها صراحة من Render عند الحاجة.
- **التحكم:** يتطلب التشغيل الإداري ضبط `TELEGRAM_BOT_TOKEN` و`TELEGRAM_ADMIN_CHAT_ID`. لم تُقرأ أو تُعدّل أي قيم أسرار.
- **الاختبارات:** CI بعد إضافة اختبارات الوصول قيد التحقق.
- **الخصوصية والتكلفة:** الحد اليومي الحالي لكل محادثة فقط؛ لا يشكل حدًا عالميًا عند تفعيل الوضع العام.

### المتبقي
1. انتظار نجاح CI.
2. التأكد من ضبط رمز Telegram ومعرّف الإدارة في Render دون مشاركة القيم.
3. عدم تفعيل الوضع العام قبل تحديد حد تكلفة/استخدام مناسب.

## English
- **Repository:** `m5moshbk/refactored-potato`
- **Isolated fix branch:** `fix/nexus-telegram-public-mode-opt-in`
- **Current service:** [m5mosh-nexus-telegram-catalog](https://m5mosh-nexus-telegram-catalog.onrender.com) runs from `main`. This branch has not been deployed.
- **Security change:** public AI chat now defaults off through `NEXUS_PUBLIC_MODE=0`; it can be explicitly enabled in Render if desired.
- **Admin control:** set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ADMIN_CHAT_ID` in Render. No secret values were read or changed.
- **Tests:** CI after adding access tests is pending verification.
- **Privacy and cost:** the current daily limit is per chat only; it is not a global cost limit if public mode is enabled.

### Remaining work
1. Confirm CI passes.
2. Verify the Telegram token and admin chat ID are configured in Render without sharing values.
3. Do not enable public mode before setting an appropriate usage/cost policy.

## بصمة المشروع | Project fingerprint
- Rights: © M5mOsH All Rights Reserved
- Rights: © M5mOsH All Rights Reserved


## مرحلة مراقبة القنوات | Channel Intelligence — 2026-11-03
- أُضيف استقبال Telegram channel_post في فرع تطوير معزول.
- تحليل منشورات القنوات التي يسلّمها Telegram إلى البوت، مع دعم الرسائل المحوّلة عبر مسار الرسائل الموجود.
- تنبيهات خاصة إلى TELEGRAM_ADMIN_CHAT_ID، ومنع التكرار عبر SQLite.
- إخفاء أنماط شائعة للأسرار قبل تمرير النص للتحليل.
- لا نشر ولا رد آلي؛ مسودات فقط.
- لا يوجد نشر على Render حتى مراجعة الاختبارات ودمج التغيير.
- القنوات العامة التي لا يملك البوت صلاحية الوصول إليها لا يمكن قراءتها مباشرة بواسطة Bot API؛ استخدم إعادة توجيه المنشور أو صلاحية مناسبة.

- توسعة مراقبة القنوات لتشمل edited_channel_post مع منع تكرار كل نسخة تعديل، وإشعار الإدارة عند تعذر المعالجة دون كشف تفاصيل الاستثناء.
