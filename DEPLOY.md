# Private beta deploy checklist

Ship today with **Vercel (frontend)** + **Railway (backend + Postgres)**.  
Acceptable for trusted testers only — resume URLs are not auth-protected yet.

---

## Before you deploy

- [ ] **Rotate API keys** if `backend/.env` was ever shared or committed
- [ ] **Initialize git** and push to GitHub (required for Vercel/Railway)
- [ ] Confirm local build passes:
  ```bash
  cd frontend && npm run build
  ```

---

## 1. Backend (Railway)

### Create services

1. New project → **Add PostgreSQL** (Database plugin)
2. New service → **GitHub repo** → root path: `backend/`
3. Or deploy from Dockerfile: `backend/Dockerfile`

### Link Postgres to the API service (required)

Railway **no longer auto-injects** database URLs. You must add an explicit **reference** on the API service (e.g. `AIfy_Resume`), not only on Postgres (e.g. `Postgres-Cq8L`).

**Dashboard (30 seconds):**

1. Open service **`AIfy_Resume`** (GitHub / API — not Postgres)
2. **Variables** → **+ New Variable** → **Add Reference** (or raw variable)
3. If raw, set:
   - **Name:** `DATABASE_URL`
   - **Value:** `${{Postgres-Cq8L.DATABASE_URL}}`  
     (use autocomplete — service name must match your Postgres service exactly)
4. Save → Railway redeploys automatically

**CLI (optional):**

```bash
npm install -g @railway/cli
railway login
cd backend && railway link   # pick AIfy_Resume
chmod +x ../scripts/railway-link-postgres.sh
../scripts/railway-link-postgres.sh Postgres-Cq8L AIfy_Resume
```

The app auto-converts Railway’s `postgresql://...` URL to `postgresql+asyncpg://...`. Do **not** paste your local `localhost` `.env` value.

Verify after deploy — logs should show:

```
Database env: DATABASE_URL=set, ...
Database target: postgres.railway.internal:5432 (no-ssl)
```

Or `curl https://YOUR-API.up.railway.app/health` → `"db_host": "postgres.railway.internal"`.

### If you still get `Connection refused`

Railway logs will show `Database target: HOST:PORT (ssl/no-ssl)` — use that to debug.

| Log shows | Fix |
|-----------|-----|
| `localhost:5432` | `DATABASE_URL` is missing on the **backend** service — add a reference (see above) |
| `postgres.railway.internal:5432 (no-ssl)` | Postgres not reachable on private network. Confirm Postgres service is **Active**, then **Redeploy backend**. If it still fails, switch to the **public** URL (below). |
| `something.proxy.rlwy.net:##### (ssl)` or `*.railway.app:##### (ssl)` | Public proxy URL — port must be the **proxy port** Railway gives you (often **not** 5432). Copy the full URL from Postgres → **Connect** → **Public Network**. |
| Public URL but port is `5432` | Wrong — you mixed internal port with public host. Re-copy the full public URL from Railway. |

**Recommended fix when internal fails:**

1. Postgres service → **Connect** tab → **Public Network** → enable if off
2. Copy the full `postgresql://...` URL (note the port, e.g. `:18432`)
3. Backend service → **Variables** → set `DATABASE_URL` to that full URL
4. Redeploy backend

Your internal URL (`postgres.railway.internal:5432`) is **correct in format** — refusal usually means Postgres isn’t running yet, or private networking isn’t working between your two services. The public URL is the reliable fallback for private beta.


Copy from `backend/.env.production.example`. Minimum set:

| Variable | Example |
|----------|---------|
| `DATABASE_URL` | Reference from Railway Postgres (auto-normalized) |
| `GOOGLE_API_KEY` | Your Gemini key |
| `LLM_PROVIDER` | `gemini` |
| `LLM_MODEL` | `gemini-2.5-flash` |
| `DEBUG` | `false` |
| `CORS_ORIGINS` | `https://your-app.vercel.app` |
| `FRONTEND_URL` | `https://your-app.vercel.app` |
| `UPLOAD_DIR` | `/app/uploads` |

### Railway settings

- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health check path:** `/health`
- Add a **volume** mounted at `/app/uploads` (so uploads survive restarts)

### Verify

```bash
curl https://YOUR-API.up.railway.app/health
# → {"status":"ok","service":"alfy-resume-api"}
```

`/docs` is disabled when `DEBUG=false`.

---

## 2. Frontend (Vercel)

1. Import GitHub repo → root directory: **`frontend`**
2. Framework: **Next.js** (auto-detected)
3. Environment variable:

| Variable | Value |
|----------|--------|
| `NEXT_PUBLIC_API_URL` | `https://YOUR-API.up.railway.app` |

4. Deploy → note production URL (e.g. `https://alfy-resume.vercel.app`)

### Update backend CORS

Set on Railway (must match frontend URL exactly):

```
CORS_ORIGINS=https://alfy-resume.vercel.app
FRONTEND_URL=https://alfy-resume.vercel.app
```

Redeploy API after changing CORS.

---

## 3. Smoke test (production)

- [ ] Landing page loads
- [ ] Upload PDF/DOCX resume
- [ ] Processing completes → review screen
- [ ] Edit + save enhanced resume
- [ ] Preview + **Download PDF**
- [ ] Dashboard shows job matches
- [ ] Job links open (live posting or search fallback)

---

## 4. Private beta safeguards

- [ ] Share app URL only with trusted testers
- [ ] Do **not** post resume links publicly (anyone with UUID can access)
- [ ] Set a **spend cap** on Google AI / OpenAI billing
- [ ] Monitor Railway logs for errors during first sessions

---

## 5. Optional (same day)

| Task | Why |
|------|-----|
| Custom domain on Vercel | Cleaner URL for demos |
| Railway custom domain for API | Avoid CORS/url churn |
| `USE_CELERY=true` + worker service | Heavier uploads won’t block API |

---

## 6. Not in scope for private beta (do before public launch)

- User authentication on resume routes
- Rate limiting on `/upload`
- Alembic migrations (schema via `create_all` on startup)
- S3/Supabase for uploads (multi-instance)
- Stripe billing (router exists but not mounted)

---

## Quick reference

| Service | Local | Production |
|---------|-------|------------|
| Frontend | http://localhost:3000 | https://YOUR-APP.vercel.app |
| API | http://localhost:8000 | https://YOUR-API.up.railway.app |
| Health | http://localhost:8000/health | same on prod API |

Env templates: `backend/.env.production.example`, `frontend/.env.production.example`
