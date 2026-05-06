MARKETPLACE_PROVIDERS = [
    {"id": "trendyol", "label": "Trendyol", "pulls": ["orders", "stock", "invoices"], "frequency": "1-4x/day"},
    {"id": "hepsiburada", "label": "Hepsiburada", "pulls": ["orders", "stock", "invoices"], "frequency": "1-4x/day"},
    {"id": "amazon_tr", "label": "Amazon TR", "pulls": ["orders", "stock", "settlements"], "frequency": "1-4x/day"},
    {"id": "n11", "label": "N11", "pulls": ["orders", "stock", "invoices"], "frequency": "1-4x/day"},
    {"id": "ciceksepeti", "label": "Çiçeksepeti", "pulls": ["orders", "stock", "invoices"], "frequency": "1-4x/day"},
]

ACCOUNTING_PROVIDERS = [
    {"id": "logo", "label": "Logo", "pulls": ["e_invoice", "ledger", "expenses"]},
    {"id": "mikro", "label": "Mikro", "pulls": ["e_invoice", "ledger", "expenses"]},
    {"id": "parasut", "label": "Paraşüt", "pulls": ["e_invoice", "sales", "expenses"]},
]

SHIPPING_PROVIDERS = [
    {"id": "aras", "label": "Aras Kargo", "pulls": ["shipping_cost", "delivery_status", "delivery_time"]},
    {"id": "mng", "label": "MNG Kargo", "pulls": ["shipping_cost", "delivery_status", "delivery_time"]},
    {"id": "yurtici", "label": "Yurtiçi Kargo", "pulls": ["shipping_cost", "delivery_status", "delivery_time"]},
    {"id": "ptt", "label": "PTT Kargo", "pulls": ["shipping_cost", "delivery_status", "delivery_time"]},
]

ALERT_TEMPLATES = [
    {"event": "stock_low", "severity": "critical", "message_tr": "Stokta kalan gün kritik seviyeye indi."},
    {"event": "competitor_price_lower", "severity": "warning", "message_tr": "Rakip fiyatı sizin fiyatınızın altına indi."},
    {"event": "cash_balance_low", "severity": "critical", "message_tr": "Nakit bakiyesi yaklaşan ödemeler için yetersiz."},
    {"event": "return_rate_high", "severity": "warning", "message_tr": "İade oranı eşik değerin üzerine çıktı."},
    {"event": "roas_loss", "severity": "critical", "message_tr": "Reklam kampanyası zarar bölgesinde."},
]

ROLE_DEFINITIONS = [
    {"id": "admin", "label_tr": "Admin", "permissions": ["all"]},
    {"id": "finance", "label_tr": "Finans Sorumlusu", "permissions": ["financial_reports", "cash_flow", "tax"]},
    {"id": "marketing", "label_tr": "Pazarlama Sorumlusu", "permissions": ["ads", "roas", "competitors"]},
    {"id": "operations", "label_tr": "Operasyon Sorumlusu", "permissions": ["stock", "shipping", "returns"]},
    {"id": "readonly", "label_tr": "Salt Okunur", "permissions": ["read_dashboard"]},
]

BUSINESS_MODELS = [
    {"id": "excel_template", "label_tr": "Excel Şablon Satış", "price_tr": "1.500-3.000 TL tek seferlik"},
    {"id": "saas", "label_tr": "SaaS Platform", "price_tr": "Starter 299 TL / Pro 799 TL / Enterprise 1.999 TL"},
    {"id": "hybrid", "label_tr": "Hibrit Model", "price_tr": "3.500 TL setup + 299 TL/ay"},
    {"id": "consulting", "label_tr": "Danışmanlık + Yazılım", "price_tr": "15.000-50.000 TL"},
]

FORECAST_MODULES = [
    "30/60/90 gün satış tahmini",
    "Mevsimsellik analizi",
    "Stok planlama önerisi",
    "Aylık gelir-gider projeksiyonu",
    "Nakit akış tahmini",
    "Reklam bütçesi optimizasyonu",
    "Fiyat / reklam / ürün çıkarma senaryo analizi",
]


def platform_catalog() -> dict:
    return {
        "providers": {
            "marketplaces": MARKETPLACE_PROVIDERS,
            "accounting": ACCOUNTING_PROVIDERS,
            "shipping": SHIPPING_PROVIDERS,
        },
        "dashboard_exports": ["power_bi", "tableau", "excel_pivot", "email_weekly", "whatsapp", "telegram"],
        "alert_templates": ALERT_TEMPLATES,
        "roles": ROLE_DEFINITIONS,
        "business_models": BUSINESS_MODELS,
        "forecast_modules": FORECAST_MODULES,
        "crm_modules": ["RFM segmentation", "LTV", "Churn", "Best customers"],
        "tax_modules": ["KDV", "Stopaj", "e-Arşiv/e-Fatura", "SGK prim matrahı"],
    }
