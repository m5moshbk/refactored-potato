# حالة Nexus Inventory API | Nexus Inventory API Status

> آخر تحديث / Last updated: 2026-11-05 UTC

## تحديث دورة الاستمرارية — 2026-11-05

- **VERIFIED — PR #9:** مدمج في 2026-11-02؛ commit الدمج `c6d9674d84dbc46b04ab2d0f2a3cac045ac944f7`. الوصف السابق بأنه مفتوح وغير مدمج كان قديماً.
- **VERIFIED — PR #26:** مفتوح وغير مدمج، ويستهدف `feature/nexus-code-inventory-sync`. الرأس الحالي `35c2857e367583e1b47f28ded6d57a77891d9bd6`. تشغيل CI الجديد [41981331118](https://github.com/m5moshbk/refactored-potato/actions/runs/41981331118) بدأ بعد تحديث التوثيق؛ النتيجة النهائية لم تُؤكد بعد.
- **VERIFIED — PR #23:** مفتوح وغير مدمج، ويستهدف فرع الخدمة نفسه. لا دمج لأي من PR #23 أو #26 دون موافقة منفصلة؛ فرع الخدمة مراقب بواسطة Render Auto-deploy.
- **BLOCKED — Render re-check:** مساحة Render المحددة للفحص في هذه الدورة لا تعرض خدمات Nexus الثلاث. توجد مساحة أخرى باسم `M5mOsH Team`، ولم تُفحص دون تحديدها صراحة. بيانات Render السابقة تبقى لقطة تاريخية وليست إعادة تحقق اليوم.
- **NOT_TESTED — HTTP:** لا توجد استجابة HTTP حية جديدة موثقة في هذه الدورة.
- **NOT_CHANGED:** لا دمج أو نشر أو إعادة تشغيل أو تعديل إعدادات أو أسرار أو بيانات إنتاج.


## العربية

- **المستودع:** `m5moshbk/refactored-potato`
- **فرع العمل المعزول:** `fix/nexus-inventory-api-validation`
- **طلب الدمج:** [PR #9](https://github.com/m5moshbk/refactored-potato/pull/9) — مفتوح للمراجعة، غير مدمج.
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
- **Pull request:** [PR #9](https://github.com/m5moshbk/refactored-potato/pull/9) — open for review, not merged.
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

## الحقوق | Rights
© M5mOsH — All rights reserved.
