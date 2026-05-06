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


REPORTS: dict[str, ReportDefinition] = {
    "profitability": ReportDefinition(
        id="profitability",
        category="financial",
        label_tr="Karlılık Raporu",
        label_en="Profitability Report",
        description_tr="Sipariş ve ürün bazında net gelir, kar marjı ve gider kırılımı.",
        description_en="Order and product-level net income, margin, and expense breakdown.",
        fields=(
            ReportField("date", "Tarih", "Date", False, "date", ("date", "tarih", "islem tarihi", "işlem tarihi", "order date")),
            ReportField("order_id", "Sipariş No", "Order ID", False, "text", ("order id", "order no", "siparis no", "sipariş no", "sipariş numarası")),
            ReportField("product_name", "Ürün Adı", "Product Name", True, "text", ("product", "product name", "urun adi", "ürün adı", "sku", "title", "item", "name")),
            ReportField("revenue", "Satış Fiyatı", "Sales Price", True, "number", ("revenue", "sales", "satis fiyati", "satış fiyatı", "ciro", "gelir", "total", "price", "amount")),
            ReportField("cost", "Ürün Maliyeti", "Product Cost", True, "number", ("cost", "cogs", "maliyet", "urun maliyeti", "ürün maliyeti", "buying price", "unit cost")),
            ReportField("commission_rate", "Komisyon Oranı %", "Commission Rate %", False, "number", ("commission rate", "komisyon orani", "komisyon oranı", "komisyon %")),
            ReportField("commission", "Komisyon Tutarı", "Commission Amount", False, "number", ("commission", "komisyon", "komisyon tutari", "komisyon tutarı", "marketplace fee", "referral fee"), "=Satış Fiyatı*Komisyon Oranı/100", "=Sales Price*Commission Rate/100"),
            ReportField("shipping", "Kargo Ücreti", "Shipping Fee", False, "number", ("shipping", "shipment", "delivery", "cargo", "kargo", "kargo ücreti", "nakliye")),
            ReportField("other_expenses", "Diğer Giderler", "Other Expenses", False, "number", ("other expenses", "diger giderler", "diğer giderler", "paketleme", "depo")),
            ReportField("net_income", "Net Gelir", "Net Income", False, "number", ("net gelir", "net income", "profit", "kar", "net kar"), "=Satış-Maliyet-Komisyon-Kargo-Diğer", "=Sales-Cost-Commission-Shipping-Other"),
            ReportField("profit_margin", "Kar Marjı %", "Profit Margin %", False, "number", ("kar marji", "kar marjı", "profit margin", "margin"), "=Net Gelir/Satış*100", "=Net Income/Sales*100"),
        ),
        logic_tr=(
            "Kar marjı > %20: Yüksek Karlılık",
            "Kar marjı %10-20: Orta Karlılık",
            "Kar marjı < %10: Düşük Karlılık - incelenmeli",
        ),
        logic_en=(
            "Margin > 20%: High profitability",
            "Margin 10-20%: Medium profitability",
            "Margin < 10%: Low profitability - review required",
        ),
    ),
    "income_expense": ReportDefinition(
        id="income_expense",
        category="financial",
        label_tr="Gelir-Gider Raporu",
        label_en="Income & Expense Report",
        description_tr="Dönem bazında satış, iade, gider ve net kar/zarar analizi.",
        description_en="Period-level sales, returns, expenses, and net profit/loss analysis.",
        fields=(
            ReportField("period", "Ay", "Month", True, "text", ("month", "ay", "period", "donem", "dönem", "raporlama dönemi")),
            ReportField("gross_sales", "Toplam Satış", "Gross Sales", False, "number", ("gross sales", "toplam satis", "toplam satış", "sales", "ciro")),
            ReportField("returns", "İadeler", "Returns", False, "number", ("returns", "refunds", "iadeler", "iade")),
            ReportField("net_sales", "Net Satış", "Net Sales", True, "number", ("net sales", "net satis", "net satış", "revenue", "gelir"), "=Toplam Satış-İadeler", "=Gross Sales-Returns"),
            ReportField("product_costs", "Ürün Maliyetleri", "Product Costs", False, "number", ("product costs", "urun maliyetleri", "ürün maliyetleri", "cogs", "maliyet")),
            ReportField("marketplace_commissions", "Pazaryeri Komisyonları", "Marketplace Commissions", False, "number", ("marketplace commissions", "pazaryeri komisyonlari", "pazaryeri komisyonları", "commission", "komisyon")),
            ReportField("shipping_expenses", "Kargo Giderleri", "Shipping Expenses", False, "number", ("shipping expenses", "kargo giderleri", "shipping", "kargo")),
            ReportField("ads_expenses", "Reklam Giderleri", "Advertising Expenses", False, "number", ("ads expenses", "advertising expenses", "reklam giderleri", "ads", "reklam")),
            ReportField("operational_expenses", "Operasyonel Giderler", "Operational Expenses", False, "number", ("operational expenses", "operasyonel giderler", "depo", "personel")),
            ReportField("total_expense", "Toplam Gider", "Total Expense", False, "number", ("total expense", "toplam gider", "expenses"), "=Ürün+Komisyon+Kargo+Reklam+Operasyon", "=Product+Commission+Shipping+Ads+Operations"),
            ReportField("net_profit", "Net Kar/Zarar", "Net Profit/Loss", False, "number", ("net profit", "net kar", "kar zarar", "profit"), "=Net Satış-Toplam Gider", "=Net Sales-Total Expense"),
            ReportField("ebitda", "EBITDA", "EBITDA", False, "number", ("ebitda", "favok")),
        ),
        logic_tr=(
            "Net kar > 0: Karlı dönem",
            "Net kar < 0: Zarar - maliyet optimizasyonu gerekli",
            "Gider/Gelir oranı > %80: Yüksek gider oranı uyarısı",
        ),
        logic_en=(
            "Net profit > 0: Profitable period",
            "Net profit < 0: Loss - cost optimization required",
            "Expense/Income ratio > 80%: High expense ratio warning",
        ),
    ),
    "pricing_analysis": ReportDefinition(
        id="pricing_analysis",
        category="financial",
        label_tr="Fiyatlandırma Analizi",
        label_en="Pricing Analysis",
        description_tr="Rakip fiyatı, minimum satış fiyatı ve fiyat pozisyonu analizi.",
        description_en="Competitor price, minimum selling price, and pricing position analysis.",
        fields=(
            ReportField("sku", "Ürün SKU", "Product SKU", False, "text", ("sku", "stok kodu", "urun sku", "ürün sku")),
            ReportField("product_name", "Ürün Adı", "Product Name", True, "text", ("product", "product name", "urun adi", "ürün adı", "name")),
            ReportField("current_price", "Mevcut Satış Fiyatı", "Current Sales Price", True, "number", ("current price", "mevcut satis fiyati", "mevcut satış fiyatı", "sales price", "price")),
            ReportField("competitor_price_1", "Rakip 1 Fiyatı", "Competitor 1 Price", False, "number", ("competitor 1 price", "rakip 1 fiyati", "rakip 1 fiyatı")),
            ReportField("competitor_price_2", "Rakip 2 Fiyatı", "Competitor 2 Price", False, "number", ("competitor 2 price", "rakip 2 fiyati", "rakip 2 fiyatı")),
            ReportField("market_avg_price", "Ortalama Pazar Fiyatı", "Average Market Price", False, "number", ("market avg price", "ortalama pazar fiyati", "ortalama pazar fiyatı"), "=ORTALAMA(Rakip1:Rakip2)", "=AVERAGE(Competitor1:Competitor2)"),
            ReportField("price_gap_pct", "Fiyat Farkı %", "Price Gap %", False, "number", ("price gap", "fiyat farki", "fiyat farkı"), "=(Mevcut-Ortalama)/Ortalama*100", "=(Current-Average)/Average*100"),
            ReportField("cost", "Ürün Maliyeti", "Product Cost", True, "number", ("cost", "maliyet", "urun maliyeti", "ürün maliyeti")),
            ReportField("min_price", "Min. Satış Fiyatı", "Min. Sales Price", False, "number", ("min price", "minimum price", "min satis fiyati", "min satış fiyatı"), "=Ürün Maliyeti*1.25", "=Product Cost*1.25"),
            ReportField("suggested_price", "Önerilen Fiyat", "Suggested Price", False, "number", ("suggested price", "onerilen fiyat", "önerilen fiyat")),
            ReportField("price_status", "Fiyat Durumu", "Price Status", False, "text", ("price status", "fiyat durumu")),
        ),
        logic_tr=(
            "Fiyat farkı > %10: Fiyat düşürülmeli - rekabet riski",
            "Fiyat farkı < -%10: Fiyat artırılabilir - kar fırsatı",
            "Satış fiyatı < minimum fiyat: Uyarı - zarar riski",
        ),
        logic_en=(
            "Price gap > 10%: Consider reducing price - competition risk",
            "Price gap < -10%: Price can be increased - margin opportunity",
            "Sales price < minimum price: Warning - loss risk",
        ),
    ),
    "cash_flow": ReportDefinition(
        id="cash_flow",
        category="financial",
        label_tr="Nakit Akışı Raporu",
        label_en="Cash Flow Report",
        description_tr="Giren/çıkan nakit, bakiye ve tahsilat/ödeme riski takibi.",
        description_en="Cash-in/out, balance, expected collection, and payment risk tracking.",
        fields=(
            ReportField("date", "Tarih", "Date", True, "date", ("date", "tarih", "islem tarihi", "işlem tarihi")),
            ReportField("transaction_type", "İşlem Tipi", "Transaction Type", True, "text", ("transaction type", "islem tipi", "işlem tipi", "type", "tip")),
            ReportField("category", "Kategori", "Category", True, "text", ("category", "kategori", "sales", "satis", "satış", "gider")),
            ReportField("description", "Açıklama", "Description", False, "text", ("description", "aciklama", "açıklama", "note")),
            ReportField("cash_in", "Giren Nakit", "Cash In", False, "number", ("cash in", "giren nakit", "inflow", "gelir")),
            ReportField("cash_out", "Çıkan Nakit", "Cash Out", False, "number", ("cash out", "cikan nakit", "çıkan nakit", "outflow", "gider")),
            ReportField("daily_balance", "Günlük Bakiye", "Daily Balance", False, "number", ("daily balance", "gunluk bakiye", "günlük bakiye"), "=Önceki Bakiye+Giren-Çıkan", "=Previous Balance+Cash In-Cash Out"),
            ReportField("cumulative_balance", "Kümülatif Bakiye", "Cumulative Balance", False, "number", ("cumulative balance", "kumulatif bakiye", "kümülatif bakiye")),
            ReportField("expected_collection", "Beklenen Tahsilat", "Expected Collection", False, "number", ("expected collection", "beklenen tahsilat")),
            ReportField("expected_payment", "Beklenen Ödeme", "Expected Payment", False, "number", ("expected payment", "beklenen odeme", "beklenen ödeme")),
        ),
        logic_tr=(
            "Günlük bakiye < 0: Nakit sıkışıklığı uyarısı",
            "Beklenen tahsilat - beklenen ödeme < 0: Önümüzdeki dönem risk",
        ),
        logic_en=(
            "Daily balance < 0: Cash squeeze warning",
            "Expected collection - expected payment < 0: Upcoming period risk",
        ),
    ),
    "sales_performance": ReportDefinition(
        id="sales_performance",
        category="performance",
        label_tr="Satış Performansı",
        label_en="Sales Performance",
        description_tr="Sipariş, ciro, ortalama sepet, büyüme ve hedef gerçekleşme takibi.",
        description_en="Orders, revenue, average basket, growth, and target achievement tracking.",
        fields=(
            ReportField("date", "Tarih", "Date", False, "date", ("date", "tarih", "sales date", "satis tarihi", "satış tarihi")),
            ReportField("day", "Gün", "Day", False, "text", ("day", "gun", "gün"), '=TEXT(Tarih,"dddd")', '=TEXT(Date,"dddd")'),
            ReportField("week", "Hafta", "Week", False, "number", ("week", "hafta"), "=WEEKNUM(Tarih)", "=WEEKNUM(Date)"),
            ReportField("month", "Ay", "Month", False, "text", ("month", "ay"), '=TEXT(Tarih,"MMMM")', '=TEXT(Date,"MMMM")'),
            ReportField("order_count", "Sipariş Sayısı", "Order Count", True, "number", ("order count", "orders", "siparis sayisi", "sipariş sayısı")),
            ReportField("revenue", "Satış Tutarı", "Sales Amount", True, "number", ("sales amount", "satis tutari", "satış tutarı", "revenue", "ciro")),
            ReportField("average_basket", "Ortalama Sepet", "Average Basket", False, "number", ("average basket", "ortalama sepet"), "=Satış Tutarı/Sipariş Sayısı", "=Sales Amount/Order Count"),
            ReportField("previous_year_same_day", "Önceki Yıl Aynı Gün", "Previous Year Same Day", False, "number", ("previous year same day", "onceki yil ayni gun", "önceki yıl aynı gün")),
            ReportField("growth_pct", "Büyüme %", "Growth %", False, "number", ("growth", "buyume", "büyüme"), "=(Bu Dönem-Geçen Dönem)/Geçen Dönem*100", "=(Current-Previous)/Previous*100"),
            ReportField("target", "Hedef", "Target", False, "number", ("target", "hedef")),
            ReportField("target_completion_pct", "Hedef Gerçekleşme %", "Target Completion %", False, "number", ("target completion", "hedef gerceklesme", "hedef gerçekleşme"), "=Satış/Hedef*100", "=Sales/Target*100"),
        ),
        logic_tr=(
            "Hedef gerçekleşme > %100: Hedef aşıldı",
            "Hedef gerçekleşme %80-100: Hedefe yakın",
            "Hedef gerçekleşme < %80: Performans düşük - aksiyon gerekli",
            "Büyüme < %0: Negatif büyüme - analiz gerekli",
        ),
        logic_en=(
            "Target completion > 100%: Target exceeded",
            "Target completion 80-100%: Close to target",
            "Target completion < 80%: Low performance - action required",
            "Growth < 0%: Negative growth - analysis required",
        ),
    ),
    "product_analysis": ReportDefinition(
        id="product_analysis",
        category="performance",
        label_tr="Ürün Analizi",
        label_en="Product Analysis",
        description_tr="Satış adedi, iade oranı, stok devir hızı ve ABC sınıfı analizi.",
        description_en="Units sold, return rate, stock turnover, and ABC class analysis.",
        fields=(
            ReportField("sku", "Ürün SKU", "Product SKU", False, "text", ("sku", "stok kodu", "urun sku", "ürün sku")),
            ReportField("product_name", "Ürün Adı", "Product Name", True, "text", ("product", "product name", "urun adi", "ürün adı", "name")),
            ReportField("category", "Kategori", "Category", False, "text", ("category", "kategori")),
            ReportField("units_sold", "Satış Adedi", "Units Sold", True, "number", ("units sold", "satis adedi", "satış adedi", "quantity", "adet")),
            ReportField("revenue", "Satış Tutarı", "Sales Amount", True, "number", ("sales amount", "satis tutari", "satış tutarı", "revenue", "ciro")),
            ReportField("return_units", "İade Adedi", "Return Units", False, "number", ("return units", "iade adedi", "returns")),
            ReportField("return_rate", "İade Oranı %", "Return Rate %", False, "number", ("return rate", "iade orani", "iade oranı"), "=İade Adedi/Satış Adedi*100", "=Return Units/Units Sold*100"),
            ReportField("average_price", "Ortalama Fiyat", "Average Price", False, "number", ("average price", "ortalama fiyat"), "=Satış Tutarı/Satış Adedi", "=Sales Amount/Units Sold"),
            ReportField("stock", "Stok Miktarı", "Stock Quantity", False, "number", ("stock", "stok", "stok miktari", "stok miktarı")),
            ReportField("stock_turnover", "Stok Devir Hızı", "Stock Turnover", False, "number", ("stock turnover", "stok devir", "stok devir hizi", "stok devir hızı"), "=Satış Adedi/Ortalama Stok", "=Units Sold/Average Stock"),
            ReportField("revenue_share", "Toplam Cirodaki Pay %", "Revenue Share %", False, "number", ("revenue share", "ciro payi", "ciro payı"), "=Satış Tutarı/TOPLAM(Satış Tutarı)*100", "=Sales Amount/SUM(Sales Amount)*100"),
            ReportField("abc_class", "ABC Sınıfı", "ABC Class", False, "text", ("abc class", "abc sinifi", "abc sınıfı")),
        ),
        logic_tr=(
            "Kümülatif ciro payı <= %80: A sınıfı",
            "Kümülatif ciro payı %80-95: B sınıfı",
            "Kümülatif ciro payı > %95: C sınıfı",
            "İade oranı > %10: Yüksek iade - kalite kontrolü",
            "Stok devir < 2: Yavaş hareket eden stok",
        ),
        logic_en=(
            "Cumulative revenue share <= 80%: A class",
            "Cumulative revenue share 80-95%: B class",
            "Cumulative revenue share > 95%: C class",
            "Return rate > 10%: High returns - quality control",
            "Stock turnover < 2: Slow-moving stock",
        ),
    ),
    "trends": ReportDefinition(
        id="trends",
        category="performance",
        label_tr="Trendler",
        label_en="Trends",
        description_tr="Dönemsel satış, hareketli ortalama, tahmin ve limit takibi.",
        description_en="Period sales, moving average, forecast, and limit tracking.",
        fields=(
            ReportField("period", "Dönem", "Period", True, "text", ("period", "donem", "dönem", "week", "hafta", "month", "ay")),
            ReportField("revenue", "Satış Tutarı", "Sales Amount", True, "number", ("sales amount", "satis tutari", "satış tutarı", "revenue", "ciro")),
            ReportField("moving_average", "Hareketli Ortalama", "Moving Average", False, "number", ("moving average", "hareketli ortalama"), "=ORTALAMA(Son 4 dönem)", "=AVERAGE(Last 4 periods)"),
            ReportField("trend_direction", "Trend Yönü", "Trend Direction", False, "text", ("trend direction", "trend yonu", "trend yönü")),
            ReportField("seasonality_index", "Mevsimsel İndeks", "Seasonality Index", False, "number", ("seasonality index", "mevsimsel indeks"), "=Satış/Yıllık Ortalama", "=Sales/Annual Average"),
            ReportField("forecast", "Tahmin", "Forecast", False, "number", ("forecast", "tahmin")),
            ReportField("upper_limit", "Üst Limit", "Upper Limit", False, "number", ("upper limit", "ust limit", "üst limit"), "=Hareketli Ortalama*1.2", "=Moving Average*1.2"),
            ReportField("lower_limit", "Alt Limit", "Lower Limit", False, "number", ("lower limit", "alt limit"), "=Hareketli Ortalama*0.8", "=Moving Average*0.8"),
        ),
        logic_tr=(
            "Satış > üst limit: Olağanüstü performans - stok kontrolü",
            "Satış < alt limit: Beklenenden düşük - kampanya düşünülebilir",
            "3 ardışık dönem düşüş: Negatif trend - acil müdahale",
        ),
        logic_en=(
            "Sales > upper limit: Exceptional performance - check stock",
            "Sales < lower limit: Below expectation - consider campaign",
            "3 consecutive declines: Negative trend - urgent action",
        ),
    ),
    "commissions": ReportDefinition(
        id="commissions",
        category="operations",
        label_tr="Komisyonlar",
        label_en="Commissions",
        description_tr="Pazaryeri komisyonu, ek hizmet bedelleri ve platform maliyet oranı.",
        description_en="Marketplace commission, additional service fees, and platform cost ratio.",
        fields=(
            ReportField("marketplace", "Pazaryeri", "Marketplace", True, "text", ("marketplace", "pazaryeri", "platform")),
            ReportField("category", "Kategori", "Category", False, "text", ("category", "kategori")),
            ReportField("commission_rate", "Komisyon Oranı %", "Commission Rate %", False, "number", ("commission rate", "komisyon orani", "komisyon oranı")),
            ReportField("revenue", "Satış Tutarı", "Sales Amount", True, "number", ("sales amount", "satis tutari", "satış tutarı", "revenue", "ciro")),
            ReportField("commission", "Komisyon Tutarı", "Commission Amount", False, "number", ("commission", "komisyon", "komisyon tutari", "komisyon tutarı"), "=Satış Tutarı*Komisyon Oranı/100", "=Sales Amount*Commission Rate/100"),
            ReportField("additional_fees", "Ek Hizmet Bedelleri", "Additional Fees", False, "number", ("additional fees", "ek hizmet bedelleri", "fulfilment", "fulfillment")),
            ReportField("platform_cost", "Toplam Platform Maliyeti", "Total Platform Cost", False, "number", ("platform cost", "toplam platform maliyeti"), "=Komisyon+Ek Hizmet", "=Commission+Additional Fees"),
            ReportField("cost_sales_ratio", "Maliyet/Satış Oranı %", "Cost/Sales Ratio %", False, "number", ("cost sales ratio", "maliyet satis orani", "maliyet satış oranı"), "=Platform Maliyeti/Satış*100", "=Platform Cost/Sales*100"),
        ),
        logic_tr=(
            "Maliyet/Satış > %20: Yüksek platform maliyeti",
            "Düşük komisyonlu platformlar alternatif kanal olarak değerlendirilebilir",
        ),
        logic_en=(
            "Cost/Sales > 20%: High platform cost",
            "Lower-commission marketplaces can be evaluated as alternative channels",
        ),
    ),
    "shipping_logistics": ReportDefinition(
        id="shipping_logistics",
        category="operations",
        label_tr="Kargo ve Lojistik",
        label_en="Shipping & Logistics",
        description_tr="Kargo maliyeti, şehir/bölge, teslimat süresi ve hasar/kayıp takibi.",
        description_en="Shipping cost, city/region, delivery time, and damaged/lost shipment tracking.",
        fields=(
            ReportField("order_id", "Sipariş No", "Order ID", False, "text", ("order id", "order no", "siparis no", "sipariş no")),
            ReportField("carrier", "Kargo Firması", "Carrier", True, "text", ("carrier", "kargo firmasi", "kargo firması", "cargo company")),
            ReportField("delivery_city", "Teslimat Şehri", "Delivery City", False, "text", ("delivery city", "teslimat sehri", "teslimat şehri", "city", "il")),
            ReportField("region", "Bölge", "Region", False, "text", ("region", "bolge", "bölge")),
            ReportField("shipping", "Kargo Ücreti", "Shipping Fee", True, "number", ("shipping", "shipment cost", "cargo", "kargo", "kargo ucreti", "kargo ücreti")),
            ReportField("weight_kg", "Ağırlık (kg)", "Weight (kg)", False, "number", ("weight", "agirlik", "ağırlık", "kg")),
            ReportField("desi", "Desi", "Volumetric Weight", False, "number", ("desi", "volumetric weight")),
            ReportField("shipping_revenue_ratio", "Kargo/Satış Oranı %", "Shipping/Sales Ratio %", False, "number", ("shipping sales ratio", "kargo satis orani", "kargo satış oranı"), "=Kargo/Satış*100", "=Shipping/Sales*100"),
            ReportField("delivery_days", "Teslimat Süresi (gün)", "Delivery Days", False, "number", ("delivery days", "teslimat suresi", "teslimat süresi")),
            ReportField("damaged_lost", "Hasarlı/Kayıp", "Damaged/Lost", False, "text", ("damaged lost", "hasarli kayip", "hasarlı kayıp", "damage", "lost")),
            ReportField("revenue", "Satış Tutarı", "Sales Amount", False, "number", ("sales amount", "satis tutari", "satış tutarı", "revenue", "ciro")),
        ),
        logic_tr=(
            "Teslimat süresi > 5 gün: Geç teslimat riski",
            "Kargo/Satış > %15: Yüksek kargo maliyeti",
            "Hasar/kayıp oranı > %2: Kargo firması değerlendirmesi",
        ),
        logic_en=(
            "Delivery days > 5: Late delivery risk",
            "Shipping/Sales > 15%: High shipping cost",
            "Damaged/lost ratio > 2%: Review carrier",
        ),
    ),
    "ads_performance": ReportDefinition(
        id="ads_performance",
        category="growth",
        label_tr="Reklam ve ROAS",
        label_en="Ads & ROAS",
        description_tr="Kampanya harcaması, tıklama, dönüşüm, reklam geliri, ROAS ve CPA takibi.",
        description_en="Campaign spend, clicks, conversions, ad revenue, ROAS, and CPA tracking.",
        fields=(
            ReportField("campaign", "Kampanya Adı", "Campaign Name", True, "text", ("campaign", "campaign name", "kampanya", "kampanya adi", "kampanya adı")),
            ReportField("platform", "Platform", "Platform", False, "text", ("platform", "google", "meta", "trendyol")),
            ReportField("start_date", "Başlangıç Tarihi", "Start Date", False, "date", ("start date", "baslangic tarihi", "başlangıç tarihi")),
            ReportField("ads_spend", "Reklam Harcaması", "Ad Spend", True, "number", ("ads", "ad spend", "spend", "cost", "reklam", "reklam harcamasi", "reklam harcaması")),
            ReportField("impressions", "Gösterim", "Impressions", False, "number", ("impressions", "impression", "gosterim", "gösterim")),
            ReportField("clicks", "Tıklama", "Clicks", False, "number", ("clicks", "click", "tiklama", "tıklama")),
            ReportField("ctr", "CTR %", "CTR %", False, "number", ("ctr", "click through rate"), "=Tıklama/Gösterim*100", "=Clicks/Impressions*100"),
            ReportField("conversions", "Dönüşüm", "Conversions", False, "number", ("conversions", "conversion", "donusum", "dönüşüm", "orders")),
            ReportField("conversion_rate", "Dönüşüm Oranı %", "Conversion Rate %", False, "number", ("conversion rate", "donusum orani", "dönüşüm oranı"), "=Dönüşüm/Tıklama*100", "=Conversions/Clicks*100"),
            ReportField("revenue", "Reklam Geliri", "Ad Revenue", True, "number", ("ad revenue", "reklam geliri", "revenue", "sales", "conversion value", "ciro")),
            ReportField("roas", "ROAS", "ROAS", False, "number", ("roas", "return on ad spend"), "=Reklam Geliri/Reklam Harcaması", "=Ad Revenue/Ad Spend"),
            ReportField("cpa", "CPA", "CPA", False, "number", ("cpa", "cost per acquisition"), "=Reklam Harcaması/Dönüşüm", "=Ad Spend/Conversions"),
        ),
        logic_tr=(
            "ROAS > 4: Çok başarılı kampanya - bütçe artırılabilir",
            "ROAS 2-4: Karlı kampanya",
            "ROAS < 2: Optimize edilmeli veya durdurulmalı",
            "CTR < %0.5: Kreatif/hedefleme sorunu",
            "Dönüşüm oranı < %1: Landing page optimizasyonu gerekli",
        ),
        logic_en=(
            "ROAS > 4: Very successful campaign - budget can be increased",
            "ROAS 2-4: Profitable campaign",
            "ROAS < 2: Optimize or stop",
            "CTR < 0.5%: Creative/targeting issue",
            "Conversion rate < 1%: Landing page optimization required",
        ),
    ),
    "risk_alerts": ReportDefinition(
        id="risk_alerts",
        category="growth",
        label_tr="Risk ve Uyarılar",
        label_en="Risk & Alerts",
        description_tr="Stok, nakit ve performans riskleri için skor, eşik ve tahmini etki takibi.",
        description_en="Score, threshold, and estimated impact tracking for stock, cash, and performance risks.",
        fields=(
            ReportField("risk_type", "Risk Tipi", "Risk Type", True, "text", ("risk type", "risk tipi", "stok", "nakit", "performans")),
            ReportField("scope", "Ürün/Kategori", "Product/Category", True, "text", ("scope", "urun kategori", "ürün kategori", "product", "category", "kategori")),
            ReportField("risk_level", "Risk Seviyesi", "Risk Level", False, "text", ("risk level", "risk seviyesi", "low", "medium", "high", "dusuk", "düşük", "orta", "yuksek", "yüksek")),
            ReportField("current_value", "Mevcut Değer", "Current Value", False, "number", ("current value", "mevcut deger", "mevcut değer")),
            ReportField("threshold_value", "Eşik Değer", "Threshold Value", False, "number", ("threshold value", "esik deger", "eşik değer")),
            ReportField("difference", "Fark", "Difference", False, "number", ("difference", "fark"), "=Mevcut Değer-Eşik Değer", "=Current Value-Threshold Value"),
            ReportField("risk_score", "Risk Skoru", "Risk Score", True, "number", ("risk score", "risk skoru", "score")),
            ReportField("estimated_impact", "Tahmini Etki", "Estimated Impact", False, "number", ("estimated impact", "tahmini etki", "mali etki")),
            ReportField("mitigation_status", "Önlem Durumu", "Mitigation Status", False, "text", ("mitigation status", "onlem durumu", "önlem durumu")),
            ReportField("last_check_date", "Son Kontrol Tarihi", "Last Check Date", False, "date", ("last check date", "son kontrol tarihi")),
        ),
        logic_tr=(
            "Risk skoru >= 8: Kritik risk",
            "Risk skoru 5-7: Orta risk - takip edilmeli",
            "Tahmini etki yüksekse aksiyon önceliği artırılır",
        ),
        logic_en=(
            "Risk score >= 8: Critical risk",
            "Risk score 5-7: Medium risk - monitor",
            "High estimated impact increases action priority",
        ),
    ),
}


def get_report_definition(report_type: str | None) -> ReportDefinition:
    return REPORTS.get(report_type or "profitability", REPORTS["profitability"])


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
