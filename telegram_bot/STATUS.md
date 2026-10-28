# حالة بوت Nexus Telegram | Nexus Telegram Bot Status

> آخر تحديث / Last updated: 2026-10-28 UTC

## العربية
- **المستودع:** `m5moshbk/refactored-potato`
- **فرع الإصلاح المعزول:** `fix/nexus-telegram-public-mode-opt-in`
- **الخدمة الحالية:** [m5mosh-nexus-telegram-catalog](https://m5mosh-nexus-telegram-catalog.onrender.com) تعمل من الفرع `main`. لم تُنشر تغييرات فرع الإصلاح.
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
- Owner: Ahmed jafari
- Signature / rights tag: M5mOsH
- Contact: +99507190799
