# M5mOsH Nexus — فهرس المشاريع

مركز واجهة لتجميع روابط المشاريع ومعايناتها. هذا المستودع وخدمة Render المرتبطة به هما واجهة فهرسة؛ لا يفترضان أن جميع المشاريع متصلة ببعضها أو أن وظائفها التشغيلية قد اجتازت الاختبار.

## الهدف
توفير نقطة دخول واضحة لمشاريع M5mOsH، مع وصف موجز لكل مشروع، ورابط المستودع، ورابط المعاينة عند توفره، وفصل حالة النشر عن حالة التحقق الوظيفي.

## المشاريع الرئيسية

| المشروع | المهمة | المستودع | المعاينة المسجلة في Render |
|---|---|---|---|
| صَدَى / SADA | خدمات المساعد والذاكرة والأدوات؛ المستودع الحالي يحتوي API تشخيص/echo واختبارات وعميل Pythonista | [SADA](https://github.com/m5moshbk/SADA) | [مركز التحكم](https://m5mosh-control-center.onrender.com) |
| Elite Console X | لوحة إدارة وبوت Telegram مع حماية دخول وإعدادات بيئة | [Elite Console X](https://github.com/m5moshbk/m5moshbk-Elite-Console-X) | [فتح المعاينة](https://elite-console-x.onrender.com) |
| Sawa Play Monitor | لوحة عربية لاستقبال أحداث ومتابعة تقارير الحالة والتحليل | [Sawa Play Monitor](https://github.com/m5moshbk/Sawa-Play-Monitor) | [فتح المعاينة](https://sawa-play-monitor.onrender.com) |
| AUS Luxe | واجهة متجر لإكسسوارات السيارات | [المستودع الأساسي الحالي](https://github.com/m5moshbk/super-duper-octo-adventure) | [فتح المعاينة](https://aus-luxe-auto-store.onrender.com) |
| بوابة الأعمال/الدفع | نموذج تكامل أولي لبوابات الدفع؛ وضع المعاينة لا يعني تنفيذ مدفوعات حقيقية | [Tamara Business Site](https://github.com/m5moshbk/Tamara-Business-Site) | [خدمة Render المسجلة](https://beefitness-payments-gateway.onrender.com) |
| منصة الأعمال | واجهات وتجارب متعددة؛ يجب تحديد الفرع الصحيح قبل اعتماد أي معاينة كنسخة رئيسية | [bizweb-platform](https://github.com/m5moshbk/bizweb-platform) | [معاينة المحفظة](https://m5mosh-final-portfolio-preview.onrender.com) |

## قواعد الحالة
- **منشور**: توجد خدمة أو معاينة مسجلة.
- **تم التحقق**: اجتاز اختبارًا وظيفيًا موثقًا.
- **تجريبي**: واجهة أو مسار تجريبي، أو لم يكتمل التكامل.
- **مرشح للتوحيد**: يوجد احتمال تداخل مع مشروع آخر، ويحتاج مقارنة قبل أرشفته.

لا تساوِ بين وجود رابط Render وبين عمل جميع الوظائف. سجّل نتيجة اختبار الصحة والوظائف الفعلية وتاريخها قبل تغيير الحالة إلى «تم التحقق».

## سياسة تنظيم المستودعات
1. احتفظ بمصدر أساسي واحد لكل منتج.
2. لا تحذف مستودعًا متشابه الاسم قبل مقارنة الملفات والتاريخ والفروع وروابط النشر.
3. انقل التجارب إلى فروع واضحة أو أرشفها بعد التأكد من عدم وجود محتوى فريد.
4. لا تضع مفاتيح API أو كلمات المرور أو بيانات العملاء في المستودع.
5. وثّق الهدف، والمتطلبات، وطريقة التشغيل، ومتغيرات البيئة، والاختبارات، والقيود في README كل مشروع.

## المالك
M5mOsH


---

# English Summary

M5mOsH Nexus is a project index and preview directory. A Render URL or a successful deployment only confirms that a deployment exists; it does not prove every feature, integration, database, or authentication path works.

## Core services
- **Nexus static dashboard:** `https://m5mosh-nexus.onrender.com`
- **Code inventory API:** `https://m5mosh-nexus-inventory-api.onrender.com` — receives authenticated, metadata-only inventory summaries.
- **Telegram catalog service:** `https://m5mosh-nexus-telegram-catalog.onrender.com`

## Inventory API safeguards
- `POST /api/v1/inventory` requires a bearer token.
- `GET /api/v1/status` exposes aggregate status only.
- Source contents and detailed file paths are not intended to be stored.
- The default SQLite database under `/tmp` is ephemeral.
- See `inventory_api/README.md`, `inventory_api/DEPLOYMENT.md`, and `inventory_api/STATUS.md` for bilingual setup, deployment gates, and verified status.

## Operating rules
1. Keep one canonical repository per product and compare similar projects before retiring anything.
2. Keep API keys and passwords out of source control.
3. Separate deployed status from verified runtime behavior.
4. Test authentication, API input validation, integrations, and persistence before production rollout.
5. Do not automatically resume suspended services or promote preview branches without reviewing the changes.

## Project fingerprint
- Owner: Ahmed jafari
- Signature / rights tag: M5mOsH
- Contact: +99507190799
