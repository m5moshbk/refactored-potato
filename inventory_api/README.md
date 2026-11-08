# Nexus Code Inventory API | واجهة فهرسة ملفات Nexus

## العربية

واجهة استقبال **بيانات وصفية مجمّعة فقط** من عميل فهرسة Pythonista. لا يُرفع محتوى الملفات أو مساراتها أو أسماؤها الأصلية.

### الواجهات
- `POST /api/v1/inventory`: يتطلب `Authorization: Bearer <INGEST_TOKEN>`.
- `GET /api/v1/status`: ملخص إجمالي فقط.
- `GET /healthz`: فحص صحة الخدمة.

### ضوابط البيانات والأمان
- قائمة سماح لامتدادات الملفات.
- عميل Pythonista يولّد معرفات اصطناعية مثل `aggregate/item_00001.py` قبل الإرسال.
- لا يرسل العميل المسارات الأصلية أو أسماء الملفات أو أحجامها أو أوقات تعديلها.
- رفض الحقول غير المتوقعة، والمسارات المطلقة أو غير المعيارية، ومحاولات اجتياز المسارات.
- تخزين الأعداد الإجمالية فقط؛ لا تُخزَّن مسارات الملفات أو محتويات المصدر.
- يرفض العميل تحويلات HTTP redirects حتى لا يُعاد توجيه ترويسة Bearer إلى مضيف آخر.
- اضبط `INGEST_TOKEN` في بيئة الخدمة، ولا تضعه في GitHub أو في الواجهة الأمامية.
- قاعدة SQLite الافتراضية `/tmp/nexus_inventory.sqlite3` مؤقتة وقد تفقد البيانات عند إعادة التشغيل أو النشر.

### التشغيل
من جذر المستودع:

```bash
python -m pip install -r inventory_api/requirements.txt
python -m pytest -q inventory_api/tests
gunicorn -w 1 -b 0.0.0.0:$PORT inventory_api.app:app
```

راجع [DEPLOYMENT.md](DEPLOYMENT.md) و[STATUS.md](STATUS.md) قبل النشر. نجاح `/healthz` لا يثبت نجاح مزامنة Pythonista.

## English

The Nexus Code Inventory API accepts **aggregate metadata only** from the Pythonista inventory client. Original file contents, paths, and filenames are not uploaded.

### Endpoints
- `POST /api/v1/inventory`: requires `Authorization: Bearer <INGEST_TOKEN>`.
- `GET /api/v1/status`: aggregate summary only.
- `GET /healthz`: service health check.

### Data and security controls
- File extensions are allow-listed.
- The Pythonista client generates synthetic identifiers such as `aggregate/item_00001.py` before transmission.
- Original paths, filenames, file sizes, and modification timestamps are not sent.
- The API rejects unexpected fields, absolute/non-normalized paths, and path traversal.
- Only aggregate counts are stored; source contents and file paths are not persisted.
- The client rejects HTTP redirects so the Bearer authorization header is not forwarded to another host.
- Set `INGEST_TOKEN` in the service environment. Never commit it or expose it in frontend code.
- The default SQLite database at `/tmp/nexus_inventory.sqlite3` is ephemeral and may be lost on restart or deployment.

### Run locally
From the repository root:

```bash
python -m pip install -r inventory_api/requirements.txt
python -m pytest -q inventory_api/tests
gunicorn -w 1 -b 0.0.0.0:$PORT inventory_api.app:app
```

Review [DEPLOYMENT.md](DEPLOYMENT.md) and [STATUS.md](STATUS.md) before deployment. A successful `/healthz` response does not prove a successful Pythonista sync.

## الحقوق | Rights
© M5mOsH — All rights reserved.
