from dataclasses import dataclass


@dataclass(frozen=True)
class ReportField:
    key: str
    label_tr: str
    label_en: str
    required: bool
    kind: str
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class ReportDefinition:
    id: str
    label_tr: str
    label_en: str
    description_tr: str
    description_en: str
    fields: tuple[ReportField, ...]

    @property
    def field_keys(self) -> list[str]:
        return [field.key for field in self.fields]

    @property
    def required_fields(self) -> list[str]:
        return [field.key for field in self.fields if field.required]


REPORTS: dict[str, ReportDefinition] = {
    "profitability": ReportDefinition(
        "profitability",
        "Karlılık",
        "Profitability",
        "Ürün/sipariş bazında net kar, marj ve maliyet kırılımı.",
        "Product/order level net profit, margin, and cost breakdown.",
        (
            ReportField("product_name", "Ürün adı", "Product name", True, "text", ("product", "product name", "urun adi", "ürün adı", "sku", "title", "item", "name")),
            ReportField("revenue", "Ciro", "Revenue", True, "number", ("revenue", "sales", "satis", "satış", "ciro", "gelir", "total", "price", "amount")),
            ReportField("cost", "Ürün maliyeti", "Product cost", True, "number", ("cost", "cogs", "maliyet", "urun maliyeti", "ürün maliyeti", "buying price", "unit cost")),
            ReportField("commission", "Komisyon", "Commission", False, "number", ("commission", "komisyon", "marketplace fee", "referral fee")),
            ReportField("shipping", "Kargo", "Shipping", False, "number", ("shipping", "shipment", "delivery", "cargo", "kargo", "nakliye")),
            ReportField("ads_spend", "Reklam gideri", "Ads spend", False, "number", ("ads", "ad spend", "adspend", "advertising", "marketing", "ppc", "reklam", "reklam gideri")),
        ),
    ),
    "income_expense": ReportDefinition(
        "income_expense",
        "Gelir-Gider",
        "Income & Expense",
        "Kategori bazında gelir, gider ve dönemsel net sonuç.",
        "Category-level income, expenses, and net result.",
        (
            ReportField("date", "Tarih", "Date", False, "date", ("date", "tarih", "created at", "order date")),
            ReportField("category", "Kategori", "Category", True, "text", ("category", "kategori", "expense category", "gelir gider kategorisi")),
            ReportField("description", "Açıklama", "Description", False, "text", ("description", "aciklama", "açıklama", "note")),
            ReportField("income", "Gelir", "Income", False, "number", ("income", "gelir", "revenue", "ciro")),
            ReportField("expense", "Gider", "Expense", False, "number", ("expense", "gider", "cost", "maliyet")),
            ReportField("amount", "Tutar", "Amount", True, "number", ("amount", "tutar", "value", "net amount")),
            ReportField("type", "Tip", "Type", False, "text", ("type", "tip", "income expense type", "gelir gider tipi")),
        ),
    ),
    "ads_performance": ReportDefinition(
        "ads_performance",
        "Reklam ve ROAS",
        "Ads & ROAS",
        "Kampanya harcaması, reklam cirosu ve temel ROAS takibi.",
        "Campaign spend, attributed revenue, and basic ROAS tracking.",
        (
            ReportField("campaign", "Kampanya", "Campaign", True, "text", ("campaign", "kampanya", "ad campaign", "campaign name")),
            ReportField("product_name", "Ürün adı", "Product name", False, "text", ("product", "product name", "urun adi", "ürün adı", "sku")),
            ReportField("ads_spend", "Reklam gideri", "Ads spend", True, "number", ("ads", "ad spend", "spend", "cost", "reklam", "reklam gideri")),
            ReportField("revenue", "Reklam cirosu", "Attributed revenue", False, "number", ("revenue", "sales", "conversion value", "ciro", "gelir")),
            ReportField("impressions", "Gösterim", "Impressions", False, "number", ("impressions", "gosterim", "gösterim")),
            ReportField("clicks", "Tıklama", "Clicks", False, "number", ("clicks", "tiklama", "tıklama")),
            ReportField("orders", "Sipariş", "Orders", False, "number", ("orders", "order count", "siparis", "sipariş")),
        ),
    ),
    "sales_performance": ReportDefinition(
        "sales_performance",
        "Satış Performansı",
        "Sales Performance",
        "Ürün, adet, sipariş ve indirim bazlı satış görünümü.",
        "Product, units, orders, discount, and sales performance view.",
        (
            ReportField("product_name", "Ürün adı", "Product name", True, "text", ("product", "product name", "urun adi", "ürün adı", "sku", "title")),
            ReportField("date", "Tarih", "Date", False, "date", ("date", "tarih", "order date")),
            ReportField("revenue", "Ciro", "Revenue", True, "number", ("revenue", "sales", "ciro", "gelir", "total")),
            ReportField("units", "Adet", "Units", False, "number", ("units", "quantity", "adet", "miktar")),
            ReportField("orders", "Sipariş", "Orders", False, "number", ("orders", "order count", "siparis", "sipariş")),
            ReportField("discount", "İndirim", "Discount", False, "number", ("discount", "indirim", "coupon")),
        ),
    ),
    "shipping_logistics": ReportDefinition(
        "shipping_logistics",
        "Kargo ve Lojistik",
        "Shipping & Logistics",
        "Kargo maliyeti, taşıyıcı ve teslimat performansı.",
        "Shipping cost, carrier, and delivery performance.",
        (
            ReportField("product_name", "Ürün adı", "Product name", False, "text", ("product", "product name", "urun adi", "ürün adı", "sku")),
            ReportField("order_id", "Sipariş no", "Order ID", False, "text", ("order id", "order", "siparis no", "sipariş no")),
            ReportField("shipping", "Kargo maliyeti", "Shipping cost", True, "number", ("shipping", "shipment cost", "cargo", "kargo", "nakliye")),
            ReportField("carrier", "Taşıyıcı", "Carrier", False, "text", ("carrier", "tasiyici", "taşıyıcı", "cargo company")),
            ReportField("status", "Durum", "Status", False, "text", ("status", "durum", "delivery status")),
            ReportField("revenue", "Ciro", "Revenue", False, "number", ("revenue", "sales", "ciro", "gelir")),
        ),
    ),
    "returns_cancellations": ReportDefinition(
        "returns_cancellations",
        "İade ve İptal",
        "Returns & Cancellations",
        "İade/iptal tutarları, nedenler ve ürün etkisi.",
        "Refund/cancellation amounts, reasons, and product impact.",
        (
            ReportField("product_name", "Ürün adı", "Product name", True, "text", ("product", "product name", "urun adi", "ürün adı", "sku")),
            ReportField("return_amount", "İade tutarı", "Return amount", True, "number", ("return amount", "refund", "refund amount", "iade", "iade tutari", "iade tutarı")),
            ReportField("revenue", "Orijinal ciro", "Original revenue", False, "number", ("revenue", "sales", "ciro", "gelir")),
            ReportField("quantity", "Adet", "Quantity", False, "number", ("quantity", "qty", "adet", "miktar")),
            ReportField("reason", "Neden", "Reason", False, "text", ("reason", "neden", "return reason")),
        ),
    ),
    "inventory": ReportDefinition(
        "inventory",
        "Stok ve Devir Hızı",
        "Inventory Turnover",
        "Stok adedi, stok maliyeti ve envanter değeri.",
        "Stock quantity, unit cost, and inventory value.",
        (
            ReportField("product_name", "Ürün adı", "Product name", True, "text", ("product", "product name", "urun adi", "ürün adı", "sku")),
            ReportField("stock", "Stok", "Stock", True, "number", ("stock", "inventory", "stok", "available stock")),
            ReportField("unit_cost", "Birim maliyet", "Unit cost", True, "number", ("unit cost", "cost", "birim maliyet", "maliyet")),
            ReportField("inventory_value", "Stok değeri", "Inventory value", False, "number", ("inventory value", "stock value", "stok degeri", "stok değeri")),
        ),
    ),
}


def get_report_definition(report_type: str | None) -> ReportDefinition:
    return REPORTS.get(report_type or "profitability", REPORTS["profitability"])


def serialize_report_catalog() -> list[dict]:
    return [
        {
            "id": report.id,
            "label_tr": report.label_tr,
            "label_en": report.label_en,
            "description_tr": report.description_tr,
            "description_en": report.description_en,
            "fields": [
                {
                    "key": field.key,
                    "label_tr": field.label_tr,
                    "label_en": field.label_en,
                    "required": field.required,
                    "kind": field.kind,
                    "aliases": list(field.aliases),
                }
                for field in report.fields
            ],
        }
        for report in REPORTS.values()
    ]
