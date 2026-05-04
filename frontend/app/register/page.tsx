"use client";

import { api } from "@/lib/api";
import { BarChart3 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.register(email, password);
      const token = await api.login(email, password);
      localStorage.setItem("token", token.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-panel">
        <div className="brand">
          <BarChart3 size={30} color="#227c5c" />
          <h1>Create workspace</h1>
          <p>Free plan includes 1 upload per month</p>
        </div>
        <form className="form" onSubmit={submit}>
          <label className="field">
            <span>Email</span>
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
          </label>
          <label className="field">
            <span>Password</span>
            <input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              minLength={8}
              required
            />
          </label>
          {error ? <span className="error">{error}</span> : null}
          <button className="primary-button" disabled={loading} type="submit">
            {loading ? "Creating" : "Create account"}
          </button>
          <Link className="muted" href="/login">Already have an account</Link>
        </form>
      </section>
    </main>
  );
}
