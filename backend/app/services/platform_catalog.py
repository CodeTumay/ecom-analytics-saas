DATA_SOURCES = [
    {"id": "csv_excel", "label": "CSV / Excel Upload", "pulls": ["sales", "inventory", "costs", "stores"], "frequency": "manual"},
    {"id": "shopify", "label": "Shopify", "pulls": ["online_sales", "products", "inventory"], "frequency": "planned"},
    {"id": "woocommerce", "label": "WooCommerce", "pulls": ["online_sales", "products", "inventory"], "frequency": "planned"},
    {"id": "ikas", "label": "ikas", "pulls": ["orders", "inventory", "returns"], "frequency": "planned"},
    {"id": "ticimax", "label": "Ticimax", "pulls": ["orders", "stock", "customers"], "frequency": "planned"},
    {"id": "nebim", "label": "Nebim V3", "pulls": ["pos_sales", "stock", "stores"], "frequency": "planned"},
    {"id": "logo", "label": "Logo", "pulls": ["costs", "ledger", "cash"], "frequency": "planned"},
    {"id": "mikro", "label": "Mikro", "pulls": ["costs", "ledger", "cash"], "frequency": "planned"},
    {"id": "parasut", "label": "Paraşüt", "pulls": ["invoices", "expenses", "collections"], "frequency": "planned"},
]

ALERT_TEMPLATES = [
    {"event": "reorder_risk", "severity": "critical", "message_tr": "Hero ürün stok günleri kritik seviyeye indi."},
    {"event": "dead_stock", "severity": "warning", "message_tr": "Nakit bağlayan yavaş dönen stok tespit edildi."},
    {"event": "store_transfer", "severity": "warning", "message_tr": "Mağazalar arası transfer fırsatı var."},
    {"event": "hero_collection", "severity": "success", "message_tr": "Yatırımcı hikâyesinde kullanılabilecek koleksiyon büyümesi var."},
]

ROLE_DEFINITIONS = [
    {"id": "founder", "label_tr": "Kurucu / CEO", "permissions": ["ceo_dashboard", "investor_reports", "recommendations"]},
    {"id": "retail_ops", "label_tr": "Retail Operasyon", "permissions": ["stores", "transfers", "inventory"]},
    {"id": "buyer", "label_tr": "Buying / Koleksiyon", "permissions": ["collections", "reorder", "markdowns"]},
    {"id": "investor", "label_tr": "Yatırımcı / Board", "permissions": ["board_report", "kpi_export"]},
]

BUSINESS_MODELS = [
    {"id": "retail_health_audit", "label_tr": "7 Günlük Retail Health Audit", "price_tr": "$300-1.500"},
    {"id": "starter", "label_tr": "Starter: 1 mağaza / butik marka", "price_tr": "$99 / ay"},
    {"id": "growth", "label_tr": "Growth: 2-5 mağaza", "price_tr": "$249-399 / ay"},
    {"id": "pro", "label_tr": "Pro: 5-20 mağaza", "price_tr": "$599-999 / ay"},
]

REPORT_EXPORTS = [
    "PDF retail health report",
    "Investor / board summary",
    "KPI export",
    "PowerPoint outline",
    "Canva-ready story blocks",
]

FORECAST_MODULES = [
    "30 günlük reorder listesi",
    "Mağazalar arası transfer önerileri",
    "Dead stock / markdown listesi",
    "Hero collection growth story",
    "Yeni koleksiyon satın alma miktarı önerisi",
]


def platform_catalog() -> dict:
    return {
        "providers": {
            "data_sources": DATA_SOURCES,
            "accounting": [],
        },
        "dashboard_exports": REPORT_EXPORTS,
        "alert_templates": ALERT_TEMPLATES,
        "roles": ROLE_DEFINITIONS,
        "business_models": BUSINESS_MODELS,
        "forecast_modules": FORECAST_MODULES,
        "crm_modules": ["High-value customer cohort", "Repeat purchase signal"],
        "tax_modules": [],
    }
