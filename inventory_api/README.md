# Nexus Code Inventory API | واجهة فهرسة ملفات Nexus

## العربية

واجهة استقبال **بيانات وصفية فقط** من عميل فهرسة Pythonista. لا يُفترض رفع محتوى الملفات أو مساراتها التفصيلية إلى الخادم.

### الواجهات
- `POST /api/v1/inventory`: يتطلب `Authorization: Bearer <INGEST_TOKEN>`.
- `GET /api/v1/status`: ملخص إجمالي فقط.
- `GET /healthz`: فحص صحة الخدمة.

### ضوابط البيانات والأمان
- قائمة سماح لامتدادات الملفات.
- رفض الحقول غير المتوقعة، والمسارات المطلقة أو غير المعيارية، ومحاولات اجتياز المسارات.
- رفض أحجام الملفات التي ليست أعدادًا صحيحة غير سالبة، بما فيها القيم المنطقية.
- تخزين الأعداد الإجمالية فقط؛ لا تُخزَّن مسارات الملفات أو محتويات المصدر.
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

The Nexus Code Inventory API accepts **metadata-only** summaries from the Pythonista inventory client. It is not intended to upload source contents or retain detailed file paths.

### Endpoints
- `POST /api/v1/inventory`: requires `Authorization: Bearer <INGEST_TOKEN>`.
- `GET /api/v1/status`: aggregate summary only.
- `GET /healthz`: service health check.

### Data and security controls
- Allow-listed file extensions.
- Rejects unexpected fields, absolute/non-normalized paths, and path traversal.
- Rejects file sizes that are not non-negative integers, including booleans.
- Stores aggregate counts only; source contents and detailed paths are not persisted.
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

## بصمة المشروع | Project fingerprint
- Owner: Ahmed jafari
- Signature / rights tag: M5mOsH
- Contact: +99507190799
