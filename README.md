# JewelPilot / Accessory Retail Copilot

AI destekli retail intelligence platformu. Takı, aksesuar, butik moda ve lifestyle retail markaları için mağaza, ürün, stok, koleksiyon ve yatırımcı kararlarını tek panelde aksiyon önerisine çevirir.

Bu ürün POS, web sitesi kurucu veya genel BI dashboard değildir. Amaç karar katmanıdır:

- Hangi ürün yeniden üretilmeli?
- Hangi stok indirime girmeli veya mağazalar arasında transfer edilmeli?
- Hangi koleksiyon hero category olarak büyütülmeli?
- Hangi mağaza revenue per m², conversion veya ürün karması açısından sorunlu?
- Yatırımcı / board raporunda hangi büyüme hikayesi anlatılmalı?

## MVP: Retail Health Report

İlk sürüm API entegrasyonu gerektirmez. Müşteri CSV/Excel dosyası yükler, sistem şu çıktıları üretir:

- En karlı / hero ürünler
- Nakit bağlayan stok
- Yeniden üretim önerileri
- Markdown veya transfer önerileri
- Koleksiyon performansı
- Mağaza verimliliği
- AI retail karar içgörüleri
- CEO / yatırımcı özeti

## Beklenen Veri Alanları

- Günlük satış
- Mağaza bazlı satış
- SKU bazlı satış
- Stok adedi
- Ürün maliyeti
- Satış fiyatı
- Ürün kategorisi
- Koleksiyon adı
- Malzeme
- Mağaza m² bilgisi
- Footfall / ziyaretçi sayısı
- Online kanal satış verisi

## Ana Ekranlar

- CEO Dashboard
- Store Performance
- Product & Collection Intelligence
- Reorder & Transfer Engine
- Investor / Board Report Generator

## Planlanan Veri Kaynakları

CSV/Excel ilk kaynak olarak kalır. Sonraki entegrasyonlar:

- Shopify
- WooCommerce
- ikas
- Ticimax
- Nebim V3
- Logo
- Mikro
- Paraşüt

## Lokal Çalıştırma

```bash
cp .env.example .env
docker compose up --build
```

Adresler:

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/health
- API docs: http://localhost:8000/docs
