"use client";

import { Alerts } from "@/components/Alerts";
import { Charts } from "@/components/Charts";
import { FileUpload } from "@/components/FileUpload";
import { MappingForm } from "@/components/MappingForm";
import { ProductTable } from "@/components/ProductTable";
import { StatCard } from "@/components/StatCard";
import { Analysis, AnalysisResponse, api } from "@/lib/api";
import { BarChart3, Clock3, LogOut, UploadCloud } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0
});

function isFullAnalysis(value: AnalysisResponse["analysis"]): value is Analysis {
  return Boolean(value && "totals" in value);
}

export default function DashboardPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [dashboard, setDashboard] = useState<Awaited<ReturnType<typeof api.dashboard>>>();
  const [analysisResponse, setAnalysisResponse] = useState<AnalysisResponse>();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const analysis = isFullAnalysis(analysisResponse?.analysis) ? analysisResponse.analysis : undefined;
  const totals = analysis?.totals || dashboard?.totals;

  const uploadStatus = useMemo(() => {
    if (!analysisResponse) return "";
    if (analysisResponse.status === "completed") return "Completed";
    if (analysisResponse.status === "needs_mapping") return "Needs mapping";
    if (analysisResponse.status === "failed") return "Failed";
    return "Processing";
  }, [analysisResponse]);

  async function loadDashboard(activeToken: string) {
    const data = await api.dashboard(activeToken);
    setDashboard(data);
  }

  async function pollAnalysis(activeToken: string, uploadId: number) {
    for (let attempt = 0; attempt < 60; attempt += 1) {
      const response = await api.analysis(activeToken, uploadId);
      setAnalysisResponse(response);
      if (["completed", "needs_mapping", "failed"].includes(response.status)) {
        return;
      }
      await new Promise((resolve) => setTimeout(resolve, 1500));
    }
  }

  useEffect(() => {
    const stored = localStorage.getItem("token");
    if (!stored) {
      router.push("/login");
      return;
    }
    setToken(stored);
    loadDashboard(stored).catch((err) => {
      setError(err instanceof Error ? err.message : "Could not load dashboard");
      if (err instanceof Error && err.message.includes("validate credentials")) {
        localStorage.removeItem("token");
        router.push("/login");
      }
    });
  }, [router]);

  async function uploadFile(file: File) {
    if (!token) return;
    setBusy(true);
    setError("");
    try {
      const upload = await api.upload(token, file);
      await pollAnalysis(token, upload.id);
      await loadDashboard(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  async function saveMapping(mapping: Record<string, string>) {
    if (!token || !analysisResponse) return;
    setBusy(true);
    setError("");
    try {
      await api.saveMapping(token, analysisResponse.upload_id, mapping);
      await pollAnalysis(token, analysisResponse.upload_id);
      await loadDashboard(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Mapping failed");
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    localStorage.removeItem("token");
    router.push("/login");
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="brand">
            <BarChart3 size={30} />
            <strong>Ecom Analytics</strong>
            <span>{dashboard?.plan === "pro" ? "Pro" : "Free"} plan</span>
          </div>
          <nav className="nav">
            <a className="active" href="/dashboard"><BarChart3 size={17} />Dashboard</a>
          </nav>
        </div>
        <div className="sidebar-meta">
          {dashboard?.usage.uploads_this_month ?? 0} uploads this month
        </div>
      </aside>

      <section className="content">
        <div className="topbar">
          <div className="page-title">
            <h1>Marketplace Profitability</h1>
            <p>{uploadStatus || "Ready"}</p>
          </div>
          <button className="ghost-button" type="button" onClick={logout}>
            <LogOut size={17} />
            Sign out
          </button>
        </div>

        {error ? <div className="alert critical"><strong>{error}</strong></div> : null}

        <div className="grid stats">
          <StatCard label="Revenue" value={money.format(totals?.revenue || 0)} />
          <StatCard label="Profit" value={money.format(totals?.profit || 0)} negative={(totals?.profit || 0) < 0} />
          <StatCard label="Ads Spend" value={money.format(totals?.ads_spend || 0)} />
          <StatCard label="Margin" value={`${analysis?.totals.margin ?? 0}%`} negative={(analysis?.totals.margin || 0) < 0} />
        </div>

        <div className="grid workspace">
          <div className="grid">
            <section className="panel">
              <div className="panel-header">
                <h2>Upload</h2>
                {busy ? <span className="status"><Clock3 size={13} /> Processing</span> : null}
              </div>
              <FileUpload disabled={busy} onFile={uploadFile} />
            </section>

            {analysisResponse?.status === "needs_mapping" ? (
              <MappingForm response={analysisResponse} onSubmit={saveMapping} />
            ) : null}

            <Charts analysis={analysis} />

            <section className="panel">
              <div className="panel-header">
                <h2>Products</h2>
              </div>
              <ProductTable products={analysis?.products || []} />
            </section>
          </div>

          <div className="grid">
            <section className="panel">
              <div className="panel-header">
                <h2>Insights</h2>
              </div>
              <Alerts insights={analysis?.insights || []} />
            </section>

            <section className="panel">
              <div className="panel-header">
                <h2>Uploads</h2>
                <UploadCloud size={18} />
              </div>
              <div className="upload-list">
                {(dashboard?.recent_uploads || []).map((upload) => (
                  <button
                    className="upload-item"
                    key={upload.id}
                    type="button"
                    onClick={() => token && pollAnalysis(token, upload.id)}
                  >
                    <span>{upload.filename}</span>
                    <span className="status">{upload.status}</span>
                  </button>
                ))}
              </div>
            </section>
          </div>
        </div>
      </section>
    </main>
  );
}
