# حالة Nexus Inventory API | Nexus Inventory API Status

> آخر تحديث / Last updated: 2026-11-05 UTC

## تحديث دورة الاستمرارية — 2026-11-05

- **VERIFIED — PR #9:** مدمج في 2026-11-02؛ commit الدمج `c6d9674d84dbc46b04ab2d0f2a3cac045ac944f7`. الوصف السابق بأنه مفتوح وغير مدمج كان قديماً.
- **VERIFIED — PR #26:** مفتوح وغير مدمج، ويستهدف `feature/nexus-code-inventory-sync`. الرأس الذي تم التحقق منه `885d0435905498093ca9068114b3c0932b98ed6f`. GitHub Actions run [41981373378](https://github.com/m5moshbk/refactored-potato/actions/runs/41981373378) اكتمل بنجاح بعد تحديث التوثيق؛ النتيجة 18 اختبارًا ناجحًا.

- **VERIFIED — PR #23:** مفتوح وغير مدمج، ويستهدف فرع الخدمة نفسه. لا دمج لأي من PR #23 أو #26 دون موافقة منفصلة؛ فرع الخدمة مراقب بواسطة Render Auto-deploy.
- **BLOCKED — Render re-check:** مساحة Render المحددة للفحص في هذه الدورة لا تعرض خدمات Nexus الثلاث. توجد مساحة أخرى باسم `M5mOsH Team`، ولم تُفحص دون تحديدها صراحة. بيانات Render السابقة تبقى لقطة تاريخية وليست إعادة تحقق اليوم.
- **NOT_TESTED — HTTP:** لا توجد استجابة HTTP حية جديدة موثقة في هذه الدورة.
- **NOT_CHANGED:** لا دمج أو نشر أو إعادة تشغيل أو تعديل إعدادات أو أسرار أو بيانات إنتاج.


## العربية

- **المستودع:** `m5moshbk/refactored-potato`
- **فرع التغيير التاريخي:** `fix/nexus-inventory-api-validation`.
- **طلب الدمج:** [PR #9](https://github.com/m5moshbk/refactored-potato/pull/9) — مدمج في 2026-11-02؛ commit الدمج `c6d9674d84dbc46b04ab2d0f2a3cac045ac944f7`.
- **الخدمة الحالية:** [m5mosh-nexus-inventory-api](https://m5mosh-nexus-inventory-api.onrender.com) تعمل على الفرع `feature/nexus-code-inventory-sync`. لم تُنشر تغييرات هذا الفرع عليها.
- **التغييرات:** تشديد التحقق من المسارات النسبية المعيارية ورفض المسارات المطلقة بصيغة Windows، ورفض القيم المنطقية كأحجام ملفات؛ إضافة اختبارات API وسير عمل CI مستقل وتوثيق عربي/إنجليزي.
- **الاختبار التاريخي:** سجل [GitHub Actions #40653017103](https://github.com/m5moshbk/refactored-potato/actions/runs/40653017103) نجح على رأس سابق للفرع `ae15002abf2bebee3fad20c9615d3517f8ff5646`؛ لا يُعد ذلك إثباتًا مستقلاً لنتيجة CI على commit الدمج.
- **الخصوصية:** يقبل API بيانات وصفية محدودة ويخزن ملخصات إجمالية فقط؛ لا يُفترض حفظ محتوى المصدر أو مسارات الملفات.
- **التخزين:** قاعدة SQLite الافتراضية تحت `/tmp` مؤقتة.
- **الأسرار:** يجب ضبط `INGEST_TOKEN` في Render دون كشف قيمته.

### المتبقي قبل النشر
1. التحقق من CI على أي تعديل برمجي جديد قبل الدمج.
2. مراجعة وجود `INGEST_TOKEN` دون كشف قيمته، ومراجعة التخزين الدائم دون تغيير إعدادات الإنتاج.
3. لا دمج إلى فرع الخدمة ولا نشر دون موافقة منفصلة.

## English

- **Repository:** `m5moshbk/refactored-potato`
- **Historical change branch:** `fix/nexus-inventory-api-validation`.
- **Pull request:** [PR #9](https://github.com/m5moshbk/refactored-potato/pull/9) — merged on 2026-11-02; merge commit `c6d9674d84dbc46b04ab2d0f2a3cac045ac944f7`.
- **Current service:** [m5mosh-nexus-inventory-api](https://m5mosh-nexus-inventory-api.onrender.com) runs from `feature/nexus-code-inventory-sync`. This branch has not been deployed to it.
- **Changes:** strengthened normalized relative-path validation, rejected Windows absolute paths and boolean file sizes, and added API tests, a dedicated CI workflow, and bilingual documentation.
- **Historical tests:** [GitHub Actions run #40653017103](https://github.com/m5moshbk/refactored-potato/actions/runs/40653017103) passed on an earlier branch head `ae15002abf2bebee3fad20c9615d3517f8ff5646`; this is not an independent CI result for the merge commit.
- **Privacy:** the API accepts limited metadata and stores aggregate summaries only; source contents and detailed paths are not intended to be persisted.
- **Storage:** the default SQLite database under `/tmp` is ephemeral.
- **Secrets:** configure `INGEST_TOKEN` in Render without disclosing its value.

### Release blockers
1. Run CI for every new code change before merge.
2. Review `INGEST_TOKEN` presence without exposing its value and review persistent-storage options without changing production settings.
3. Do not merge to the service branch or deploy without separate explicit approval.

## الحقوق | Rights
© M5mOsH — All rights reserved.
