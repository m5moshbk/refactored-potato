# صدى الحرف

منصة ذكية للتواصل الصوتي، التحقق الصوتي، ودعم الأشخاص البكم أو ذوي صعوبات النطق.

## الهدف
- تحويل الكلام إلى نص
- دعم التواصل الصوتي
- التحقق الآمن عبر الصوت
- إنشاء بصمة صوتية
- واجهة عربية سهلة
- توسيع المشروع إلى مؤسسات ومراكز صحية وتعليمية

## المشروع التجريبي داخل المستودع
تم إضافة مشروع تجريبي جديد داخل مجلد `sada-voice/` مع واجهة Next.js وبنية FastAPI.

- [دليل المشروع](sada-voice/README.md)
- [الخادم](sada-voice/backend)
- [الواجهة الأمامية](sada-voice/frontend)

## التشغيل السريع

### 1) قاعدة البيانات
```bash
docker-compose up -d
```

### 2) Backend
```bash
cd sada-voice/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3) Frontend
```bash
cd sada-voice/frontend
npm install
npm run dev
```

## APIs الأساسية
- GET /health
- POST /api/v1/transcribe
- POST /api/v1/voiceprint
- POST /api/v1/verify
- POST /api/v1/signup
- POST /api/v1/login

## المراحل
1. صوت إلى نص
2. بصمة صوتية
3. تسجيل دخول صوتي
4. لوحة إدارة
5. التوسع إلى المؤسسات
6. التطوير الذاتي

## ملاحظة
هذا هو إطلاق أولي تجريبي، مصمم ليعمل محليًا للتطوير والاختبار قبل التوسع إلى بيئة إنتاج أو خدمة Render.
