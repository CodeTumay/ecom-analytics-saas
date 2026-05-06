# Kullanici Deneyimi, Raporlama ve Entegrasyon Yol Haritasi

## Oncelik 1: Kullanilabilirlik

- Dashboard mobilde tek kolon calismali; tablo ve detay alanlari yatay kaydirma ile okunabilir kalmali.
- Kritik aksiyonlar ust barda toplanmali: para birimi, PDF al, dil, cikis.
- Upload ve Trendyol aktarimi ayni "veri girisi" alaninda olmali.
- Rapor secimi kullaniciyi teknik kolon isimlerine mecbur birakmadan baslik, ornek CSV ve kabul edilen alan adlariyla anlatilmali.

## Oncelik 2: Rapor Alma

- Ilk adim: tarayicinin print/PDF akisi ile dashboard PDF olarak alinabilir.
- Sonraki adim: backend tarafinda markali PDF rapor servisi eklenmeli.
- Planlanan PDF icerigi:
  - Ozet metrikler
  - Karlilik ve maliyet kirilimi
  - En karli ve zarar eden urunler
  - AI icgoruler
  - Rapor detayi ve veri kaynagi

## Oncelik 3: Para Birimi

- UI USD/TL gosterebilmeli.
- TL gosteriminde kullanici kur katsayisini degistirebilmeli.
- Sonraki adimda gunluk kur otomatik cekilmeli ve rapor aninda kullanilan kur rapora yazilmali.

## Oncelik 4: Trendyol Entegrasyonu

- Trendyol siparis endpoint'i:
  - `GET /integration/order/sellers/{sellerId}/orders`
  - Basic auth kullanir.
  - `startDate` ve `endDate` Unix timestamp milisaniye bekler.
  - `size` maksimum 200'dur.
- Ilk entegrasyon akisi:
  - Kullanici seller ID, API key, API secret ve gun araligi girer.
  - Sistem siparis paketlerini ceker.
  - Siparis satirlarini mevcut karlilik analizine uygun CSV'ye cevirir.
  - Analiz motoruna kuyruklar.
- Sonraki adimlar:
  - Credential bilgileri sifreli saklanmali.
  - Artimli senkronizasyon icin son basarili sync zamani tutulmali.
  - Buyuk hacim icin Trendyol'un shipment package stream endpoint'i kullanilmali.
  - Urun maliyeti ve reklam harcamasi Trendyol disi kaynaklardan eslestirilmelidir.

## Oncelik 5: Anlik Analiz

- Trendyol siparisleri periyodik cekilmeli.
- Her sync sonrasi dashboard otomatik yenilenmeli.
- Kar marji dususu, zarar eden urun, kargo/komisyon artis gibi alarmlar bildirim kanallarina baglanmali.
