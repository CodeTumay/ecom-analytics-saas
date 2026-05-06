"use client";

import { Alerts } from "@/components/Alerts";
import { Charts } from "@/components/Charts";
import { FileUpload } from "@/components/FileUpload";
import { LanguageToggle } from "@/components/LanguageToggle";
import { MappingForm } from "@/components/MappingForm";
import { ProductTable } from "@/components/ProductTable";
import { StatCard } from "@/components/StatCard";
import { Analysis, AnalysisResponse, ReportDefinition, api } from "@/lib/api";
import { useLanguage } from "@/lib/i18n";
import {
  AlertTriangle,
  BarChart3,
  Boxes,
  Calculator,
  CircleDollarSign,
  ClipboardList,
  CreditCard,
  LineChart,
  LogOut,
  Megaphone,
  PackageSearch,
  Percent,
  Receipt,
  RotateCcw,
  ShoppingCart,
  Truck,
  UploadCloud,
  Users,
  Warehouse
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0
});

const percent = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 1,
  minimumFractionDigits: 0
});

const text = {
  tr: {
    app: "Ecom Analytics",
    plan: "plan",
    title: "E-ticaret Karlılık Merkezi",
    ready: "Hazır",
    completed: "Tamamlandı",
    needsMapping: "Kolon eşleştirme gerekli",
    failed: "Başarısız",
    processing: "İşleniyor",
    signOut: "Çıkış yap",
    uploadsThisMonth: "bu ay yükleme",
    revenue: "Ciro",
    profit: "Net Kar",
    adsSpend: "Reklam Harcaması",
    margin: "Kar Marjı",
    totalCosts: "Toplam Gider",
    contribution: "Katkı Karı",
    lossProducts: "Zarardaki Ürün",
    averageOrderProfit: "Ortalama Sipariş Karı",
    upload: "Dosya Yükle",
    uploadHelp: "Excel/CSV dosyanı yükle. Sistem ayraç, sayı formatı ve kolonları otomatik algılar.",
    uploadGuide: "Otomatik Analiz İçin Başlıklar",
    sample: "Örnek CSV indir",
    required: "Zorunlu",
    optional: "Opsiyonel",
    acceptedNames: "Kabul edilen başlık örnekleri",
    products: "Ürünler",
    insights: "AI İçgörüler",
    uploads: "Yüklemeler",
    reports: "Raporlar",
    reportMap: "E-ticaret Rapor Haritası",
    reportMapHelp: "Sol menüde tüm ana rapor başlıkları yer alır; veri geldikçe ilgili raporlar otomatik dolar.",
    financial: "Finansal Raporlar",
    performance: "Performans Raporları",
    operations: "Operasyon Raporları",
    growth: "Büyüme ve Risk",
    available: "Aktif",
    planned: "Planlandı",
    noData: "Veri bekleniyor",
    summary: "Özet",
    currentUpload: "Mevcut analiz",
    reportCards: "Kapsamlı Rapor Özeti",
    reportType: "Rapor tipi",
    selectReportType: "Yüklenecek rapor tipini seç",
    combineReports: "Genel rapor oluştur",
    selectedReports: "seçili rapor",
    generalReport: "Genel Birleşik Rapor",
    clearGeneralReport: "Genel raporu kapat",
    completedOnly: "Sadece tamamlanan raporlar seçilebilir",
    costBreakdown: "Maliyet Kırılımı",
    topProducts: "En Karlı Ürünler",
    lossMakers: "Zarar Eden Ürünler",
    adRatio: "Reklam/Ciro",
    shippingRatio: "Kargo/Ciro",
    commissionRatio: "Komisyon/Ciro",
    profitableProducts: "Karlı Ürün",
    canonical: {
      product_name: "Ürün adı",
      revenue: "Ciro/Satış",
      cost: "Ürün maliyeti",
      commission: "Komisyon",
      shipping: "Kargo",
      ads_spend: "Reklam gideri"
    },
    aliases: {
      product_name: "Product, Product Name, Ürün Adı, SKU, Title, Item",
      revenue: "Revenue, Sales, Satış, Ciro, Gelir, Total, Price",
      cost: "Cost, COGS, Maliyet, Ürün Maliyeti, Buying Price",
      commission: "Commission, Komisyon, Marketplace Fee, Referral Fee",
      shipping: "Shipping, Kargo, Cargo, Delivery, Shipment",
      ads_spend: "Ads, Ad Spend, Reklam, PPC, Marketing"
    }
  },
  en: {
    app: "Ecom Analytics",
    plan: "plan",
    title: "E-commerce Profit Center",
    ready: "Ready",
    completed: "Completed",
    needsMapping: "Column mapping required",
    failed: "Failed",
    processing: "Processing",
    signOut: "Sign out",
    uploadsThisMonth: "uploads this month",
    revenue: "Revenue",
    profit: "Net Profit",
    adsSpend: "Ads Spend",
    margin: "Profit Margin",
    totalCosts: "Total Costs",
    contribution: "Contribution Profit",
    lossProducts: "Loss Products",
    averageOrderProfit: "Avg. Order Profit",
    upload: "Upload File",
    uploadHelp: "Upload Excel/CSV. The system auto-detects delimiter, number format, and columns.",
    uploadGuide: "Headers for Automated Analysis",
    sample: "Download sample CSV",
    required: "Required",
    optional: "Optional",
    acceptedNames: "Accepted header examples",
    products: "Products",
    insights: "AI Insights",
    uploads: "Uploads",
    reports: "Reports",
    reportMap: "E-commerce Report Map",
    reportMapHelp: "The left menu lists all major report groups; reports populate automatically as data arrives.",
    financial: "Financial Reports",
    performance: "Performance Reports",
    operations: "Operations Reports",
    growth: "Growth and Risk",
    available: "Active",
    planned: "Planned",
    noData: "Waiting for data",
    summary: "Summary",
    currentUpload: "Current analysis",
    reportCards: "Expanded Report Summary",
    reportType: "Report type",
    selectReportType: "Select report type before upload",
    combineReports: "Build combined report",
    selectedReports: "selected reports",
    generalReport: "Combined General Report",
    clearGeneralReport: "Close combined report",
    completedOnly: "Only completed reports can be selected",
    costBreakdown: "Cost Breakdown",
    topProducts: "Top Profitable Products",
    lossMakers: "Loss-making Products",
    adRatio: "Ads/Revenue",
    shippingRatio: "Shipping/Revenue",
    commissionRatio: "Commission/Revenue",
    profitableProducts: "Profitable Products",
    canonical: {
      product_name: "Product name",
      revenue: "Revenue/Sales",
      cost: "Product cost",
      commission: "Commission",
      shipping: "Shipping",
      ads_spend: "Ads spend"
    },
    aliases: {
      product_name: "Product, Product Name, Ürün Adı, SKU, Title, Item",
      revenue: "Revenue, Sales, Satış, Ciro, Gelir, Total, Price",
      cost: "Cost, COGS, Maliyet, Ürün Maliyeti, Buying Price",
      commission: "Commission, Komisyon, Marketplace Fee, Referral Fee",
      shipping: "Shipping, Kargo, Cargo, Delivery, Shipment",
      ads_spend: "Ads, Ad Spend, Reklam, PPC, Marketing"
    }
  }
} as const;

function isFullAnalysis(value: AnalysisResponse["analysis"]): value is Analysis {
  return Boolean(value && "totals" in value);
}

function ratio(part = 0, total = 0) {
  return total ? (part / total) * 100 : 0;
}

function downloadSampleCsv() {
  const rows = [
    "Product;Revenue;Cost;Commission;Shipping;Ads",
    "Test Product;100;50;10;5;8",
    "Second Product;200;80;20;12;15",
    "Bad Product;40;50;5;5;0"
  ];
  const blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "ecommerce-analysis-template.csv";
  anchor.click();
  URL.revokeObjectURL(url);
}

export default function DashboardPage() {
  const router = useRouter();
  const { language, setLanguage } = useLanguage();
  const t = text[language];
  const [token, setToken] = useState<string | null>(null);
  const [dashboard, setDashboard] = useState<Awaited<ReturnType<typeof api.dashboard>>>();
  const [reportTypes, setReportTypes] = useState<ReportDefinition[]>([]);
  const [selectedReportType, setSelectedReportType] = useState("profitability");
  const [analysisResponse, setAnalysisResponse] = useState<AnalysisResponse>();
  const [combinedAnalysis, setCombinedAnalysis] = useState<Analysis>();
  const [selectedUploadIds, setSelectedUploadIds] = useState<number[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [activeReport, setActiveReport] = useState("profitability");

  const currentAnalysis = isFullAnalysis(analysisResponse?.analysis) ? analysisResponse.analysis : undefined;
  const analysis = combinedAnalysis || currentAnalysis;
  const totals = analysis?.totals || dashboard?.totals;
  const products = analysis?.products || [];
  const selectedDefinition =
    reportTypes.find((report) => report.id === selectedReportType) || reportTypes[0];
  const totalCosts =
    (totals?.cost || 0) +
    (totals?.commission || 0) +
    (totals?.shipping || 0) +
    (totals?.ads_spend || 0);
  const profitableProducts = products.filter((product) => product.net_profit >= 0).length;
  const lossProducts = products.filter((product) => product.net_profit < 0).length;
  const averageOrderProfit = analysis?.orders?.length
    ? (totals?.profit || 0) / analysis.orders.length
    : 0;

  const uploadStatus = useMemo(() => {
    if (!analysisResponse) return "";
    if (analysisResponse.status === "completed") return t.completed;
    if (analysisResponse.status === "needs_mapping") return t.needsMapping;
    if (analysisResponse.status === "failed") return t.failed;
    return t.processing;
  }, [analysisResponse, t]);

  const reportGroups = [
    {
      title: t.financial,
      items: [
        { id: "profitability", label: language === "tr" ? "Karlılık" : "Profitability", icon: CircleDollarSign, active: true },
        { id: "pnl", label: language === "tr" ? "Gelir-Gider" : "P&L", icon: Receipt, active: true },
        { id: "pricing", label: language === "tr" ? "Fiyatlandırma" : "Pricing", icon: Percent, active: true },
        { id: "cashflow", label: language === "tr" ? "Nakit Akışı" : "Cash Flow", icon: CreditCard, active: false }
      ]
    },
    {
      title: t.performance,
      items: [
        { id: "sales", label: language === "tr" ? "Satış Performansı" : "Sales Performance", icon: ShoppingCart, active: true },
        { id: "products", label: language === "tr" ? "Ürün Analizi" : "Product Analysis", icon: PackageSearch, active: true },
        { id: "marketplace", label: language === "tr" ? "Pazaryeri Analizi" : "Marketplace Analysis", icon: BarChart3, active: false },
        { id: "trends", label: language === "tr" ? "Trendler" : "Trends", icon: LineChart, active: true }
      ]
    },
    {
      title: t.operations,
      items: [
        { id: "commission", label: language === "tr" ? "Komisyonlar" : "Commissions", icon: Calculator, active: true },
        { id: "shipping", label: language === "tr" ? "Kargo ve Lojistik" : "Shipping & Logistics", icon: Truck, active: true },
        { id: "returns", label: language === "tr" ? "İade ve İptal" : "Returns & Cancellations", icon: RotateCcw, active: false },
        { id: "inventory", label: language === "tr" ? "Stok ve Devir Hızı" : "Inventory Turnover", icon: Warehouse, active: false }
      ]
    },
    {
      title: t.growth,
      items: [
        { id: "ads", label: language === "tr" ? "Reklam ve ROAS" : "Ads & ROAS", icon: Megaphone, active: true },
        { id: "customers", label: language === "tr" ? "Müşteri Segmentleri" : "Customer Segments", icon: Users, active: false },
        { id: "risk", label: language === "tr" ? "Risk ve Uyarılar" : "Risk & Alerts", icon: AlertTriangle, active: true },
        { id: "exports", label: language === "tr" ? "Dışa Aktarım" : "Exports", icon: ClipboardList, active: false }
      ]
    }
  ];

  const reportCards = [
    {
      title: t.costBreakdown,
      value: money.format(totalCosts),
      detail: `${t.commissionRatio}: ${percent.format(ratio(totals?.commission, totals?.revenue))}%`
    },
    {
      title: language === "tr" ? "Reklam Verimliliği" : "Ad Efficiency",
      value: `${percent.format(ratio(totals?.ads_spend, totals?.revenue))}%`,
      detail: t.adRatio
    },
    {
      title: language === "tr" ? "Kargo Yükü" : "Shipping Load",
      value: `${percent.format(ratio(totals?.shipping, totals?.revenue))}%`,
      detail: t.shippingRatio
    },
    {
      title: t.topProducts,
      value: String(profitableProducts),
      detail: `${lossProducts} ${t.lossProducts.toLowerCase()}`
    },
    {
      title: t.averageOrderProfit,
      value: money.format(averageOrderProfit),
      detail: analysis?.orders?.length
        ? language === "tr"
          ? `${analysis.orders.length} sipariş`
          : `${analysis.orders.length} orders`
        : t.noData
    },
    {
      title: language === "tr" ? "Başabaş Risk" : "Break-even Risk",
      value: lossProducts ? String(lossProducts) : "0",
      detail: lossProducts ? t.lossMakers : t.available
    }
  ];

  async function loadDashboard(activeToken: string) {
    const data = await api.dashboard(activeToken);
    setDashboard(data);
  }

  async function loadReportTypes(activeToken: string) {
    const data = await api.reportTypes(activeToken);
    setReportTypes(data.reports);
    if (data.reports.length && !data.reports.some((report) => report.id === selectedReportType)) {
      setSelectedReportType(data.reports[0].id);
    }
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
    loadReportTypes(stored).catch(() => undefined);
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
      const upload = await api.upload(token, file, selectedReportType);
      setCombinedAnalysis(undefined);
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

  function toggleUploadSelection(uploadId: number) {
    setSelectedUploadIds((current) =>
      current.includes(uploadId)
        ? current.filter((id) => id !== uploadId)
        : [...current, uploadId]
    );
  }

  async function buildCombinedReport() {
    if (!token || selectedUploadIds.length === 0) return;
    setBusy(true);
    setError("");
    try {
      setCombinedAnalysis(await api.combinedReport(token, selectedUploadIds));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not build combined report");
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
      <aside className="sidebar report-sidebar">
        <div>
          <div className="brand">
            <BarChart3 size={30} />
            <strong>{t.app}</strong>
            <span>{dashboard?.plan === "pro" ? "Pro" : "Free"} {t.plan}</span>
          </div>
          <nav className="nav report-nav">
            {reportGroups.map((group) => (
              <div className="nav-group" key={group.title}>
                <span className="nav-group-title">{group.title}</span>
                {group.items.map((item) => {
                  const Icon = item.icon;
                  return (
                    <button
                      className={activeReport === item.id ? "active" : ""}
                      key={item.id}
                      type="button"
                      onClick={() => setActiveReport(item.id)}
                    >
                      <Icon size={16} />
                      <span>{item.label}</span>
                      <em>{item.active ? t.available : t.planned}</em>
                    </button>
                  );
                })}
              </div>
            ))}
          </nav>
        </div>
        <div className="sidebar-meta">
          {dashboard?.usage.uploads_this_month ?? 0} {t.uploadsThisMonth}
        </div>
      </aside>

      <section className="content">
        <div className="topbar">
          <div className="page-title">
            <h1>{t.title}</h1>
            <p>{combinedAnalysis ? t.generalReport : uploadStatus || t.ready}</p>
          </div>
          <div className="topbar-actions">
            <LanguageToggle language={language} onChange={setLanguage} />
            <button className="ghost-button" type="button" onClick={logout}>
              <LogOut size={17} />
              {t.signOut}
            </button>
          </div>
        </div>

        {error ? <div className="alert critical"><strong>{error}</strong></div> : null}

        <div className="grid stats extended-stats">
          <StatCard label={t.revenue} value={money.format(totals?.revenue || 0)} />
          <StatCard label={t.profit} value={money.format(totals?.profit || 0)} negative={(totals?.profit || 0) < 0} />
          <StatCard label={t.adsSpend} value={money.format(totals?.ads_spend || 0)} />
          <StatCard label={t.margin} value={`${analysis?.totals.margin ?? 0}%`} negative={(analysis?.totals.margin || 0) < 0} />
          <StatCard label={t.totalCosts} value={money.format(totalCosts)} />
          <StatCard label={t.lossProducts} value={String(lossProducts)} negative={lossProducts > 0} />
        </div>

        <section className="report-strip">
          <div>
            <h2>{t.reportMap}</h2>
            <p>{t.reportMapHelp}</p>
          </div>
          <strong>{reportGroups.flatMap((group) => group.items).length} {t.reports}</strong>
        </section>

        <div className="grid workspace">
          <div className="grid">
            <section className="panel">
              <div className="panel-header">
                <div>
                  <h2>{t.upload}</h2>
                  <p className="panel-subtitle">{t.uploadHelp}</p>
                </div>
                {busy ? <span className="status">{t.processing}</span> : null}
              </div>
              <label className="field report-type-field">
                <span>{t.selectReportType}</span>
                <select
                  value={selectedReportType}
                  onChange={(event) => setSelectedReportType(event.target.value)}
                >
                  {reportTypes.map((report) => (
                    <option key={report.id} value={report.id}>
                      {language === "tr" ? report.label_tr : report.label_en}
                    </option>
                  ))}
                </select>
              </label>
              <FileUpload
                disabled={busy}
                labels={{
                  title: language === "tr" ? "Pazaryeri dışa aktarımı" : "Marketplace export",
                  subtitle: "CSV / XLSX",
                  button: language === "tr" ? "Yükle" : "Upload"
                }}
                onFile={uploadFile}
              />
            </section>

            <section className="panel">
              <div className="panel-header">
                <div>
                  <h2>{t.uploadGuide}</h2>
                  <p className="panel-subtitle">
                    {selectedDefinition
                      ? language === "tr"
                        ? selectedDefinition.description_tr
                        : selectedDefinition.description_en
                      : t.reportType}
                  </p>
                </div>
                <button className="ghost-button" type="button" onClick={downloadSampleCsv}>
                  <UploadCloud size={17} />
                  {t.sample}
                </button>
              </div>
              <div className="schema-grid">
                {(selectedDefinition?.fields || []).map((field) => (
                  <div className="schema-row" key={field.key}>
                    <div>
                      <strong>{field.key}</strong>
                      <span>{language === "tr" ? field.label_tr : field.label_en}</span>
                    </div>
                    <p>{field.aliases.join(", ")}</p>
                    <em>{field.required ? t.required : t.optional}</em>
                  </div>
                ))}
              </div>
            </section>

            {combinedAnalysis ? (
              <section className="panel combined-panel">
                <div className="panel-header">
                  <div>
                    <h2>{t.generalReport}</h2>
                    <p className="panel-subtitle">
                      {combinedAnalysis.included_reports?.length || 0} {t.selectedReports}
                    </p>
                  </div>
                  <button className="ghost-button" type="button" onClick={() => setCombinedAnalysis(undefined)}>
                    {t.clearGeneralReport}
                  </button>
                </div>
                <div className="included-report-list">
                  {(combinedAnalysis.included_reports || []).map((report) => (
                    <div className="included-report" key={report.id}>
                      <strong>{report.filename}</strong>
                      <span>{report.report_type}</span>
                      <em>{money.format(report.totals?.profit || 0)}</em>
                    </div>
                  ))}
                </div>
              </section>
            ) : null}

            {analysisResponse?.status === "needs_mapping" ? (
              <MappingForm response={analysisResponse} onSubmit={saveMapping} />
            ) : null}

            <section className="panel">
              <div className="panel-header">
                <h2>{t.reportCards}</h2>
                <span className="status">{t.currentUpload}</span>
              </div>
              <div className="report-card-grid">
                {reportCards.map((card) => (
                  <div className="report-card" key={card.title}>
                    <span>{card.title}</span>
                    <strong>{card.value}</strong>
                    <p>{card.detail}</p>
                  </div>
                ))}
              </div>
            </section>

            <Charts
              analysis={analysis}
              labels={{
                revenueProfit: language === "tr" ? "Ciro ve Kar" : "Revenue and Profit",
                costBreakdown: t.costBreakdown
              }}
            />

            <section className="panel">
              <div className="panel-header">
                <h2>{t.products}</h2>
              </div>
              <ProductTable
                labels={{
                  product: language === "tr" ? "Ürün" : "Product",
                  revenue: t.revenue,
                  cost: language === "tr" ? "Maliyet" : "Cost",
                  commission: language === "tr" ? "Komisyon" : "Commission",
                  shipping: language === "tr" ? "Kargo" : "Shipping",
                  ads: language === "tr" ? "Reklam" : "Ads",
                  profit: t.profit,
                  margin: t.margin,
                  empty: language === "tr" ? "Henüz ürün yok" : "No products yet"
                }}
                products={products}
              />
            </section>
          </div>

          <div className="grid">
            <section className="panel">
              <div className="panel-header">
                <h2>{t.insights}</h2>
              </div>
              <Alerts insights={analysis?.insights || []} />
            </section>

            <section className="panel">
              <div className="panel-header">
                <h2>{t.uploads}</h2>
                <UploadCloud size={18} />
              </div>
              <div className="upload-list">
                {(dashboard?.recent_uploads || []).map((upload) => (
                  <div className="upload-item selectable-upload" key={upload.id}>
                    <label>
                      <input
                        checked={selectedUploadIds.includes(upload.id)}
                        disabled={upload.status !== "completed"}
                        type="checkbox"
                        onChange={() => toggleUploadSelection(upload.id)}
                      />
                      <span>{upload.filename}</span>
                    </label>
                    <button type="button" onClick={() => token && pollAnalysis(token, upload.id)}>
                      <span className="status">{upload.report_type || "profitability"}</span>
                      <span className="status">{upload.status}</span>
                    </button>
                  </div>
                ))}
              </div>
              <div className="combine-actions">
                <span className="muted">{selectedUploadIds.length} {t.selectedReports}</span>
                <button
                  className="primary-button"
                  disabled={selectedUploadIds.length === 0 || busy}
                  type="button"
                  onClick={buildCombinedReport}
                >
                  {t.combineReports}
                </button>
              </div>
              <p className="muted">{t.completedOnly}</p>
            </section>

            <section className="panel">
              <div className="panel-header">
                <h2>{language === "tr" ? "Aktif Rapor" : "Active Report"}</h2>
              </div>
              <div className="active-report-box">
                <Boxes size={22} />
                <strong>
                  {reportGroups
                    .flatMap((group) => group.items)
                    .find((item) => item.id === activeReport)?.label}
                </strong>
                <p className="muted">
                  {language === "tr"
                    ? "Bu başlığın metrikleri ana dashboard içinde gösteriliyor. Detay sayfaları sonraki modül olarak ayrılabilir."
                    : "This report's metrics are shown in the main dashboard. Dedicated drill-down pages can be split out next."}
                </p>
              </div>
            </section>
          </div>
        </div>
      </section>
    </main>
  );
}
