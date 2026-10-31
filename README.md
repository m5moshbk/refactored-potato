# M5mOsH Voice Nexus

M5mOsH Voice Nexus هو مشروع عربي ذكي يركّز على الصوت والهوية والتفاعل الرقمي الآمن. يهدف إلى تحويل الكلام إلى نص، ودعم الأشخاص البكم أو ذوي صعوبات النطق، مع تمكين التحقق الآمن عبر بصمة الصوت.

## الفكرة الأساسية
الوقت الحالي يتطلب منصات ذكية أكثر شمولية. الصوت ليس مجرد وسيلة للتواصل، بل هو هوية، أمان، وتقارب إنساني.

## الهدف
- تحويل الصوت إلى نص
- دعم التواصل الصوتي
- التحقق الآمن عبر الصوت
- دعم الأشخاص ذوي صعوبات النطق
- بناء منصة قابلة للتوسع في التعليم، الصحة، والخدمات

## مشروع تجريبي داخل هذا المستودع
- ملف صفحة العرض: `m5mosh-voice-nexus.html`
- ملف الوصف: `M5mOsH-Voice-Nexus.md`
- ملف الحزمة البصرية: `M5mOsH-Complete-Brand-Pack.md`
- مشروع تجريبي كامل داخل `sada-voice/`

## الهوية
- الاسم الرسمي: M5mOsH Voice Nexus
- الاسم العربي: صدى الحرف
- الشعار: Voice • Identity • Access • Future
- الملكية: © M5mOsH — All rights reserved

## التشغيل السريع
### قاعدة البيانات
```bash
docker-compose up -d
```

### Backend
```bash
cd sada-voice/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd sada-voice/frontend
npm install
npm run dev
```

## متغيرات البيئة
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/sada_voice
SECRET_KEY=change-me
JWT_ALGORITHM=HS256
OPENAI_API_KEY=
GEMINI_API_KEY=
AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## الخلاصة
هذا المشروع يجمع بين الصوت، الهوية، والأمان، ويشكل قاعدة قوية لمنصة عربية ذكية متكاملة قادرة على خدمة الإنسان والقطاع المؤسسي.

© M5mOsH — All rights reserved
