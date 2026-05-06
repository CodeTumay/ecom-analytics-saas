"use client";

import { api } from "@/lib/api";
import { LanguageToggle } from "@/components/LanguageToggle";
import { useLanguage } from "@/lib/i18n";
import { BarChart3 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

export default function LoginPage() {
  const router = useRouter();
  const { language, setLanguage } = useLanguage();
  const t = {
    tr: {
      title: "E-commerce Analytics",
      subtitle: "Çalışma alanına giriş yap",
      email: "E-posta",
      password: "Şifre",
      submit: "Giriş yap",
      loading: "Giriş yapılıyor",
      create: "Hesap oluştur",
      error: "Giriş başarısız"
    },
    en: {
      title: "E-commerce Analytics",
      subtitle: "Sign in to your workspace",
      email: "Email",
      password: "Password",
      submit: "Sign in",
      loading: "Signing in",
      create: "Create account",
      error: "Login failed"
    }
  }[language];
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const token = await api.login(email, password);
      localStorage.setItem("token", token.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : t.error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-panel">
        <div className="brand">
          <BarChart3 size={30} color="#227c5c" />
          <h1>{t.title}</h1>
          <p>{t.subtitle}</p>
        </div>
        <div className="auth-language">
          <LanguageToggle language={language} onChange={setLanguage} />
        </div>
        <form className="form" onSubmit={submit}>
          <label className="field">
            <span>{t.email}</span>
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
          </label>
          <label className="field">
            <span>{t.password}</span>
            <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" required />
          </label>
          {error ? <span className="error">{error}</span> : null}
          <button className="primary-button" disabled={loading} type="submit">
            {loading ? t.loading : t.submit}
          </button>
          <Link className="muted" href="/register">{t.create}</Link>
        </form>
      </section>
    </main>
  );
}
