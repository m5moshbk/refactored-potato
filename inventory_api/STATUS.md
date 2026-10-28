# حالة Nexus Inventory API | Nexus Inventory API Status

> آخر تحديث / Last updated: 2026-10-28 UTC

## العربية

- **المستودع:** `m5moshbk/refactored-potato`
- **فرع العمل المعزول:** `fix/nexus-inventory-api-validation`
- **طلب الدمج:** [PR #9](https://github.com/m5moshbk/refactored-potato/pull/9) — مفتوح كمسودة، غير مدمج.
- **الخدمة الحالية:** [m5mosh-nexus-inventory-api](https://m5mosh-nexus-inventory-api.onrender.com) تعمل على الفرع `feature/nexus-code-inventory-sync`. لم تُنشر تغييرات هذا الفرع عليها.
- **التغييرات:** تشديد التحقق من المسارات النسبية المعيارية ورفض المسارات المطلقة بصيغة Windows، ورفض القيم المنطقية كأحجام ملفات؛ إضافة اختبارات API وسير عمل CI مستقل وتوثيق عربي/إنجليزي.
- **الاختبار:** نجح تشغيل [GitHub Actions #40653017103](https://github.com/m5moshbk/refactored-potato/actions/runs/40653017103) على رأس الفرع `ae15002abf2bebee3fad20c9615d3517f8ff5646`، بما يشمل اختبارات API. يجب التأكد من نتيجة CI لأي تعديل لاحق قبل الدمج.
- **الخصوصية:** يقبل API بيانات وصفية محدودة ويخزن ملخصات إجمالية فقط؛ لا يُفترض حفظ محتوى المصدر أو مسارات الملفات.
- **التخزين:** قاعدة SQLite الافتراضية تحت `/tmp` مؤقتة.
- **الأسرار:** يجب ضبط `INGEST_TOKEN` في Render دون كشف قيمته.

### المتبقي قبل النشر
1. التأكد من نجاح CI على أحدث رأس للفرع.
2. مراجعة إعدادات `INGEST_TOKEN` والتخزين الدائم.
3. مراجعة طلب الدمج قبل أي دمج؛ لا تنشر هذا الفرع تلقائيًا على الخدمة الحية.

## English

- **Repository:** `m5moshbk/refactored-potato`
- **Isolated work branch:** `fix/nexus-inventory-api-validation`
- **Pull request:** [PR #9](https://github.com/m5moshbk/refactored-potato/pull/9) — open draft, not merged.
- **Current service:** [m5mosh-nexus-inventory-api](https://m5mosh-nexus-inventory-api.onrender.com) runs from `feature/nexus-code-inventory-sync`. This branch has not been deployed to it.
- **Changes:** strengthened normalized relative-path validation, rejected Windows absolute paths and boolean file sizes, and added API tests, a dedicated CI workflow, and bilingual documentation.
- **Tests:** [GitHub Actions run #40653017103](https://github.com/m5moshbk/refactored-potato/actions/runs/40653017103) passed on branch head `ae15002abf2bebee3fad20c9615d3517f8ff5646`, including API tests. Any later change must pass CI before merging.
- **Privacy:** the API accepts limited metadata and stores aggregate summaries only; source contents and detailed paths are not intended to be persisted.
- **Storage:** the default SQLite database under `/tmp` is ephemeral.
- **Secrets:** configure `INGEST_TOKEN` in Render without disclosing its value.

### Release blockers
1. Confirm CI passes on the latest branch head.
2. Review `INGEST_TOKEN` and persistent-storage settings.
3. Review the pull request before merging; do not automatically deploy this branch to the live service.

## بصمة المشروع | Project fingerprint
- Owner: Ahmed jafari
- Signature / rights tag: M5mOsH
- Contact: +99507190799
