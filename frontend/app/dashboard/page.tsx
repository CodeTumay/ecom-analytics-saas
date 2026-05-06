"use client";

import { Alerts } from "@/components/Alerts";
import { Charts } from "@/components/Charts";
import { FileUpload } from "@/components/FileUpload";
import { LanguageToggle } from "@/components/LanguageToggle";
import { MappingForm } from "@/components/MappingForm";
import { ProductTable } from "@/components/ProductTable";
import { StatCard } from "@/components/StatCard";
import { Analysis, AnalysisResponse, ReportDefinition, api } from "@/lib/api";
import { DEFAULT_USD_TO_TRY, DisplayCurrency, formatMoney } from "@/lib/currency";
import { useLanguage } from "@/lib/i18n";
import {
  AlertTriangle,
  BarChart3,
  Bell,
  Boxes,
  Brain,
  Calculator,
  CalendarDays,
  CircleDollarSign,
  CreditCard,
  FileText,
  Link2,
  LineChart,
  LogOut,
  Megaphone,
  PackageSearch,
  Percent,
  Play,
  Printer,
  Radar,
  Receipt,
  Save,
  Settings,
  Send,
  ShieldCheck,
  ShoppingCart,
  Truck,
  UploadCloud
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

const percent = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 1,
  minimumFractionDigits: 0
});

const dataSourceConnections = [
  { id: "shopify", label: "Shopify", fields: ["store_url", "access_token"] },
  { id: "woocommerce", label: "WooCommerce", fields: ["store_url", "consumer_key", "consumer_secret"] },
  { id: "ikas", label: "ikas", fields: ["store_id", "api_key"] },
  { id: "ticimax", label: "Ticimax", fields: ["service_url", "api_key"] },
  { id: "nebim", label: "Nebim V3", fields: ["company_code", "api_user"] },
  { id: "logo", label: "Logo", fields: ["company_code", "api_user"] },
  { id: "mikro", label: "Mikro", fields: ["company_code", "api_user"] },
  { id: "parasut", label: "Paraşüt", fields: ["client_id", "client_secret"] }
] as const;

const text = {
  tr: {
    app: "JewelPilot",
    plan: "plan",
    title: "Accessory Retail Copilot",
    ready: "Hazır",
    completed: "Tamamlandı",
    needsMapping: "Kolon eşleştirme gerekli",
    failed: "Başarısız",
    processing: "İşleniyor",
    signOut: "Çıkış yap",
    reportView: "Rapor",
    settings: "Ayarlar",
    exportPdf: "PDF al",
    currency: "Para birimi",
    fxRate: "USD/TL kuru",
    uploadsThisMonth: "bu ay yükleme",
    revenue: "Ciro",
    profit: "Net Kar",
    adsSpend: "Nakit Bağlayan Stok",
    margin: "Kar Marjı",
    totalCosts: "Ürün Maliyeti",
    contribution: "Katkı Karı",
    lossProducts: "Zarardaki Ürün",
    averageOrderProfit: "Satır Başı Kar",
    upload: "Dosya Yükle",
    dataSources: "Veri kaynakları",
    apiConnections: "API Bağlantıları",
    apiConnectionsHelp: "İlk sürüm Excel/CSV retail health raporu üretir; entegrasyonlar daha sonra veri kaynağı olarak bağlanır.",
    manualUpload: "Manuel dosya yükleme",
    saveConnection: "Bağlantıyı kaydet",
    savedConnection: "Bağlantı kayıtlı",
    noConnection: "Bağlantı yok",
    uploadHelp: "Satış, stok, maliyet, mağaza, koleksiyon ve ürün verini yükle. Sistem retail karar raporu üretir.",
    uploadGuide: "Retail Health Template Alanları",
    sample: "Örnek CSV indir",
    required: "Zorunlu",
    optional: "Opsiyonel",
    formula: "Formül",
    logic: "İşlem Mantığı",
    acceptedNames: "Kabul edilen başlık örnekleri",
    reportDetails: "Rapor Detayları",
    emptyDetail: "Detay satırı yok",
    products: "Ürünler",
    insights: "AI İçgörüler",
    uploads: "Yüklemeler",
    reports: "Raporlar",
    reportMap: "Accessory Retail Copilot",
    reportMapHelp: "Mağaza, stok, koleksiyon ve yatırımcı kararlarını tek rapora çevirir.",
    financial: "CEO",
    performance: "Mağaza",
    operations: "Ürün & Stok",
    growth: "Board",
    available: "Aktif",
    planned: "Planlandı",
    noData: "Veri bekleniyor",
    summary: "Özet",
    currentUpload: "Mevcut analiz",
    reportCards: "Kapsamlı Rapor Özeti",
    reportType: "Rapor tipi",
    selectReportType: "Yüklenecek rapor tipini seç",
    combineReports: "Retail health raporu oluştur",
    selectedReports: "seçili rapor",
    generalReport: "Genel Birleşik Rapor",
    clearGeneralReport: "Genel raporu kapat",
    completedOnly: "Sadece tamamlanan raporlar seçilebilir",
    costBreakdown: "Nakit Bağlayan Stok",
    topProducts: "Hero Ürünler",
    lossMakers: "Eritilecek Ürünler",
    adRatio: "Stok/Ciro",
    shippingRatio: "Sell-through",
    commissionRatio: "Brüt Marj",
    profitableProducts: "Hero SKU",
    automationCenter: "Veri Kaynakları",
    integrationsCenter: "CSV/Excel önce; Shopify, WooCommerce, ikas, Ticimax, Nebim, Logo, Mikro ve Paraşüt sonra.",
    notificationCenter: "Retail Karar Uyarıları",
    competitorCenter: "Benchmark Hazırlığı",
    planningCenter: "Reorder ve Transfer Planı",
    rolesCenter: "Çoklu Kullanıcı ve Yetkiler",
    businessModels: "İş Modeli",
    dashboardExports: "Dashboard ve Bildirim Kanalları",
    connected: "bağlı",
    configured: "kurulu",
    tracked: "takipte",
    enabled: "aktif",
    forecast30: "30 gün tahmin",
    forecast60: "60 gün tahmin",
    forecast90: "90 gün tahmin",
    expectedProfit: "Beklenen kar",
    scenarioAnalysis: "Senaryo Analizi",
    providerReady: "Planlandı",
    canonical: {
      product_name: "Ürün adı",
      revenue: "Ciro/Satış",
      cost: "Ürün maliyeti",
      commission: "Mağaza m²",
      shipping: "Stok",
      ads_spend: "Stok değeri"
    },
    aliases: {
      product_name: "Product, Product Name, Ürün Adı, SKU, Title, Item",
      revenue: "Revenue, Sales, Satış, Ciro, Gelir, Total, Price",
      cost: "Cost, COGS, Maliyet, Ürün Maliyeti, Buying Price",
      commission: "Store m2, Mağaza m², Metrekare",
      shipping: "Stock, Stok, Inventory",
      ads_spend: "Inventory Value, Stok Değeri"
    }
  },
  en: {
    app: "JewelPilot",
    plan: "plan",
    title: "Accessory Retail Copilot",
    ready: "Ready",
    completed: "Completed",
    needsMapping: "Column mapping required",
    failed: "Failed",
    processing: "Processing",
    signOut: "Sign out",
    reportView: "Report",
    settings: "Settings",
    exportPdf: "Export PDF",
    currency: "Currency",
    fxRate: "USD/TRY rate",
    uploadsThisMonth: "uploads this month",
    revenue: "Revenue",
    profit: "Net Profit",
    adsSpend: "Cash in Inventory",
    margin: "Profit Margin",
    totalCosts: "Product Cost",
    contribution: "Contribution Profit",
    lossProducts: "Loss Products",
    averageOrderProfit: "Profit per Row",
    upload: "Upload File",
    dataSources: "Data sources",
    apiConnections: "API Connections",
    apiConnectionsHelp: "MVP starts with CSV/Excel retail health reports; integrations become data sources later.",
    manualUpload: "Manual file upload",
    saveConnection: "Save connection",
    savedConnection: "Connection saved",
    noConnection: "No connection",
    uploadHelp: "Upload sales, inventory, cost, store, collection, and product data. The system returns a retail decision report.",
    uploadGuide: "Retail Health Template Fields",
    sample: "Download sample CSV",
    required: "Required",
    optional: "Optional",
    formula: "Formula",
    logic: "Processing Logic",
    acceptedNames: "Accepted header examples",
    reportDetails: "Report Details",
    emptyDetail: "No detail rows",
    products: "Products",
    insights: "AI Insights",
    uploads: "Uploads",
    reports: "Reports",
    reportMap: "Accessory Retail Copilot",
    reportMapHelp: "Turns store, inventory, collection, and board decisions into one action report.",
    financial: "CEO",
    performance: "Store",
    operations: "Product & Stock",
    growth: "Board",
    available: "Active",
    planned: "Planned",
    noData: "Waiting for data",
    summary: "Summary",
    currentUpload: "Current analysis",
    reportCards: "Expanded Report Summary",
    reportType: "Report type",
    selectReportType: "Select report type before upload",
    combineReports: "Build retail health report",
    selectedReports: "selected reports",
    generalReport: "Combined General Report",
    clearGeneralReport: "Close combined report",
    completedOnly: "Only completed reports can be selected",
    costBreakdown: "Cash in Inventory",
    topProducts: "Hero Products",
    lossMakers: "Markdown Products",
    adRatio: "Stock/Revenue",
    shippingRatio: "Sell-through",
    commissionRatio: "Gross Margin",
    profitableProducts: "Hero SKU",
    automationCenter: "Data Sources",
    integrationsCenter: "CSV/Excel first; Shopify, WooCommerce, ikas, Ticimax, Nebim, Logo, Mikro, and Paraşüt later.",
    notificationCenter: "Retail Decision Alerts",
    competitorCenter: "Benchmark Readiness",
    planningCenter: "Reorder and Transfer Plan",
    rolesCenter: "Multi-user Roles",
    businessModels: "Business Model",
    dashboardExports: "Dashboard and Notification Channels",
    connected: "connected",
    configured: "configured",
    tracked: "tracked",
    enabled: "enabled",
    forecast30: "30-day forecast",
    forecast60: "60-day forecast",
    forecast90: "90-day forecast",
    expectedProfit: "Expected profit",
    scenarioAnalysis: "Scenario Analysis",
    providerReady: "Planned",
    canonical: {
      product_name: "Product name",
      revenue: "Revenue/Sales",
      cost: "Product cost",
      commission: "Store m²",
      shipping: "Stock",
      ads_spend: "Inventory value"
    },
    aliases: {
      product_name: "Product, Product Name, Ürün Adı, SKU, Title, Item",
      revenue: "Revenue, Sales, Satış, Ciro, Gelir, Total, Price",
      cost: "Cost, COGS, Maliyet, Ürün Maliyeti, Buying Price",
      commission: "Store m2, Mağaza m², Metrekare",
      shipping: "Stock, Stok, Inventory",
      ads_spend: "Inventory Value, Stok Değeri"
    }
  }
} as const;

function isFullAnalysis(value: AnalysisResponse["analysis"]): value is Analysis {
  return Boolean(value && "totals" in value);
}

function ratio(part = 0, total = 0) {
  return total ? (part / total) * 100 : 0;
}

function sumDetail(rows: Analysis["detail_rows"] | undefined, key: string) {
  return (rows || []).reduce((sum, row) => sum + Number(row[key] || 0), 0);
}

function sampleValue(key: string, index: number) {
  if (key.includes("date")) return index === 1 ? "01.01.2026" : "02.01.2026";
  if (key.includes("period") || key === "month") return index === 1 ? "Ocak 2026" : "Şubat 2026";
  if (key.includes("store")) return index === 1 ? "Nişantaşı" : "Galataport";
  if (key.includes("product_name")) return index === 1 ? "Pearl Hoop Earrings" : "Natural Stone Bracelet";
  if (key.includes("collection")) return index === 1 ? "Pearl Collection" : "Natural Stone";
  if (key.includes("material")) return index === 1 ? "İnci" : "Doğal taş";
  if (key.includes("risk")) return index === 1 ? "Stok" : "Nakit";
  if (key.includes("category")) return index === 1 ? "Küpe" : "Bileklik";
  if (key.includes("sku")) return index === 1 ? "JWL-001" : "JWL-002";
  if (key.includes("order")) return index === 1 ? "ORD-001" : "ORD-002";
  if (key.includes("rate") || key.includes("pct") || key.includes("ratio")) return index === 1 ? "15" : "8";
  if (key.includes("count") || key.includes("units") || key.includes("click") || key.includes("conversion")) return index === 1 ? "10" : "25";
  if (key.includes("score")) return index === 1 ? "8" : "4";
  return index === 1 ? "1000" : "650";
}

function downloadSampleCsv(report?: ReportDefinition) {
  const fields = report?.fields?.length
    ? report.fields
    : [
        { key: "product_name" },
        { key: "revenue" },
        { key: "cost" },
        { key: "stock" },
        { key: "collection" },
        { key: "store_name" }
      ];
  const header = fields.map((field) => field.key).join(";");
  const rows = [
    header,
    fields.map((field) => sampleValue(field.key, 1)).join(";"),
    fields.map((field) => sampleValue(field.key, 2)).join(";")
  ];
  const blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${report?.id || "retail-health"}-template.csv`;
  anchor.click();
  URL.revokeObjectURL(url);
}

function DetailTable({
  emptyLabel,
  rows
}: {
  emptyLabel: string;
  rows?: Array<Record<string, string | number>>;
}) {
  const columns = rows?.[0] ? Object.keys(rows[0]).slice(0, 12) : [];
  return (
    <div className="table-wrap detail-table">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {(rows || []).slice(0, 50).map((row, index) => (
            <tr key={`${index}-${columns.join("-")}`}>
              {columns.map((column) => (
                <td key={column}>{row[column]}</td>
              ))}
            </tr>
          ))}
          {!rows?.length ? (
            <tr>
              <td className="muted" colSpan={Math.max(columns.length, 1)}>{emptyLabel}</td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const { language, setLanguage } = useLanguage();
  const t = text[language];
  const [token, setToken] = useState<string | null>(null);
  const [dashboard, setDashboard] = useState<Awaited<ReturnType<typeof api.dashboard>>>();
  const [platformCatalog, setPlatformCatalog] = useState<Awaited<ReturnType<typeof api.platformCatalog>>>();
  const [platformOverview, setPlatformOverview] = useState<Awaited<ReturnType<typeof api.platformOverview>>>();
  const [planningSummary, setPlanningSummary] = useState<Awaited<ReturnType<typeof api.planningSummary>>>();
  const [integrations, setIntegrations] = useState<Awaited<ReturnType<typeof api.integrations>>>([]);
  const [reportTypes, setReportTypes] = useState<ReportDefinition[]>([]);
  const [selectedReportType, setSelectedReportType] = useState("retail_health");
  const [analysisResponse, setAnalysisResponse] = useState<AnalysisResponse>();
  const [combinedAnalysis, setCombinedAnalysis] = useState<Analysis>();
  const [selectedUploadIds, setSelectedUploadIds] = useState<number[]>([]);
  const [displayCurrency, setDisplayCurrency] = useState<DisplayCurrency>("USD");
  const [usdToTry, setUsdToTry] = useState(DEFAULT_USD_TO_TRY);
  const [activeView, setActiveView] = useState<"report" | "settings">("report");
  const [integrationForms, setIntegrationForms] = useState<Record<string, Record<string, string>>>({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [activeReport, setActiveReport] = useState("retail_health");

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
  const inventoryValue = sumDetail(analysis?.detail_rows, "inventory_value");
  const sellThrough =
    analysis?.detail_rows?.length
      ? sumDetail(analysis.detail_rows, "sell_through") / analysis.detail_rows.length
      : 0;
  const profitableProducts = products.filter((product) => product.net_profit >= 0).length;
  const lossProducts = products.filter((product) => product.net_profit < 0).length;
  const averageOrderProfit = analysis?.orders?.length
    ? (totals?.profit || 0) / analysis.orders.length
    : 0;
  const connectedProviders = new Set(
    integrations
      .filter((integration) => integration.status === "connected")
      .map((integration) => `${integration.category}:${integration.provider}`)
  );
  const integrationByProvider = new Map(
    integrations.map((integration) => [integration.provider, integration])
  );
  const money = (value: number, maximumFractionDigits = 0) =>
    formatMoney(value, displayCurrency, usdToTry, maximumFractionDigits);

  const uploadStatus = useMemo(() => {
    if (!analysisResponse) return "";
    if (analysisResponse.status === "completed") return t.completed;
    if (analysisResponse.status === "needs_mapping") return t.needsMapping;
    if (analysisResponse.status === "failed") return t.failed;
    return t.processing;
  }, [analysisResponse, t]);

  const reportIconById = {
    retail_health: CircleDollarSign,
    ceo_dashboard: Receipt,
    store_performance: ShoppingCart,
    product_collection: PackageSearch,
    reorder_transfer: Truck,
    investor_board: FileText
  } as const;
  const categoryTitles = {
    ceo: t.financial,
    store: t.performance,
    product: t.operations,
    action: t.planningCenter,
    board: t.growth
  } as const;
  const reportGroups = (["ceo", "store", "product", "action", "board"] as const)
    .map((category) => ({
      title: categoryTitles[category],
      items: reportTypes
        .filter((report) => report.category === category)
        .map((report) => ({
          id: report.id,
          label: language === "tr" ? report.label_tr : report.label_en,
          icon: reportIconById[report.id as keyof typeof reportIconById] || BarChart3,
          active: true
        }))
    }))
    .filter((group) => group.items.length > 0);

  const reportCards = [
    {
      title: t.costBreakdown,
      value: money(inventoryValue || totalCosts),
      detail: `${t.commissionRatio}: ${percent.format(totals?.margin || 0)}%`
    },
    {
      title: language === "tr" ? "Stokta Bağlı Nakit" : "Cash in Stock",
      value: `${percent.format(ratio(inventoryValue, totals?.revenue))}%`,
      detail: t.adRatio
    },
    {
      title: language === "tr" ? "Sell-through" : "Sell-through",
      value: `${percent.format(sellThrough)}%`,
      detail: t.shippingRatio
    },
    {
      title: t.topProducts,
      value: String(profitableProducts),
      detail: `${lossProducts} ${t.lossProducts.toLowerCase()}`
    },
    {
      title: t.averageOrderProfit,
      value: money(averageOrderProfit),
      detail: analysis?.orders?.length
        ? language === "tr"
          ? `${analysis.orders.length} veri satırı`
          : `${analysis.orders.length} data rows`
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

  async function loadPlatform(activeToken: string) {
    const [catalog, overview, planning, integrationList] = await Promise.all([
      api.platformCatalog(activeToken),
      api.platformOverview(activeToken),
      api.planningSummary(activeToken),
      api.integrations(activeToken)
    ]);
    setPlatformCatalog(catalog);
    setPlatformOverview(overview);
    setPlanningSummary(planning);
    setIntegrations(integrationList);
    setIntegrationForms((current) => {
      const next = { ...current };
      integrationList.forEach((integration) => {
        if (integration.config && !next[integration.provider]) {
          next[integration.provider] = Object.fromEntries(
            Object.entries(integration.config).filter(([, value]) => value !== "***")
          );
        }
      });
      return next;
    });
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
    loadPlatform(stored).catch(() => undefined);
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

  function updateIntegrationField(provider: string, field: string, value: string) {
    setIntegrationForms((current) => ({
      ...current,
      [provider]: {
        ...(current[provider] || {}),
        [field]: value
      }
    }));
  }

  async function saveDataSourceIntegration(provider: string) {
    if (!token) return;
    setBusy(true);
    setError("");
    try {
      await api.saveIntegration(token, {
        category: "data_source",
        provider,
        sync_frequency: "hourly",
        config: integrationForms[provider] || {}
      });
      await loadPlatform(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Connection could not be saved");
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    localStorage.removeItem("token");
    router.push("/login");
  }

  function exportPdf() {
    window.print();
  }

  return (
    <main className={`app-shell ${activeView === "settings" ? "settings-view" : "report-view"}`}>
      <aside className="sidebar report-sidebar">
        <div>
          <div className="brand">
            <BarChart3 size={30} />
            <strong>{t.app}</strong>
            <span>{dashboard?.plan === "pro" ? "Pro" : "Free"} {t.plan}</span>
          </div>
          <nav className="nav report-nav">
            <div className="nav-group">
              <button
                className={activeView === "report" ? "active" : ""}
                type="button"
                onClick={() => setActiveView("report")}
              >
                <FileText size={16} />
                <span>{t.reportView}</span>
                <em>{t.available}</em>
              </button>
              <button
                className={activeView === "settings" ? "active" : ""}
                type="button"
                onClick={() => setActiveView("settings")}
              >
                <Settings size={16} />
                <span>{t.settings}</span>
                <em>{integrations.length}</em>
              </button>
            </div>
            {activeView === "report" ? reportGroups.map((group) => (
                <div className="nav-group" key={group.title}>
                  <span className="nav-group-title">{group.title}</span>
                  {group.items.map((item) => {
                    const Icon = item.icon;
                    return (
                      <button
                        className={activeReport === item.id ? "active" : ""}
                        key={item.id}
                        type="button"
                        onClick={() => {
                          setActiveReport(item.id);
                          setSelectedReportType(item.id);
                        }}
                      >
                        <Icon size={16} />
                        <span>{item.label}</span>
                        <em>{item.active ? t.available : t.planned}</em>
                      </button>
                    );
                  })}
                </div>
              )) : null}
          </nav>
        </div>
        <div className="sidebar-meta">
          {dashboard?.usage.uploads_this_month ?? 0} {t.uploadsThisMonth}
        </div>
      </aside>

      <section className="content">
        <div className="topbar">
          <div className="topbar-search">
            <PackageSearch size={18} />
            <input
              aria-label={language === "tr" ? "Analitik ara" : "Search analytics"}
              placeholder={language === "tr" ? "Analitik ara..." : "Search analytics..."}
            />
          </div>
          <div className="topbar-actions">
            <div className="toolbar-group" aria-label={t.currency}>
              <select
                aria-label={t.currency}
                value={displayCurrency}
                onChange={(event) => setDisplayCurrency(event.target.value as DisplayCurrency)}
              >
                <option value="USD">USD</option>
                <option value="TRY">TL</option>
              </select>
              {displayCurrency === "TRY" ? (
                <input
                  aria-label={t.fxRate}
                  min="1"
                  step="0.01"
                  type="number"
                  value={usdToTry}
                  onChange={(event) => setUsdToTry(Number(event.target.value) || DEFAULT_USD_TO_TRY)}
                />
              ) : null}
            </div>
            <LanguageToggle language={language} onChange={setLanguage} />
            <button className="ghost-button report-only" type="button" onClick={exportPdf}>
              <Printer size={17} />
              {t.exportPdf}
            </button>
            <button className="ghost-button" type="button" onClick={logout}>
              <LogOut size={17} />
              {t.signOut}
            </button>
          </div>
        </div>

        <div className="dashboard-heading">
          <div className="page-title">
            <h1>{activeView === "settings" ? t.settings : t.title}</h1>
            <p>{activeView === "settings" ? t.apiConnectionsHelp : combinedAnalysis ? t.generalReport : uploadStatus || t.ready}</p>
          </div>
          <div className="date-filter">
            <CalendarDays size={18} />
            <span>{language === "tr" ? "Son 30 Gün" : "Last 30 Days"}</span>
          </div>
        </div>

        {error ? <div className="alert critical"><strong>{error}</strong></div> : null}

        <div className="grid stats extended-stats report-only">
          <StatCard label={t.revenue} value={money(totals?.revenue || 0)} />
          <StatCard label={t.profit} value={money(totals?.profit || 0)} negative={(totals?.profit || 0) < 0} />
          <StatCard label={t.adsSpend} value={money(inventoryValue || totals?.ads_spend || 0)} />
          <StatCard label={t.margin} value={`${analysis?.totals.margin ?? 0}%`} negative={(analysis?.totals.margin || 0) < 0} />
          <StatCard label={t.totalCosts} value={money(totalCosts)} />
          <StatCard label={t.lossProducts} value={String(lossProducts)} negative={lossProducts > 0} />
        </div>

        <section className="report-strip settings-only">
          <div>
            <h2>{t.dataSources}</h2>
            <p>{t.apiConnectionsHelp}</p>
          </div>
          <strong>{integrations.length} {t.configured}</strong>
        </section>

        <div className="grid workspace">
          <div className="grid">
            <section className="panel settings-only">
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
                  onChange={(event) => {
                    setSelectedReportType(event.target.value);
                    setActiveReport(event.target.value);
                  }}
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
                  title: language === "tr" ? "Retail Health veri dosyası" : "Retail Health data file",
                  subtitle: "CSV / XLSX",
                  button: language === "tr" ? "Yükle" : "Upload"
                }}
                onFile={uploadFile}
              />
              <div className="integration-form">
                <div>
                  <h3>{t.apiConnections}</h3>
                  <p>{t.apiConnectionsHelp}</p>
                </div>
                <div className="connection-list">
                  {dataSourceConnections.map((provider) => {
                    const saved = integrationByProvider.get(provider.id);
                    return (
                      <div className="connection-card" key={provider.id}>
                        <div className="connection-card-header">
                          <div>
                            <strong>{provider.label}</strong>
                            <span>{saved ? t.savedConnection : t.noConnection}</span>
                          </div>
                          {saved ? <em>{saved.status}</em> : null}
                        </div>
                        <div className="integration-fields">
                          {provider.fields.map((field) => (
                            <label key={field}>
                              <span>{field}</span>
                              <input
                                type={field.includes("secret") || field.includes("key") ? "password" : "text"}
                                value={integrationForms[provider.id]?.[field] || ""}
                                placeholder={saved?.config?.[field] === "***" ? "***" : ""}
                                onChange={(event) =>
                                  updateIntegrationField(provider.id, field, event.target.value)
                                }
                              />
                            </label>
                          ))}
                        </div>
                        <div className="connection-actions">
                          <button
                            className="ghost-button"
                            disabled={busy}
                            type="button"
                            onClick={() => saveDataSourceIntegration(provider.id)}
                          >
                            <Save size={17} />
                            {t.saveConnection}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </section>

            <section className="panel settings-only">
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
                <button className="ghost-button" type="button" onClick={() => downloadSampleCsv(selectedDefinition)}>
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
                    <div className="schema-copy">
                      <p><b>{t.acceptedNames}:</b> {field.aliases.join(", ")}</p>
                      {(language === "tr" ? field.formula_tr : field.formula_en) ? (
                        <p><b>{t.formula}:</b> {language === "tr" ? field.formula_tr : field.formula_en}</p>
                      ) : null}
                    </div>
                    <em>{field.required ? t.required : t.optional}</em>
                  </div>
                ))}
              </div>
              {selectedDefinition ? (
                <div className="logic-list">
                  <strong>{t.logic}</strong>
                  {(language === "tr" ? selectedDefinition.logic_tr : selectedDefinition.logic_en)?.map((item) => (
                    <span key={item}>{item}</span>
                  ))}
                </div>
              ) : null}
            </section>

            {combinedAnalysis ? (
              <section className="panel combined-panel report-only">
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
                      <em>{money(report.totals?.profit || 0)}</em>
                    </div>
                  ))}
                </div>
              </section>
            ) : null}

            {analysisResponse?.status === "needs_mapping" ? (
              <div className="settings-only">
                <MappingForm response={analysisResponse} onSubmit={saveMapping} />
              </div>
            ) : null}

            <section className="panel report-only">
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

            <section className="panel settings-only">
              <div className="panel-header">
                <div>
                  <h2>{t.automationCenter}</h2>
                  <p className="panel-subtitle">{t.integrationsCenter}</p>
                </div>
                <Link2 size={18} />
              </div>
              <div className="provider-grid">
                {[
                  { category: "data_source", title: language === "tr" ? "Veri kaynakları" : "Data sources", items: platformCatalog?.providers.data_sources || [] }
                ].map((group) => (
                  <div className="provider-group" key={group.category}>
                    <strong>{group.title}</strong>
                    <span>
                      {platformOverview?.integrations.by_category?.[group.category] || 0} {t.configured}
                    </span>
                    <div className="provider-list">
                      {group.items.map((provider) => {
                        const connected = connectedProviders.has(`${group.category}:${provider.id}`);
                        return (
                          <div className={connected ? "provider-card connected" : "provider-card"} key={provider.id}>
                            <b>{provider.label}</b>
                            <em>{connected ? t.connected : t.providerReady}</em>
                            <small>{provider.pulls.join(", ")}</small>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <div className="report-only">
              <Charts
                analysis={analysis}
                formatMoney={money}
                labels={{
                  revenueProfit: language === "tr" ? "Ciro ve Kar" : "Revenue and Profit",
                  costBreakdown: t.costBreakdown
                }}
              />
            </div>

            <section className="panel report-only">
              <div className="panel-header">
                <h2>{t.products}</h2>
              </div>
              <ProductTable
                formatMoney={money}
                labels={{
                  product: language === "tr" ? "Ürün" : "Product",
                  revenue: t.revenue,
                  cost: language === "tr" ? "Maliyet" : "Cost",
                  profit: t.profit,
                  margin: t.margin,
                  empty: language === "tr" ? "Henüz ürün yok" : "No products yet"
                }}
                products={products}
              />
            </section>

            <section className="panel report-only">
              <div className="panel-header">
                <h2>{t.reportDetails}</h2>
                <span className="status">{analysis?.report_type || selectedReportType}</span>
              </div>
              <DetailTable emptyLabel={t.emptyDetail} rows={analysis?.detail_rows} />
            </section>
          </div>

          <div className="grid">
            <section className="panel report-only">
              <div className="panel-header">
                <h2>{t.insights}</h2>
              </div>
              <Alerts insights={analysis?.insights || []} />
            </section>

            <section className="panel settings-only">
              <div className="panel-header">
                <div>
                  <h2>{t.notificationCenter}</h2>
                  <p className="panel-subtitle">
                    {platformOverview?.alerts.enabled || 0} {t.enabled}
                  </p>
                </div>
                <Bell size={18} />
              </div>
              <div className="roadmap-list">
                {(platformCatalog?.alert_templates || []).map((alert) => (
                  <div className={`roadmap-item ${alert.severity}`} key={alert.event}>
                    <strong>{alert.event}</strong>
                    <span>{language === "tr" ? alert.message_tr : alert.message_tr}</span>
                  </div>
                ))}
              </div>
            </section>

            <section className="panel settings-only">
              <div className="panel-header">
                <div>
                  <h2>{t.planningCenter}</h2>
                  <p className="panel-subtitle">{t.scenarioAnalysis}</p>
                </div>
                <Brain size={18} />
              </div>
              <div className="forecast-grid">
                <StatCard label={t.forecast30} value={money(planningSummary?.sales_forecast.next_30_days || 0)} />
                <StatCard label={t.forecast60} value={money(planningSummary?.sales_forecast.next_60_days || 0)} />
                <StatCard label={t.forecast90} value={money(planningSummary?.sales_forecast.next_90_days || 0)} />
              </div>
              <div className="scenario-list">
                {(planningSummary?.scenarios || []).map((scenario) => (
                  <div className="scenario-item" key={scenario.id}>
                    <strong>{scenario.id}</strong>
                    <span>{money(scenario.profit)} / {scenario.margin}%</span>
                  </div>
                ))}
              </div>
            </section>

            <section className="panel settings-only">
              <div className="panel-header">
                <div>
                  <h2>{t.competitorCenter}</h2>
                  <p className="panel-subtitle">
                    {platformOverview?.competitors.tracked || 0} {t.tracked}
                  </p>
                </div>
                <Radar size={18} />
              </div>
              <p className="muted">
                {language === "tr"
                  ? "Rakip fiyat, stok ve kampanya takip kayıtları API üzerinden yönetilir; scraping işi güvenli adapter ile sıraya alınır."
                  : "Competitor price, stock, and campaign watches are managed through the API; scraping is queued through a safe adapter."}
              </p>
            </section>

            <section className="panel settings-only">
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
                      <span className="status">{upload.report_type || "retail_health"}</span>
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

            <section className="panel settings-only">
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

            <section className="panel settings-only">
              <div className="panel-header">
                <div>
                  <h2>{t.dashboardExports}</h2>
                  <p className="panel-subtitle">Power BI, Tableau, Excel, Mail, WhatsApp, Telegram</p>
                </div>
                <Send size={18} />
              </div>
              <div className="chip-list">
                {(platformCatalog?.dashboard_exports || []).map((item) => (
                  <span key={item}>{item}</span>
                ))}
              </div>
            </section>

            <section className="panel settings-only">
              <div className="panel-header">
                <div>
                  <h2>{t.rolesCenter}</h2>
                  <p className="panel-subtitle">Admin, finans, pazarlama, operasyon, salt okunur</p>
                </div>
                <ShieldCheck size={18} />
              </div>
              <div className="roadmap-list compact">
                {(platformCatalog?.roles || []).map((role) => (
                  <div className="roadmap-item" key={role.id}>
                    <strong>{role.label_tr}</strong>
                    <span>{role.permissions.join(", ")}</span>
                  </div>
                ))}
              </div>
            </section>

            <section className="panel settings-only">
              <div className="panel-header">
                <div>
                  <h2>{t.businessModels}</h2>
                  <p className="panel-subtitle">Excel, SaaS, hibrit ve danışmanlık paketleri</p>
                </div>
                <FileText size={18} />
              </div>
              <div className="roadmap-list compact">
                {(platformCatalog?.business_models || []).map((model) => (
                  <div className="roadmap-item" key={model.id}>
                    <strong>{model.label_tr}</strong>
                    <span>{model.price_tr}</span>
                  </div>
                ))}
              </div>
            </section>
          </div>
        </div>
      </section>
      <footer className="bottom-nav">
        <button className={activeView === "report" ? "active" : ""} type="button" onClick={() => setActiveView("report")}>
          <BarChart3 size={20} />
          <span>{language === "tr" ? "Finans" : "Finance"}</span>
        </button>
        <button type="button" onClick={() => setActiveReport("store_performance")}>
          <LineChart size={20} />
          <span>{language === "tr" ? "Performans" : "Performance"}</span>
        </button>
        <button type="button" onClick={() => setActiveReport("reorder_transfer")}>
          <Truck size={20} />
          <span>{language === "tr" ? "Operasyon" : "Ops"}</span>
        </button>
        <button className={activeView === "settings" ? "active" : ""} type="button" onClick={() => setActiveView("settings")}>
          <Settings size={20} />
          <span>{t.settings}</span>
        </button>
      </footer>
    </main>
  );
}
