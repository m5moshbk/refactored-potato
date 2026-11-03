# حالة Nexus Inventory API | Nexus Inventory API Status

> آخر تحديث / Last updated: 2026-11-03 UTC

## تحديث المشغّل المستقل — 2026-11-03 07:37 UTC

- **التحقق:** أضيف تحقق فعلي من صيغة ISO-8601 لكل من `checked_at` و`files[].modified`؛ تُرفض السلاسل المشوهة والتواريخ غير الصالحة والتاريخ دون جزء زمني.
- **اختبارات الانحدار:** أضيفت حالات للمدخلات غير الصالحة، وللتوقيت بصيغة UTC `Z`، والإزاحة الزمنية، والتوقيت المحلي دون إزاحة.
- **الفرع المعزول:** `feat/nexus-autonomous-operator-20261103`، بعيد عن فرع Render المتصل بالخدمة.
- **Commits:** `5b60984aa1346a252d1401cdac695dff41d7393a` (التحقق)، ثم `80e394e99d5515d33614d984f3648fcce35be504` (الاختبارات).
- **CI مؤكد:** GitHub Actions run [41597480704](https://github.com/m5moshbk/refactored-potato/actions/runs/41597480704) — نجح، ونتيجة pytest: **23 passed in 0.25s**.
- **حدود الاختبار:** اختبارات Flask المحلية عبر CI فقط؛ لم يتم تأكيد HTTP حيّ من واجهة الوصول الحالية، ولم يتم تغيير الخدمة أو إعدادات Render.
- **مراجعة:** التغييرات موجودة ضمن PR #23 للمراجعة، ولا تزال غير مدمجة.

## العربية

- **المستودع:** `m5moshbk/refactored-potato`
- **فرع الخدمة:** `feature/nexus-code-inventory-sync`.
- **الخدمة:** [m5mosh-nexus-inventory-api](https://m5mosh-nexus-inventory-api.onrender.com).
- **حالة Render المؤكدة:** الخدمة غير معلّقة، وتعمل بإعداد Auto-deploy مفعّل على فرع الخدمة. أحدث نشر ظاهر في سجل Render انتهى بالحالة `live` على commit `c6d9674d84dbc46b04ab2d0f2a3cac045ac944f7` بتاريخ 2026-11-03 03:10:42 UTC.
- **PR #9:** [Fix Nexus inventory API path validation and add tests](https://github.com/m5moshbk/refactored-potato/pull/9) — مدمج في 2026-11-02، وcommit الدمج `c6d9674d84dbc46b04ab2d0f2a3cac045ac944f7`. الحالة السابقة التي وصفته بأنه مفتوح وغير مدمج كانت قديمة.
- **التغييرات المدمجة:** تشديد التحقق من المسارات النسبية المعيارية ورفض المسارات المطلقة بصيغة Windows، ورفض القيم المنطقية كأحجام ملفات؛ إضافة اختبارات API وسير عمل CI وتوثيق عربي/إنجليزي.
- **الاختبارات:** سجل PR #9 التاريخي يذكر نجاح CI على رأس سابق للفرع. فحص commit الدمج نفسه عبر GitHub أظهر عدم وجود check runs أو statuses منشورة في الاستعلام الحالي؛ لذلك لا نصف commit الدمج بأنه اجتاز CI مستقلاً. على فرع المشغّل المعزول، نجح تشغيل الاختبارات رقم [41596920011](https://github.com/m5moshbk/refactored-potato/actions/runs/41596920011) بتاريخ 2026-11-03، وشملت الخطوات تثبيت الاعتماديات وتشغيل `pytest` على `inventory_api/tests`.
- **PR #23:** [M5mOsH Autonomous Operator guardrails](https://github.com/m5moshbk/refactored-potato/pull/23) — مفتوح للمراجعة، غير مدمج؛ يستهدف فرع الخدمة. يجب عدم دمجه دون موافقة منفصلة لأن الفرع مرتبط بـ Render Auto-deploy.
- **الخصوصية:** يقبل API بيانات وصفية محدودة ويخزن ملخصات إجمالية فقط؛ لا يُفترض حفظ محتوى المصدر أو مسارات الملفات التفصيلية.
- **التخزين:** قاعدة SQLite الافتراضية تحت `/tmp/nexus_inventory.sqlite3` مؤقتة؛ استمرارية البيانات بعد إعادة التشغيل أو النشر غير مضمونة دون إعداد تخزين دائم والتحقق منه.
- **الأسرار:** التطبيق يتطلب `INGEST_TOKEN` لإدخال البيانات. لم تُقرأ قيمة السر ولم يتم التحقق من وجوده في Render ضمن هذا التحديث.

### المتبقي قبل أي تغيير إنتاجي

1. مراجعة سياسة التخزين الدائم وخياراته؛ لا تغيّر قاعدة البيانات أو القرص دون موافقة منفصلة.
2. التحقق من وجود إعداد `INGEST_TOKEN` دون كشف قيمته، عند توفر مراجعة إعدادات مصرح بها.
3. اختبار استجابة HTTP الفعلية ونقطة `/api/v1/status` بأداة وصول مناسبة؛ تعذر تأكيد الاستجابة الحية في فحص المتصفح الحالي.
4. مراجعة PR #23؛ لا دمج ولا نشر دون موافقة منفصلة.

## English

- **Repository:** `m5moshbk/refactored-potato`.
- **Service branch:** `feature/nexus-code-inventory-sync`.
- **Service:** [m5mosh-nexus-inventory-api](https://m5mosh-nexus-inventory-api.onrender.com).
- **Confirmed Render metadata:** the service is not suspended and has Auto-deploy enabled for its service branch. The latest deployment visible in Render's deployment list completed as `live` on commit `c6d9674d84dbc46b04ab2d0f2a3cac045ac944f7` at 2026-11-03 03:10:42 UTC.
- **PR #9:** [Fix Nexus inventory API path validation and add tests](https://github.com/m5moshbk/refactored-potato/pull/9) — merged on 2026-11-02; merge commit `c6d9674d84dbc46b04ab2d0f2a3cac045ac944f7`. The previous open/not-merged statement was stale.
- **Merged changes:** stricter normalized relative-path validation, rejection of Windows absolute paths and boolean file sizes, API regression tests, CI workflow, and bilingual documentation.
- **Tests:** the historical PR #9 record reports a successful CI run on an earlier branch head. The current GitHub query for the merge commit returned no check runs or status contexts, so this document does not claim an independently verified CI result for the merge commit. On the isolated operator branch, [GitHub Actions run #41596920011](https://github.com/m5moshbk/refactored-potato/actions/runs/41596920011) completed successfully on 2026-11-03; its steps included dependency installation and `pytest` for `inventory_api/tests`.
- **PR #23:** [M5mOsH Autonomous Operator guardrails](https://github.com/m5moshbk/refactored-potato/pull/23) — open for review, not merged; it targets the service branch. Do not merge without separate approval because Render Auto-deploy watches that branch.
- **Privacy:** the API accepts limited metadata and stores aggregate summaries only; detailed source contents and file paths are not intended to be retained.
- **Storage:** the default SQLite database at `/tmp/nexus_inventory.sqlite3` is ephemeral; persistence across restarts or deployments is not guaranteed without a separately verified persistent-storage configuration.
- **Secrets:** the application requires `INGEST_TOKEN` for ingestion. Its value was not read, and its presence in Render was not verified in this update.

### Remaining before any production change

1. Review persistent-storage options; do not change the database or disk without separate approval.
2. Verify whether `INGEST_TOKEN` is configured without revealing its value, when an authorized configuration review is available.
3. Verify live HTTP responses and `/api/v1/status` using a suitable access method; the current browser check could not confirm live responses.
4. Review PR #23; no merge or deployment without separate approval.

## الحقوق | Rights

© M5mOsH All Rights Reserved
