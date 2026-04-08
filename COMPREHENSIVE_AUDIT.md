# Comprehensive Audit Summary (April 2026)

> **Date**: April 7, 2026  
> **Version**: v2.5.7  
> **Status**: Vercel Proxy Layer Active - CORS Fixed ✅

---

## Executive Summary

Your SimHPC codebase is a solid, production-oriented full-stack setup (FastAPI backend on RunPod + React/Vite frontend on Vercel + Supabase + Redis + autoscaling). However, several **critical blockers** explain the persistent issues you're seeing:

- CORS failures on every fetch (including `/user/profile` and robustness start)
- Vercel build failures (`APIReference` import)
- GitHub CI failures (Ruff + Infisical)
- Redis connection errors on new pods
- Inconsistent pod IDs across deploys

---

## 1. CORS Issues (Primary Blocker Right Now)

### Root Cause

- You have `allow_credentials=True` + two `CORSMiddleware` instances (one with list, one with `allow_origin_regex`).
- FastAPI docs and CORS spec: **You cannot use `["*"]` or unreliable wildcards with `allow_credentials=True`**. Browsers reject it for security.
- Vercel preview domains (`https://*-projects.vercel.app`) change on every deploy and often don't match `https://*.vercel.app` reliably.
- Current pod (`40n3yh92ugakps-8000.proxy.runpod.net`) likely doesn't have your exact preview origin in `ALLOWED_ORIGINS`.
- Preflight (OPTIONS) requests fail → "No 'Access-Control-Allow-Origin' header".

### Immediate Fix (on current RunPod pod)

Edit the pod → Environment Variables → Update `ALLOWED_ORIGINS` to **exactly** this (no wildcards for Vercel previews):

```
http://localhost:3000,http://localhost:5173,http://localhost:59824,http://127.0.0.1:59824,https://simhpc-nexusbayareas-projects.vercel.app,https://simhpc.nexusbayarea.com,https://simhpc.com
```

Save → pod restarts (~60-90s).  
Then test: `https://40n3yh92ugakps-8000.proxy.runpod.net/api/v1/health`

### Better Long-Term Fix in `api.py` (recommended)

Replace the current CORS section with this cleaner version:

```python
# --- CORS (Clean v2.5.5+) ---
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:59824,"
    "http://127.0.0.1:59824,https://simhpc-nexusbayareas-projects.vercel.app,"
    "https://simhpc.nexusbayarea.com,https://simhpc.com",
).split(",")

CORS_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,           # Explicit list (no *)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Optional: Regex fallback for future Vercel previews (use sparingly)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https://.*-projects\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Remove any manual `@app.options` preflight handlers — the middleware handles them.

**Alternative (if CORS keeps fighting you)**: Implement a simple Vercel proxy route as mentioned in `progress.md` (server-to-server bypass). See `apps/frontend/api/[...path].ts`.

---

## 2. Vercel Build Error (`Could not resolve "./APIReference"`)

### Root Cause

The file `apps/frontend/src/pages/index.ts` still imports a deleted/refactored component.

### Action

- Open that file and **remove** the import line for `./APIReference` and any `<APIReference />` usage.
- Or replace it with the correct component (likely a dashboard or API docs section).

Push the change → Vercel build should succeed, allowing you to update `VITE_API_URL` to the current pod.

### Fix Applied

```typescript
// apps/frontend/src/pages/index.ts
export * from './Benchmarks';
export * from './Dashboard';
export * from './Pricing';
export * from './Privacy';
export * from './SignIn';
export * from './SignUp';
export * from './Terms';
export * from './About';
export * from './Docs';
// export * from './APIReference';  // REMOVED - doesn't exist
export * from './CCPA';
export * from './DPA';
export * from './CookiePolicy';
export * from './Contact';
```

---

## 3. GitHub CI Failures

### Ruff in `services/worker/worker.py`

Run locally:
```bash
cd services/worker
ruff check --fix worker.py
```

Then manually:
- Delete unused imports: `hashlib`, `requests`, `redis.exceptions.ConnectionError`
- Fix one-line `if` statements (add newlines).

### Infisical

Your workflow needs authentication. Add a GitHub secret `INFISICAL_TOKEN` (service token from Infisical) and append `--token=${{ secrets.INFISICAL_TOKEN }}` to the export command.

### Node.js deprecation

Update your GitHub workflow to `node-version: 22` (or 20 is fine but deprecated).

---

## 4. Redis & Pod Stability

- Every time you edit env vars on RunPod, it often creates a **new pod ID**. Always update Vercel `VITE_API_URL` after.
- Your `api.py` now has a nice `InMemoryCache` fallback — good safety net, but production needs real Redis.
- Make sure `REDIS_URL` is set on every new pod.

---

## 5. Other Observations (Positive + Minor)

### Good

- In-memory Redis fallback in `api.py` is smart.
- Non-root users in Dockerfiles.
- Structured logging and metadata in robustness_service.py.
- Autoscaler with cost guards and long-term idle termination.
- Health endpoints present.

### Minor Issues

- `vercel.json` rewrites everything to `/` — fine for SPA but ensure API proxy (if used) is handled.
- `index.html` has hardcoded Supabase URL and some outdated links.
- `worker.py` still has simulation placeholders (good for testing, replace with real physics when ready).
- `progress.md` mentions v2.5.5 proxy layer — implement if CORS remains stubborn.

---

## Recommended Next Steps (Priority Order)

1. **Fix CORS on current pod** (update `ALLOWED_ORIGINS` exactly as above) + test `/health`.
2. **Fix Vercel build** (remove `APIReference` import) + push → redeploy frontend.
3. **Update Vercel env** `VITE_API_URL` to current pod (`https://40n3yh92ugakps-8000.proxy.runpod.net`).
4. **Clean `worker.py`** lint + push to green CI.
5. **Hard refresh dashboard** and test robustness start + user profile fetch.

Once these are done, the "Failed to fetch" + CORS errors should vanish, and simulations should start.

---

## Environment Variable Reference

### RunPod Pod Environment Variables

| Key | Value |
|-----|-------|
| `SB_URL` | Supabase project URL |
| `SB_SERVICE_KEY` | Supabase service role key |
| `SB_JWT_SECRET` | Supabase JWT secret |
| `SB_AUDIENCE` | `authenticated` |
| `ALLOWED_ORIGINS` | Comma-separated allowed origins |
| `REDIS_URL` | Redis connection string |
| `RUNPOD_POD_ID` | Current pod ID |
| `RUNPOD_API_URL` | Full API URL with proxy |

### Vercel Environment Variables

| Key | Value |
|-----|-------|
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key |
| `VITE_API_URL` | `https://{POD_ID}-8000.proxy.runpod.net` |
| `RUNPOD_API_URL` | `https://{POD_ID}-8000.proxy.runpod.net` |

---

## Testing Checklist

- [ ] `/api/v1/health` returns 200 after CORS fix
- [ ] `/api/v1/user/profile` returns user data (no CORS error)
- [ ] Vercel build passes
- [ ] GitHub CI passes (Ruff + Infisical)
- [ ] Robustness simulation starts successfully
- [ ] Frontend can fetch from backend without CORS errors

---

*End of Comprehensive Audit Summary*
