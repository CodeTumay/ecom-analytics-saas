# E-commerce Analytics SaaS

A compact SaaS starter for marketplace profitability analytics. Users upload Trendyol, Amazon, Shopify, or similar CSV/XLSX exports; the backend auto-maps columns, runs async pandas processing, stores product-level results, and serves a dashboard with alerts.

## Folder Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/routes/          # FastAPI endpoints
│   │   ├── core/                # settings and JWT/password helpers
│   │   ├── db/                  # SQLAlchemy engine/session
│   │   ├── models/              # users, uploads, products
│   │   ├── processing/          # pandas mapping, profitability, analytics
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── services/            # storage, usage limits, insights
│   │   └── worker/              # Celery app and tasks
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/                     # Next.js app router pages
│   ├── components/              # dashboard UI pieces
│   ├── lib/api.ts               # API client and shared types
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── storage/uploads/
```

## Backend

Core endpoints:

- `POST /auth/register`
- `POST /auth/login`
- `POST /upload`
- `GET /analysis/{upload_id}`
- `POST /analysis/{upload_id}/mapping`
- `GET /dashboard`

The processing path is separate from API code:

- `column_mapping.py` detects `product_name`, `revenue`, `cost`, `commission`, `shipping`, and `ads_spend`.
- `profitability.py` calculates net profit, margin, order-level profit, and product-level profit.
- `analytics.py` builds top products, loss makers, revenue trends, and cost breakdowns.
- `insights.py` emits rule-based AI-style insights.

## Run With Docker

1. Copy environment defaults:

```bash
cp .env.example .env
```

2. Edit `.env` and set a strong `JWT_SECRET`.

3. Start the stack:

```bash
docker compose up --build
```

4. Open:

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/health
- API docs: http://localhost:8000/docs

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=postgresql+psycopg://analytics:analytics@localhost:5432/ecommerce_analytics
set REDIS_URL=redis://localhost:6379/0
uvicorn app.main:app --reload
```

Worker:

```bash
cd backend
.venv\Scripts\activate
celery -A app.worker.celery_app.celery_app worker --loglevel=info
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Proxmox Deployment Notes

- Use `docker-compose.prod.yml` on the Proxmox server.
- Keep `.env.production` only on the server; do not commit secrets to GitHub.
- Expose only `127.0.0.1:3000` and `127.0.0.1:8000`; Cloudflare Tunnel should forward public hostnames to those local ports.
- Recommended hostnames:
  - `analytics.droopshipping.com.tr` -> `http://localhost:3000`
  - `analytics-api.droopshipping.com.tr` -> `http://localhost:8000`
  - `proxmox.droopshipping.com.tr` -> `https://localhost:8006`
- GitHub deployment is prepared through a self-hosted runner workflow at `.github/workflows/deploy-proxmox.yml`.
- Full Turkish setup guide: `docs/DEPLOYMENT_TR.md`.

## SaaS Rules

- New users start on the `free` plan.
- Free users are limited to `1` upload per calendar month.
- Users on the `pro` plan have unlimited uploads.
- Plans are stored on the `users.plan` column; billing integration can update that field later.
