"use client";

import { useState } from "react";

export default function HomePage() {
  const [mode, setMode] = useState<"login" | "signup">("signup");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loggedIn, setLoggedIn] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [transcript, setTranscript] = useState("");

  const handleAuth = async () => {
    const endpoint = mode === "signup"
      ? "http://localhost:8000/api/v1/signup"
      : "http://localhost:8000/api/v1/login";

    const payload = mode === "signup"
      ? { email, full_name: fullName, password }
      : { email, password };

    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (data.access_token) {
      setLoggedIn(true);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://localhost:8000/api/v1/transcribe", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setTranscript(data.transcript || "لا يوجد نص");
  };

  if (!loggedIn) {
    return (
      <main className="min-h-screen bg-slate-950 text-white p-8">
        <div className="max-w-md mx-auto bg-slate-900 p-8 rounded-2xl shadow-xl">
          <h1 className="text-4xl font-bold mb-6">صدى الحرف</h1>

          <div className="flex gap-3 mb-6">
            <button
              onClick={() => setMode("signup")}
              className={`flex-1 p-3 rounded-lg ${mode === "signup" ? "bg-indigo-600" : "bg-slate-700"}`}
            >
              تسجيل جديد
            </button>
            <button
              onClick={() => setMode("login")}
              className={`flex-1 p-3 rounded-lg ${mode === "login" ? "bg-indigo-600" : "bg-slate-700"}`}
            >
              تسجيل دخول
            </button>
          </div>

          {mode === "signup" && (
            <input
              placeholder="الاسم الكامل"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full mb-3 p-3 rounded-lg bg-slate-800 border border-slate-700"
            />
          )}

          <input
            placeholder="البريد الإلكتروني"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full mb-3 p-3 rounded-lg bg-slate-800 border border-slate-700"
          />

          <input
            type="password"
            placeholder="كلمة المرور"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full mb-4 p-3 rounded-lg bg-slate-800 border border-slate-700"
          />

          <button
            onClick={handleAuth}
            className="w-full bg-indigo-600 hover:bg-indigo-500 p-3 rounded-lg font-semibold"
          >
            {mode === "signup" ? "إنشاء الحساب" : "تسجيل الدخول"}
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-5xl font-bold mb-4">صدى الحرف</h1>
        <p className="text-slate-300 text-lg mb-8">
          منصة صوتية ذكية لدعم التواصل، التحقق الصوتي، والهوية الرقمية.
        </p>

        <div className="bg-slate-900 rounded-2xl p-6">
          <input
            type="file"
            accept="audio/*"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm text-slate-200 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-500 file:text-white hover:file:bg-indigo-400"
          />

          <button
            onClick={handleUpload}
            className="mt-4 bg-indigo-600 px-4 py-2 rounded-lg hover:bg-indigo-500"
          >
            تحويل الصوت إلى نص
          </button>
        </div>

        <div className="mt-8 bg-slate-900 p-6 rounded-2xl">
          <h2 className="text-2xl font-semibold mb-2">النص:</h2>
          <p className="text-slate-200 whitespace-pre-wrap">
            {transcript || "لم يتم تحويل أي ملف بعد."}
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
          {['نعم', 'لا', 'أحتاج مساعدة', 'أريد الطبيب'].map((item) => (
            <button key={item} className="bg-slate-800 hover:bg-slate-700 p-4 rounded-xl">
              {item}
            </button>
          ))}
        </div>
      </div>
    </main>
  );
}
