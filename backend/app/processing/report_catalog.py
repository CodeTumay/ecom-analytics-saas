from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ReportField:
    key: str
    label_tr: str
    label_en: str
    required: bool
    kind: str
    aliases: tuple[str, ...]
    formula_tr: str = ""
    formula_en: str = ""


@dataclass(frozen=True)
class ReportDefinition:
    id: str
    category: str
    label_tr: str
    label_en: str
    description_tr: str
    description_en: str
    fields: tuple[ReportField, ...]
    logic_tr: tuple[str, ...] = field(default_factory=tuple)
    logic_en: tuple[str, ...] = field(default_factory=tuple)

    @property
    def field_keys(self) -> list[str]:
        return [field.key for field in self.fields]

    @property
    def required_fields(self) -> list[str]:
        return [field.key for field in self.fields if field.required]


RETAIL_FIELDS = (
    ReportField("date", "Tarih", "Date", False, "date", ("date", "tarih", "sales date", "satış tarihi")),
    ReportField("store_name", "Mağaza", "Store", False, "text", ("store", "store name", "magaza", "mağaza", "lokasyon")),
    ReportField("store_sqm", "Mağaza m²", "Store m²", False, "number", ("sqm", "m2", "m²", "metrekare", "store sqm")),
    ReportField("channel", "Kanal", "Channel", False, "text", ("channel", "kanal", "online", "offline")),
    ReportField("sku", "SKU", "SKU", False, "text", ("sku", "stok kodu", "ürün kodu", "product code")),
    ReportField("product_name", "Ürün", "Product", True, "text", ("product", "product name", "ürün", "urun", "ürün adı", "title")),
    ReportField("collection", "Koleksiyon", "Collection", False, "text", ("collection", "koleksiyon", "season", "drop")),
    ReportField("category", "Kategori", "Category", False, "text", ("category", "kategori", "product type")),
    ReportField("material", "Malzeme", "Material", False, "text", ("material", "malzeme", "inci", "doğal taş", "gumus", "gümüş")),
    ReportField("units_sold", "Satış Adedi", "Units Sold", False, "number", ("units sold", "quantity", "adet", "satış adedi")),
    ReportField("revenue", "Ciro", "Revenue", True, "number", ("revenue", "sales", "net sales", "ciro", "satış", "satis")),
    ReportField("cost", "Ürün Maliyeti", "Product Cost", True, "number", ("cost", "unit cost", "cogs", "maliyet", "ürün maliyeti")),
    ReportField("selling_price", "Satış Fiyatı", "Selling Price", False, "number", ("price", "selling price", "satış fiyatı", "fiyat")),
    ReportField("stock", "Stok", "Stock", False, "number", ("stock", "inventory", "stok", "stok adedi")),
    ReportField("footfall", "Ziyaretçi", "Footfall", False, "number", ("footfall", "visitor", "traffic", "ziyaretçi", "ziyaretci")),
    ReportField("conversion_rate", "Conversion %", "Conversion %", False, "number", ("conversion", "conversion rate", "dönüşüm", "donusum")),
    ReportField("sell_through", "Sell-through %", "Sell-through %", False, "number", ("sell through", "sell-through", "satılan stok yüzdesi")),
    ReportField("inventory_value", "Stok Değeri", "Inventory Value", False, "number", ("inventory value", "stok değeri", "stok degeri")),
)


REPORTS: dict[str, ReportDefinition] = {
    "retail_health": ReportDefinition(
        id="retail_health",
        category="ceo",
        label_tr="Retail Health Report",
        label_en="Retail Health Report",
        description_tr="Son 6 ay satış ve stok datasından ürün, mağaza, stok ve koleksiyon aksiyon planı.",
        description_en="Action plan for products, stores, stock, and collections from retail sales and inventory data.",
        fields=RETAIL_FIELDS,
        logic_tr=(
            "Sell-through yüksek + stok düşük = yeniden üretim önerisi",
            "Marj yüksek + satış artıyor = hero product",
            "Stok yüksek + satış düşük = markdown / transfer",
            "Online iyi, mağaza kötü = merchandising veya lokasyon uyarısı",
        ),
        logic_en=(
            "High sell-through + low stock = reorder recommendation",
            "High margin + rising sales = hero product",
            "High stock + low sales = markdown / transfer",
            "Strong online and weak store performance = merchandising or location issue",
        ),
    ),
    "ceo_dashboard": ReportDefinition(
        id="ceo_dashboard",
        category="ceo",
        label_tr="CEO Dashboard",
        label_en="CEO Dashboard",
        description_tr="Ciro, brüt marj, mağaza başı ciro, revenue per m², sepet, conversion ve sell-through.",
        description_en="Revenue, gross margin, store revenue, revenue per m², basket, conversion, and sell-through.",
        fields=RETAIL_FIELDS,
    ),
    "store_performance": ReportDefinition(
        id="store_performance",
        category="store",
        label_tr="Store Performance",
        label_en="Store Performance",
        description_tr="Mağaza verimliliği, stok kaynaklı satış kaybı, conversion ve mağazalar arası transfer sinyali.",
        description_en="Store productivity, missed sales from stock gaps, conversion, and transfer signals.",
        fields=RETAIL_FIELDS,
    ),
    "product_collection": ReportDefinition(
        id="product_collection",
        category="product",
        label_tr="Product & Collection Intelligence",
        label_en="Product & Collection Intelligence",
        description_tr="SKU, koleksiyon, kategori, malzeme ve fiyat bandı bazında büyütülecek veya eritilecek ürünler.",
        description_en="SKU, collection, category, material, and price-band intelligence for growth and markdown decisions.",
        fields=RETAIL_FIELDS,
    ),
    "reorder_transfer": ReportDefinition(
        id="reorder_transfer",
        category="action",
        label_tr="Reorder & Transfer Engine",
        label_en="Reorder & Transfer Engine",
        description_tr="Yeniden üretim, mağazalar arası transfer, kritik stok, dead stock ve markdown önerileri.",
        description_en="Reorder, transfer, critical stock, dead stock, and markdown recommendations.",
        fields=RETAIL_FIELDS,
    ),
    "investor_board": ReportDefinition(
        id="investor_board",
        category="board",
        label_tr="Investor / Board Report",
        label_en="Investor / Board Report",
        description_tr="Koleksiyon performansını, mağaza verimliliğini ve hero category büyüme hikayesini yatırımcı diline çevirir.",
        description_en="Turns collection performance, store productivity, and hero categories into an investor-ready story.",
        fields=RETAIL_FIELDS,
    ),
}


def get_report_definition(report_type: str | None) -> ReportDefinition:
    return REPORTS.get(report_type or "retail_health", REPORTS["retail_health"])


def serialize_report_catalog() -> list[dict]:
    return [
        {
            "id": report.id,
            "category": report.category,
            "label_tr": report.label_tr,
            "label_en": report.label_en,
            "description_tr": report.description_tr,
            "description_en": report.description_en,
            "logic_tr": list(report.logic_tr),
            "logic_en": list(report.logic_en),
            "fields": [
                {
                    "key": field.key,
                    "label_tr": field.label_tr,
                    "label_en": field.label_en,
                    "required": field.required,
                    "kind": field.kind,
                    "aliases": list(field.aliases),
                    "formula_tr": field.formula_tr,
                    "formula_en": field.formula_en,
                }
                for field in report.fields
            ],
        }
        for report in REPORTS.values()
    ]
