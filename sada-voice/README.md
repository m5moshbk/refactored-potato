# M5mOsH Voice Nexus | صدى الحرف

**Voice • Identity • Access • Future**

> صوتك هو هويتك. اتصالك هو قوتك.

**Owner:** M5mOsH  
**Project status:** Prototype / MVP Foundation — Under Development  
**Rights:** © M5mOsH All Rights Reserved

---

## 🇸🇦 العربية

### نبذة عن المشروع

صدى الحرف — M5mOsH Voice Nexus: مشروع تقني عربي يهدف إلى تطوير التواصل الصوتي وتحويل الكلام إلى نص، واستكشاف تقنيات الهوية الصوتية وإمكانية الوصول، ضمن بنية قابلة للتوسع.

يهدف المشروع إلى بناء أساس تقني يمكن تطويره لدعم التواصل الرقمي وتحسين الوصول إلى الخدمات الصوتية، مع استكشاف حلول تخدم الأشخاص الذين يواجهون صعوبات في التواصل.

### البنية والمكونات الموجودة في النموذج

- **Speech-to-Text:** مسار لتحويل الصوت إلى نص باستخدام OpenAI API عند توفر مفتاح الخدمة.
- **Voiceprint Prototype:** إنشاء بصمة SHA-256 لبايتات الملف الصوتي.
- **Verification:** مقارنة بصمات الملفات الصوتية.
- **Authentication:** مسارات أولية للتسجيل وتسجيل الدخول باستخدام bcrypt وJWT.
- **Backend:** مبني باستخدام FastAPI.
- **Frontend:** مبني باستخدام Next.js.

وجود هذه المكونات في الشيفرة لا يعني أن جميعها اجتازت اختبارات متكاملة أو أنها جاهزة للاستخدام الإنتاجي.

### واجهات API الموثقة

| المسار | الوظيفة المعلنة |
|---|---|
| `GET /health` | فحص صحة الخدمة |
| `POST /api/v1/transcribe` | تحويل الصوت إلى نص |
| `POST /api/v1/voiceprint` | إنشاء بصمة ملف صوتي |
| `POST /api/v1/verify` | مقارنة البصمات |
| `POST /api/v1/signup` | إنشاء حساب |
| `POST /api/v1/login` | تسجيل الدخول |

هذه المسارات موثقة في المشروع؛ ولم يتم توثيق اجتيازها جميعاً لاختبارات تشغيل متكاملة.

### التشغيل المحلي

#### 1. قاعدة البيانات

من جذر المشروع الذي يحتوي ملف `docker-compose.yml`:

```bash
docker-compose up -d
```

#### 2. Backend

```bash
cd sada-voice/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Frontend

```bash
cd sada-voice/frontend
npm install
npm run dev
```

راجع ملفات الإعداد ومتطلبات البيئة في المشروع قبل التشغيل. لا تضع مفاتيح API أو كلمات المرور أو بيانات الاتصال في المستودع.

### حدود تقنية معروفة

- استخدام SHA-256 لمقارنة الملفات لا يمثل نظاماً حقيقياً للتعرف البيومتري على المتحدث؛ إنه تطابق لبصمة الملف نفسه.
- عند غياب مفتاح OpenAI، يحتوي مسار تحويل الصوت إلى نص على استجابة تجريبية ثابتة.
- قيم الثقة الظاهرة في بعض أجزاء النموذج ليست نتائج قياس أو Benchmark موثقة.
- لا توجد أدلة كافية هنا لإثبات الجاهزية الإنتاجية أو دقة التعرف أو مستوى الأمان التشغيلي.
- يلزم إجراء اختبارات وظيفية وأمنية وخصوصية قبل استخدام بيانات صوتية حقيقية على نطاق واسع.

### الخصوصية والأمان

قد تتضمن البيانات الصوتية معلومات شخصية حساسة. يجب أن يعتمد أي تشغيل مستقبلي على موافقة واضحة، وتقليل البيانات، والتحكم في الوصول، والتخزين الآمن، وسياسة احتفاظ وحذف محددة.

لا تستخدم هذا النموذج كنظام إنتاجي للمصادقة البيومترية قبل إجراء تقييم مستقل للأمان والدقة والامتثال.

### خارطة التطوير المقترحة

1. تحسين تحويل الكلام العربي إلى نص وقياس جودة النتائج.
2. تقييم نماذج مناسبة للتعرف على المتحدث عبر اختبارات مستقلة.
3. توسيع دعم التواصل وإمكانية الوصول.
4. إضافة إدارة آمنة للموافقات والبيانات الصوتية.
5. بناء اختبارات تلقائية ونشر نتائج قابلة للتحقق.
6. إعداد بنية تشغيل ومراقبة مناسبة قبل أي إطلاق إنتاجي.

هذه أهداف تطوير مقترحة وليست ادعاءً بأن الميزات مكتملة حالياً.

---

## 🇬🇧 English

### Project Overview

M5mOsH Voice Nexus — An Arabic-first voice technology project exploring speech-to-text, voice identity, and accessible digital communication through an extensible software architecture.

The project aims to establish a technical foundation for improving digital communication and exploring accessible voice-based experiences.

### Existing Prototype Components

- **Speech-to-Text:** An integration path using the OpenAI API when credentials are available.
- **Voiceprint Prototype:** SHA-256 hashing of audio-file bytes.
- **Verification:** Exact hash comparison between audio files.
- **Authentication:** Initial signup and login routes using bcrypt and JWT.
- **Backend:** FastAPI.
- **Frontend:** Next.js.

The presence of these components in the source code does not establish complete test coverage or production readiness.

### Documented API Routes

| Endpoint | Documented purpose |
|---|---|
| `GET /health` | Service health check |
| `POST /api/v1/transcribe` | Speech-to-text |
| `POST /api/v1/voiceprint` | Generate an audio-file hash |
| `POST /api/v1/verify` | Compare audio hashes |
| `POST /api/v1/signup` | Account registration |
| `POST /api/v1/login` | User authentication |

These routes are documented in the project. Full integration-test results have not been established.

### Local Development

#### 1. Database

From the project root containing `docker-compose.yml`:

```bash
docker-compose up -d
```

#### 2. Backend

```bash
cd sada-voice/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Frontend

```bash
cd sada-voice/frontend
npm install
npm run dev
```

Review the project's environment configuration before running it. Never commit API keys, passwords, or connection credentials.

### Known Technical Limitations

- SHA-256 file hashing is not biometric speaker recognition; it checks whether file hashes match.
- The speech-to-text path includes a fixed demo response when an OpenAI API key is unavailable.
- Confidence values shown in parts of the prototype are not verified measurement or benchmark results.
- Production readiness, recognition accuracy, and operational security have not been established.
- Further functional, security, and privacy testing is required before handling real-world audio data at scale.

### Privacy & Security

Voice data may contain sensitive personal information. Any future deployment should establish clear consent, data minimization, access controls, secure storage, and defined retention and deletion policies.

Do not use this prototype as a production biometric authentication system without an independent security and accuracy assessment.

### Proposed Roadmap

1. Improve Arabic speech-to-text and measure transcription quality.
2. Evaluate suitable speaker-recognition models through independent testing.
3. Expand accessibility and communication support.
4. Implement secure consent and audio-data handling.
5. Add automated tests and publish verifiable results.
6. Establish production-grade deployment and monitoring practices.

These are proposed development goals, not claims of completed functionality.

---

## Ownership & Rights

**M5mOsH**  
© M5mOsH All Rights Reserved
