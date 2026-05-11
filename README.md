# Affiliate Automation Backend

Fresh FastAPI scaffold for multi-platform affiliate integrations (CJ, Impact, WordPress, Metricool).

## Folder Structure

```text
app/
  main.py
  api/
    v1/
      router.py
      endpoints/
        cj/
        impact/
        wordpress/
        metricool/
  core/
  schemas/
    cj/
    impact/
    wordpress/
    metricool/
  services/
    cj/
    impact/
    wordpress/
    metricool/
  models/
  workers/
  utils/
```

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Docs
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Current Starter Endpoints
- `GET /api/v1/health`
- `GET /api/v1/platforms`
- `GET /api/v1/cj/health`
- `POST /api/v1/cj/authorize`
- `GET /api/v1/impact/health`
- `POST /api/v1/impact/authorize`
- `GET /api/v1/wordpress/health`
- `POST /api/v1/wordpress/authorize`
- `GET /api/v1/metricool/health`
- `POST /api/v1/metricool/authorize`

Next, we can add each platform router from your cURL commands one-by-one.

## CJ: Advertiser Lookup
- Backend route: `GET /api/v1/cj/advertisers/lookup`
- Required query params:
  - `requestor-cid` (example: `6947255`)
  - `advertiser-ids` optional (default: `joined`, example: `1,2`)
  - `response-format` optional (`json` or `raw`, default: `json`)
- Auth options:
  - Set once via `POST /api/v1/cj/authorize` with body `{"token":"<CJ_TOKEN>"}`
  - Or pass header `Authorization: Bearer <token>` directly on lookup call

## CJ: Ads Product Query
- Backend route: `POST /api/v1/cj/ads/products/query`
- Upstream URL: `https://ads.api.cj.com/query`
- Uses token saved from `POST /api/v1/cj/authorize`
- Content type sent upstream: `application/graphql`
