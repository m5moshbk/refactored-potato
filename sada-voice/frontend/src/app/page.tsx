"use client";

import { useRef, useState } from "react";

type SpeechAlternative = { transcript: string };
type SpeechResult = ArrayLike<SpeechAlternative>;
type SpeechEvent = { results: ArrayLike<SpeechResult> };
type SpeechErrorEvent = { error: string };
type SpeechRecognitionLike = {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((event: SpeechEvent) => void) | null;
  onerror: ((event: SpeechErrorEvent) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
};
type SpeechWindow = Window & {
  SpeechRecognition?: new () => SpeechRecognitionLike;
  webkitSpeechRecognition?: new () => SpeechRecognitionLike;
};

const API_URL = (
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "development" ? "http://localhost:8000" : "")
).replace(/\/+$/, "");

const phrases = [
  "نعم",
  "لا",
  "أحتاج مساعدة",
  "أريد التحدث مع شخص",
  "أحتاج إلى استراحة",
  "شكرًا لك",
];

export default function HomePage() {
  const [mode, setMode] = useState<"signup" | "login">("signup");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [authMessage, setAuthMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [consent, setConsent] = useState(false);
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [speechMessage, setSpeechMessage] = useState("");
  const [spokenText, setSpokenText] = useState("");
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);

  async function handleAuth() {
    if (!API_URL) {
      setAuthMessage("عنوان API غير مضبوط. أضف NEXT_PUBLIC_API_URL إلى إعدادات الواجهة ثم أعد البناء.");
      return;
    }
    setBusy(true);
    setAuthMessage("");
    try {
      const response = await fetch(`${API_URL}/api/v1/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(
          mode === "signup"
            ? { email, full_name: fullName, password }
            : { email, password }
        ),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "تعذر إتمام الطلب.");
      setToken(data.access_token);
      setAuthMessage("تم تسجيل الدخول. الرمز محفوظ في ذاكرة الصفحة فقط.");
    } catch (error) {
      setAuthMessage(error instanceof Error ? error.message : "حدث خطأ غير متوقع.");
    } finally {
      setBusy(false);
    }
  }

  function startListening() {
    if (!consent) {
      setSpeechMessage("يرجى الموافقة أولًا على استخدام الميكروفون ومعالجة الكلام عبر المتصفح.");
      return;
    }
    const speechWindow = window as SpeechWindow;
    const Recognition = speechWindow.SpeechRecognition || speechWindow.webkitSpeechRecognition;
    if (!Recognition) {
      setSpeechMessage("التعرف على الكلام غير مدعوم في هذا المتصفح. يمكنك استخدام لوحة العبارات والكتابة.");
      return;
    }
    const recognition = new Recognition();
    recognition.lang = "ar-SA";
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.onresult = (event) => {
      const parts: string[] = [];
      for (let i = 0; i < event.results.length; i += 1) {
        parts.push(event.results[i][0].transcript);
      }
      setTranscript(parts.join(" "));
    };
    recognition.onerror = (event) => {
      setSpeechMessage(`تعذر التعرف على الكلام: ${event.error}`);
      setListening(false);
    };
    recognition.onend = () => setListening(false);
    recognitionRef.current = recognition;
    try {
      recognition.start();
      setListening(true);
      setSpeechMessage("الميكروفون نشط بطلب منك. اضغط إيقاف عند الانتهاء.");
    } catch {
      setSpeechMessage("تعذر بدء الميكروفون. تحقق من إذن المتصفح ثم حاول مجددًا.");
    }
  }

  function stopListening() {
    recognitionRef.current?.stop();
    setListening(false);
  }

  function speak(text = spokenText) {
    if (!text.trim() || !("speechSynthesis" in window)) {
      setSpeechMessage("تحويل النص إلى صوت غير متاح في هذا المتصفح أو لا يوجد نص.");
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "ar-SA";
    window.speechSynthesis.speak(utterance);
  }

  function logout() {
    setToken("");
    setAuthMessage("تم إنهاء حالة الدخول في هذه الصفحة.");
  }

  return (
    <main className="shell">
      <nav className="topbar">
        <a className="brand" href="#" aria-label="صدى الحرف - الصفحة الرئيسية">
          <span className="brand-mark">ص</span>
          <span><strong>M5mOsH</strong><small>VOICE NEXUS</small></span>
        </a>
        <span className="top-tag">VOICE • IDENTITY • ACCESS • FUTURE</span>
      </nav>

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">منصة عربية للصوت والتواصل الشامل</p>
          <h1>صوتك يستحق أن <span>يُسمع.</span></h1>
          <p className="lead">
            صدى الحرف يجمع أدوات التواصل الصوتي وإمكانية الوصول في تجربة عربية
            واضحة، مع بناء آمن للهوية الرقمية دون ادعاءات بيومترية غير مثبتة.
          </p>
          <div className="hero-actions">
            <a className="primary-link" href="#workspace">ابدأ التجربة</a>
            <a className="secondary-link" href="#principles">مبادئ الأمان</a>
          </div>
          <div className="signal-row">
            <span><i className="signal-dot" /> واجهة عربية RTL</span>
            <span>خصوصية بموافقة واضحة</span>
            <span>لا تخزين صوت خام افتراضيًا</span>
          </div>
        </div>
        <div className="voice-orbit" aria-hidden="true">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="orbit-core"><span>ص</span><small>صدى الحرف</small></div>
          <div className="orbit-caption">VOICE / HUMAN / ACCESS</div>
        </div>
      </section>

      <section className="feature-grid" aria-label="قدرات المنصة">
        <article className="feature-card">
          <span className="feature-number">01</span>
          <h2>كلام إلى نص</h2>
          <p>استخدم التعرف الصوتي المدمج في المتصفح عندما يكون مدعومًا، مع إظهار حدود التوافق والخصوصية.</p>
        </article>
        <article className="feature-card">
          <span className="feature-number">02</span>
          <h2>نص إلى صوت</h2>
          <p>حوّل الرسائل المكتوبة إلى كلام باستخدام إمكانات النطق المتاحة على جهازك.</p>
        </article>
        <article className="feature-card">
          <span className="feature-number">03</span>
          <h2>تواصل بديل</h2>
          <p>لوحة عبارات سريعة قابلة للنطق لتسهيل التعبير عن الاحتياجات اليومية.</p>
        </article>
        <article className="feature-card muted-card">
          <span className="feature-number">04</span>
          <h2>الهوية الصوتية</h2>
          <p>ميزة قيد التطوير؛ التحقق البيومتري معطل حتى دمج نموذج مختبر ومقاومة انتحال وموافقة صريحة.</p>
        </article>
      </section>

      <section className="workspace" id="workspace">
        <div className="section-heading">
          <p className="eyebrow">مساحة التجربة</p>
          <h2>تواصل بالطريقة التي تناسبك</h2>
          <p>يمكنك تجربة أدوات المتصفح دون إنشاء حساب. الحساب مطلوب فقط للواجهات المحمية في الخادم.</p>
        </div>

        <div className="workspace-grid">
          <article className="panel speech-panel">
            <div className="panel-heading">
              <div><span className="panel-kicker">01 / SPEECH</span><h3>تحويل الكلام إلى نص</h3></div>
              <span className={listening ? "status live" : "status"}>{listening ? "يستمع الآن" : "متوقف"}</span>
            </div>
            <label className="consent-line">
              <input type="checkbox" checked={consent} onChange={(event) => setConsent(event.target.checked)} />
              <span>أوافق على استخدام الميكروفون. قد يعالج المتصفح الصوت عبر خدمة تابعة لمزوده؛ راجع سياسة الخصوصية لديه قبل المتابعة.</span>
            </label>
            <div className="button-row">
              <button className="button-primary" onClick={startListening} disabled={listening}>ابدأ الاستماع</button>
              <button className="button-quiet" onClick={stopListening} disabled={!listening}>إيقاف</button>
              <button className="button-quiet" onClick={() => setTranscript("")}>مسح النص</button>
            </div>
            <label className="field-label" htmlFor="transcript">النص الناتج</label>
            <textarea id="transcript" value={transcript} onChange={(event) => setTranscript(event.target.value)} placeholder="سيظهر النص هنا، ويمكنك تعديله..." rows={5} />
            <p className="helper" role="status">{speechMessage || "التعرف الصوتي يعتمد على دعم المتصفح واللغة وإعدادات الخصوصية لديه."}</p>
          </article>

          <article className="panel access-panel">
            <div className="panel-heading">
              <div><span className="panel-kicker">02 / ACCESS</span><h3>لوحة التواصل السريع</h3></div>
            </div>
            <p className="panel-intro">اختر عبارة لتظهر في مربع النص، ثم انطقها عند الحاجة.</p>
            <div className="phrase-grid">
              {phrases.map((phrase) => (
                <button key={phrase} className="phrase-button" onClick={() => setSpokenText(phrase)}>{phrase}</button>
              ))}
            </div>
            <label className="field-label" htmlFor="spokenText">اكتب رسالتك</label>
            <textarea id="spokenText" value={spokenText} onChange={(event) => setSpokenText(event.target.value)} placeholder="اكتب ما تريد قوله..." rows={3} />
            <button className="button-primary full-button" onClick={() => speak()}> <span aria-hidden="true">▶</span> نطق الرسالة</button>
          </article>
        </div>
      </section>

      <section className="account-section">
        <div className="section-heading">
          <p className="eyebrow">حساب المنصة</p>
          <h2>مساحة الحساب المحمية</h2>
          <p>إنشاء الحساب وتسجيل الدخول يحتاجان إعداد الخادم وقاعدة البيانات ومفتاح توقيع آمن.</p>
        </div>
        <div className="account-panel">
          {token ? (
            <div className="account-success">
              <div><strong>الجلسة نشطة</strong><p>رمز الدخول محفوظ في ذاكرة الصفحة فقط، ويُمسح عند إعادة التحميل أو إغلاق الصفحة.</p></div>
              <button className="button-quiet" onClick={logout}>تسجيل الخروج</button>
            </div>
          ) : (
            <>
              <div className="tabs">
                <button className={mode === "signup" ? "tab active" : "tab"} onClick={() => setMode("signup")}>إنشاء حساب</button>
                <button className={mode === "login" ? "tab active" : "tab"} onClick={() => setMode("login")}>تسجيل الدخول</button>
              </div>
              {mode === "signup" && <label className="field-label">الاسم<input value={fullName} onChange={(event) => setFullName(event.target.value)} autoComplete="name" /></label>}
              <label className="field-label">البريد الإلكتروني<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" /></label>
              <label className="field-label">كلمة المرور<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete={mode === "signup" ? "new-password" : "current-password"} /></label>
              <button className="button-primary full-button" onClick={handleAuth} disabled={busy || !email || !password || (mode === "signup" && password.length < 12)}>
                {busy ? "جارٍ الإرسال..." : mode === "signup" ? "إنشاء الحساب" : "دخول"}
              </button>
              {mode === "signup" && <p className="helper">استخدم كلمة مرور من 12 حرفًا على الأقل.</p>}
            </>
          )}
          {authMessage && <p className="notice" role="status">{authMessage}</p>}
        </div>
      </section>

      <section className="principles" id="principles">
        <div className="section-heading">
          <p className="eyebrow">الثقة أولًا</p>
          <h2>ما الذي لا ندّعيه؟</h2>
        </div>
        <div className="principle-list">
          <p><strong>لا تحقق بيومتري وهمي:</strong> تشابه ملفات الصوت أو تطابق بصمتها الرقمية لا يثبت هوية المتحدث.</p>
          <p><strong>لا تسجيل خفي:</strong> تشغيل الميكروفون يتطلب إجراءً واضحًا وموافقة المستخدم.</p>
          <p><strong>لا حفظ افتراضي للصوت:</strong> أدوات المتصفح هنا لا ترفع ملفات صوت إلى خادم المشروع.</p>
          <p><strong>لا جاهزية إنتاجية مزعومة:</strong> التكاملات الحساسة تظل معطلة حتى الاختبار والمراجعة المستقلة.</p>
        </div>
      </section>

      <footer className="footer">
        <div><strong>M5mOsH Voice Nexus</strong><p>الصوت ليس مجرد وسيلة للتواصل. إنه وسيلة للتعبير والوصول.</p></div>
        <span>© M5mOsH — All rights reserved</span>
      </footer>
    </main>
  );
}
