# GitHub + Proxmox + Cloudflare Tunnel Yayın Akışı

Bu proje için önerilen akış:

1. Kod GitHub reposunda durur.
2. Proxmox sunucuda Docker Compose ile servisler çalışır.
3. Proxmox içine kurulan self-hosted GitHub Actions runner, `main` branch'e push gelince projeyi günceller.
4. Cloudflare Tunnel dışarıdan gelen trafiği sunucudaki `localhost:3000` ve `localhost:8000` portlarına taşır.

## 1. GitHub Reposu Oluştur

GitHub'da boş bir repo oluştur. Örnek ad:

```bash
ecom-analytics-saas
```

Lokal makinende Git kurulu değilse önce Git for Windows kur:

```text
https://git-scm.com/download/win
```

Sonra proje klasöründe:

```bash
git init
git add .
git commit -m "Initial e-commerce analytics SaaS"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADIN/ecom-analytics-saas.git
git push -u origin main
```

Not: Büyük Excel/CSV dosyaları `.gitignore` içinde ignore edilir.

## 2. Proxmox Sunucuyu Hazırla

Proxmox host üzerinde veya önerilen şekilde bir Debian/Ubuntu VM içinde:

```bash
apt update
apt install -y git curl rsync ca-certificates docker.io docker-compose-plugin
systemctl enable --now docker
```

Uygulama klasörünü oluştur:

```bash
mkdir -p /opt/ecom-analytics
chown -R $USER:$USER /opt/ecom-analytics
```

İlk kurulum için repoyu çek:

```bash
git clone https://github.com/KULLANICI_ADIN/ecom-analytics-saas.git /opt/ecom-analytics
cd /opt/ecom-analytics
cp .env.production.example .env.production
```

Güçlü secret üret:

```bash
openssl rand -hex 32
```

`.env.production` dosyasını düzenle:

```bash
nano .env.production
```

Önemli alanlar:

```env
JWT_SECRET=openssl-ile-urettigin-secret
POSTGRES_PASSWORD=guclu-db-sifresi
DATABASE_URL=postgresql+psycopg://analytics:guclu-db-sifresi@postgres:5432/jewelpilot
NEXT_PUBLIC_API_URL=https://analytics-api.droopshipping.com.tr
CORS_ORIGINS=https://analytics.droopshipping.com.tr
```

İlk deploy:

```bash
bash deploy/proxmox-deploy.sh
```

Kontrol:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml ps
curl http://localhost:8000/health
```

## 3. Cloudflare Tunnel Hostname Ayarları

Mevcut tunnel'a şu public hostname'leri eklemeni öneririm:

```text
analytics.droopshipping.com.tr      -> http://localhost:3000
analytics-api.droopshipping.com.tr  -> http://localhost:8000
proxmox.droopshipping.com.tr        -> https://localhost:8006
```

`proxmox.droopshipping.com.tr` alan adını Proxmox paneline ayırmak daha temiz ve güvenli olur. Uygulama için ayrı `analytics` ve `analytics-api` subdomain kullanıyoruz.

Cloudflare Zero Trust panelinden:

```text
Networks > Tunnels > mevcut tunnel > Public Hostnames > Add a public hostname
```

Alternatif config örneği:

```bash
deploy/cloudflare-tunnel.example.yml
```

## 4. GitHub Self-hosted Runner Kur

GitHub reposunda:

```text
Settings > Actions > Runners > New self-hosted runner > Linux x64
```

GitHub'ın verdiği komutları Proxmox sunucuda çalıştır. Runner label kısmına şunları ekle:

```text
proxmox,production
```

Runner'ın Docker çalıştırabilmesi gerekir:

```bash
usermod -aG docker $USER
```

Runner farklı bir kullanıcıyla çalışıyorsa o kullanıcıyı Docker grubuna ekle. Gerekirse oturumu kapatıp aç.

Runner klasöründe servisi kur:

```bash
sudo ./svc.sh install
sudo ./svc.sh start
```

## 5. Otomatik Yayın

Bu dosya otomatik deploy yapar:

```bash
.github/workflows/deploy-proxmox.yml
```

Akış:

1. `main` branch'e push yapılır.
2. `CI` workflow'u backend testlerini ve frontend build'i çalıştırır.
3. CI başarılı olursa Proxmox içindeki runner deploy'u başlatır.
4. Repo `/opt/ecom-analytics` klasörüne senkronize edilir.
5. `.env.production` korunur.
6. Docker image'ları yeniden build edilir.
7. Servisler kesintiyi minimumda tutacak şekilde güncellenir.

Manuel deploy için GitHub Actions içinden `Deploy to Proxmox` workflow'unu `Run workflow` ile çalıştırabilirsin.

## 6. Güncelleme Komutları

Lokalden GitHub'a gönder:

```bash
git add .
git commit -m "Describe change"
git push
```

Sunucuda elle güncellemek istersen:

```bash
cd /opt/ecom-analytics
git pull
bash deploy/proxmox-deploy.sh
```

## 7. Servis URL'leri

Yayın sonrası:

```text
Frontend: https://analytics.droopshipping.com.tr
Backend:  https://analytics-api.droopshipping.com.tr
Docs:     https://analytics-api.droopshipping.com.tr/docs
Health:   https://analytics-api.droopshipping.com.tr/health
```
