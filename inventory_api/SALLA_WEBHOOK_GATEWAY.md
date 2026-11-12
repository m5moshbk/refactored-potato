# M5mOsH Salla Webhook Gateway

## العربية

### النطاق

يضيف هذا التغيير مستقبلًا مستقلاً لأحداث سلة على:

`POST /webhooks/salla`

هذه المرحلة هي **استقبال موثّق وتسجيل إيصال محدود فقط**. لا تنفّذ تعديلات على الطلبات أو المنتجات أو العملاء أو المدفوعات أو الشحن، ولا تستدعي واجهات سلة لإجراء تغييرات.

### المصادقة من شاشة التاجر الحالية

عند استخدام حقل **Request headers** في لوحة التاجر، اختر وضع الرمز المشترك:

1. أنشئ رمزًا عشوائيًا طويلًا محليًا، مثال للأمر: `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
2. أضف في Render متغيري البيئة:
   - `SALLA_WEBHOOK_AUTH_MODE=token`
   - `SALLA_WEBHOOK_TOKEN=<secret>`
3. في سلة، أضف Request Header:
   - Key: `X-M5mOsH-Webhook-Token`
   - Value: نفس الرمز الذي خزّنته في Render.
4. لا تحفظ الرمز في GitHub أو الكود أو الواجهة الأمامية أو المحادثات.

لا تستخدم `Authorization: Bearer` لهذا المستقبل؛ ترويسة التحقق المخصصة أعلاه هي العقد المعتمد لوضع الرمز في هذه المرحلة.

### وضع التوقيع الرسمي (Partner App)

يدعم المستقبل أيضًا وضع التوقيع إذا كان إعداد Salla Partner App يرسل ترويسات التوقيع الرسمية:

- `SALLA_WEBHOOK_AUTH_MODE=signature`
- `SALLA_WEBHOOK_SECRET=<secret configured for the Salla signature>`
- `X-Salla-Security-Strategy: Signature`
- `X-Salla-Signature: <64-character SHA-256 HMAC>`

يتم حساب HMAC-SHA256 على **بايتات جسم الطلب الخام** ومقارنته بمقارنة ثابتة التوقيت. لا تخلط وضع التوقيع مع وضع الرمز؛ اختر وضعًا واحدًا في إعدادات الخدمة.

### التخزين والخصوصية

- قاعدة البيانات مستقلة عن قاعدة Inventory API: `SALLA_WEBHOOK_DB_PATH`.
- المسار الافتراضي `/tmp/salla_webhooks.sqlite3` مؤقت، وقد يفقد البيانات عند إعادة التشغيل أو النشر.
- قبل تفعيل Webhook فعليًا، جهّز قرص Render دائمًا وعيّن `SALLA_WEBHOOK_DB_PATH` إلى مسار القرص، مثل `/var/data/salla_webhooks.sqlite3`.
- لا يُخزَّن جسم الطلب أو بيانات العميل أو البريد أو الهاتف أو العنوان أو تفاصيل الطلب/الدفع. يُخزَّن فقط اسم الحدث ووقت الاستلام وبصمة SHA-256 لجسم الطلب.
- تُستخدم البصمة لمنع تكرار إعادة إرسال **جسم مطابق تمامًا**. الجسم المطابق لاحقًا يُعاد له HTTP 200 دون إنشاء سجل جديد.
- حجم الطلب الأقصى 512 KiB.
- لا يوجد في هذه المرحلة طابور معالجة أو تنفيذ أعمال لاحقة؛ السجل يثبت وصول الحدث فقط.

### الاستجابات

| الحالة | المعنى |
|---|---|
| 202 | تم التحقق وتسجيل إيصال الحدث |
| 200 | إعادة إرسال مطابقة سبق تسجيلها |
| 401 | رمز أو توقيع غير صحيح |
| 415 | نوع المحتوى ليس JSON |
| 503 | المصادقة أو التخزين غير مهيأ/غير متاح |

### بوابة الإطلاق

لا تضع رابط الخدمة في سلة قبل نشر هذا الفرع بعد مراجعته، وضبط المصادقة، وتجهيز التخزين الدائم، والتحقق من CI واختبار استقبال تجريبي. إنشاء Pull Request لا ينشر الخدمة ولا يفعّل Webhook.

## English

The receiver accepts authenticated Salla POST callbacks at `/webhooks/salla`. It stores only the event name, receipt timestamp, and SHA-256 body fingerprint. It never persists the raw payload or customer/order/payment PII and performs no store mutations or downstream business actions.

For the merchant dashboard's custom Request Headers, configure `SALLA_WEBHOOK_AUTH_MODE=token` and store a high-entropy value in Render as `SALLA_WEBHOOK_TOKEN`. Set the Salla header key to `X-M5mOsH-Webhook-Token` and its value to the same secret. Do not use `Authorization: Bearer` for this receiver.

Partner App signature mode is also supported through `SALLA_WEBHOOK_AUTH_MODE=signature`, `SALLA_WEBHOOK_SECRET`, `X-Salla-Security-Strategy: Signature`, and `X-Salla-Signature`. The HMAC-SHA256 check uses the exact raw request bytes and constant-time comparison.

The default SQLite path under `/tmp` is ephemeral. A Render persistent disk and `SALLA_WEBHOOK_DB_PATH` pointing to that disk are required before production activation. Exact-body retries are deduplicated by the payload hash. A successful receipt is not evidence that any downstream processing occurred.

## References

- Salla Webhooks: https://docs.salla.dev/421119m0
- Salla Merchant help: https://help.salla.sa/article/%D8%A5%D8%B1%D8%B3%D8%A7%D9%84-%D8%A7%D9%84%D8%A5%D8%B4%D8%B9%D8%A7%D8%B1%D8%A7%D8%AA-%D9%84%D9%84%D8%AE%D8%AF%D9%85%D8%A7%D8%AA-%D8%A3%D8%AE%D8%B1%D9%89-%D8%B9%D8%A8%D8%B1-%D8%A7%D9%84%D9%88%D9%8A%D8%A8-%D9%87%D9%88%D9%83-webhooks-1/fzsikgjw2m8dfm8j5ep2ez4e

## الحقوق | Rights

© M5mOsH All Rights Reserved
