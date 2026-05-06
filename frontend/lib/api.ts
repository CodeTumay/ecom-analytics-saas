const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Totals = {
  revenue: number;
  cost: number;
  commission: number;
  shipping: number;
  ads_spend: number;
  profit: number;
  margin?: number;
};

export type ProductRow = {
  product_name: string;
  revenue: number;
  cost: number;
  commission: number;
  shipping: number;
  ads_spend: number;
  net_profit: number;
  profit_margin: number;
};

export type Insight = {
  severity: "success" | "warning" | "critical";
  message: string;
  recommendation: string;
};

export type Analysis = {
  report_type?: string;
  totals: Totals;
  top_profitable_products: ProductRow[];
  loss_making_products: ProductRow[];
  revenue_trends: Array<{ period: number; revenue: number; profit: number }>;
  cost_breakdown: Array<{ name: string; value: number }>;
  products: ProductRow[];
  orders: ProductRow[];
  detail_rows?: Array<Record<string, string | number>>;
  insights: Insight[];
  logic_tr?: string[];
  logic_en?: string[];
  included_reports?: Array<{
    id: number;
    filename: string;
    report_type: string;
    totals: Totals;
  }>;
};

export type ReportField = {
  key: string;
  label_tr: string;
  label_en: string;
  required: boolean;
  kind: "text" | "number" | "date" | string;
  aliases: string[];
  formula_tr?: string;
  formula_en?: string;
};

export type ReportDefinition = {
  id: string;
  category: "financial" | "performance" | "operations" | "growth" | string;
  label_tr: string;
  label_en: string;
  description_tr: string;
  description_en: string;
  logic_tr?: string[];
  logic_en?: string[];
  fields: ReportField[];
};

export type AnalysisResponse = {
  upload_id: number;
  status: "queued" | "processing" | "needs_mapping" | "completed" | "failed";
  report_type?: string;
  mapping?: Record<string, string>;
  analysis?: Analysis | {
    columns: string[];
    missing_required: string[];
    missing_optional: string[];
  };
  error_message?: string;
};

export type DashboardResponse = {
  plan: "free" | "pro";
  usage: { uploads_this_month: number };
  totals: Totals;
  recent_uploads: Array<{
    id: number;
    filename: string;
    status: string;
    report_type?: string;
    created_at: string;
  }>;
};

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    let message = "Request failed";
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
      message = response.statusText;
    }
    throw new Error(message);
  }

  return response.json();
}

export const api = {
  register: (email: string, password: string) =>
    request<{ id: number; email: string; plan: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password })
    }),

  login: (email: string, password: string) =>
    request<{ access_token: string; token_type: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    }),

  dashboard: (token: string) => request<DashboardResponse>("/dashboard", {}, token),

  reportTypes: (token: string) =>
    request<{ reports: ReportDefinition[] }>("/report-types", {}, token),

  upload: (token: string, file: File, reportType = "profitability") => {
    const form = new FormData();
    form.append("file", file);
    form.append("report_type", reportType);
    return request<{ id: number; status: string }>("/upload", {
      method: "POST",
      body: form
    }, token);
  },

  analysis: (token: string, uploadId: number) =>
    request<AnalysisResponse>(`/analysis/${uploadId}`, {}, token),

  combinedReport: (token: string, uploadIds: number[]) =>
    request<Analysis>("/reports/combined", {
      method: "POST",
      body: JSON.stringify({ upload_ids: uploadIds })
    }, token),

  saveMapping: (token: string, uploadId: number, mapping: Record<string, string>) =>
    request<{ id: number; status: string }>(`/analysis/${uploadId}/mapping`, {
      method: "POST",
      body: JSON.stringify({ mapping })
    }, token)
};
