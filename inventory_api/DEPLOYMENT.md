# دليل نشر Nexus Inventory API | Nexus Inventory API Deployment Guide

## العربية — بوابة الموافقة قبل النشر

هذه الواجهة منفصلة عمدًا عن موقع Nexus الثابت. لا تربط نطاقًا مخصصًا ولا تغيّر خدمة Nexus الحالية قبل مراجعة مستقلة.

1. أنشئ خدمة Render منفصلة من المستودع والفرع المقصودين.
2. اجعل Root Directory جذر المستودع.
3. أمر البناء: `pip install -r inventory_api/requirements.txt`.
4. أمر التشغيل: `gunicorn -w 1 -b 0.0.0.0:$PORT inventory_api.app:app`.
5. اضبط `INGEST_TOKEN` كسر طويل وعشوائي من Render Environment؛ لا تحفظه في المستودع ولا تشاركه في المحادثات.
6. يمكن ضبط `INVENTORY_DB_PATH` إلى مسار على قرص دائم. من دون قرص دائم، قد تضيع قاعدة SQLite الموجودة في `/tmp` عند إعادة التشغيل.
7. تحقق من `/healthz` و`/api/v1/status`، ثم اختبر إدخال بيانات وصفية بمفتاح تجريبي فقط.
8. لا تدمج هذا الفرع ولا تنشره على الخدمة الحية حتى تنجح الاختبارات وتُراجع إعدادات الأسرار والتخزين.

## English — Release approval gate

This API is intentionally separate from the existing static Nexus site. Do not attach a custom domain or modify the current Nexus service without a separate review.

1. Create a separate Render web service from the intended repository and branch.
2. Set the root directory to the repository root.
3. Build command: `pip install -r inventory_api/requirements.txt`.
4. Start command: `gunicorn -w 1 -b 0.0.0.0:$PORT inventory_api.app:app`.
5. Set `INGEST_TOKEN` to a long random secret in Render Environment. Never commit or share it.
6. Optionally set `INVENTORY_DB_PATH` to a persistent-disk path. Without a persistent disk, SQLite under `/tmp` may be lost on restart.
7. Verify `/healthz` and `/api/v1/status`, then test metadata ingestion using a disposable test token only.
8. Do not merge this branch or deploy it to the live service until tests pass and secret/storage settings are reviewed.

## بصمة المشروع | Project fingerprint
- Owner: Ahmed jafari
- Signature / rights tag: M5mOsH
- Contact: +99507190799
