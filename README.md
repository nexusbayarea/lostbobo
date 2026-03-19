# SimHPC Mission Control Cockpit

The SimHPC Frontend is **LIVE** and accessible at [https://simhpc.com](https://simhpc.com).

This is the public-facing repository for the SimHPC Mission Control Cockpit, a premium interface for aerospace and thermal engineering simulations.

## Architecture (v2.1.1)

### Docker Containers
| Service | Image | Purpose |
| :--- | :--- | :--- |
| API | `simhpc/api:alpha` | FastAPI backend with gunicorn |
| GPU Worker | `simhpcworker/simhpc-worker:v2` | RunPod GPU pod with infinite loop |
| Autoscaler | `simhpc/autoscaler:alpha` | Queue monitoring & pod management |

### Queue Architecture
- **Queue Name**: `simhpc_jobs` (default)
- **Polling**: Every 2 seconds
- **Concurrency**: Up to 2 jobs per pod via thread pool
- **Auto-scaling**: Pods start/stop based on queue length

## v2.1.1: Concurrent Workers
- **TelemetryPanel**: 240Hz solver streams.
- **OperatorConsole**: High-stakes engineering actions (Intercept, Clone, Boost, Certify).
- **SimulationLineage**: Visual ancestry and Flux Delta tracking.
- **GuidanceEngine**: Mercury AI-powered strategy recommendations.
- **Toast Notifications**: Sonner-based toast system with 6s/8s/10s duration tiers, cyan glow theme, `toast.promise()` pattern, and Supabase Realtime completion celebrations.
- **Simulation Detail Modal**: Clickable simulation rows with AI insights, physics metrics JSON, and PDF download.
- **Admin Analytics**: Real-time GPU pod health, simulation counts, and lead qualification tracking at `/admin/analytics`.
- **Custom Domain**: First-party auth via subdomain strategy (app + auth on same apex).

## Development

### Prerequisites
- Node.js 18+
- npm or yarn

### Run Development Server
```bash
npm install
npm run dev
```

### Build for Production
```bash
npm run build
```

## Deployment
The frontend is automatically deployed to Vercel upon merging into the main branch of the `lostbobo` repository.
- **Primary**: [https://simhpc.com](https://simhpc.com) — Vercel (production)
- **Backup**: [https://NexusBayArea.github.io/lostbobo](https://NexusBayArea.github.io/lostbobo) — GitHub Pages (staging/debug only)

### Environment Variables (Critical)
Vite requires `VITE_` prefixed variables to be available **at build time**. They are hardcoded into the JavaScript bundle during `npm run build`.

| Variable | Purpose | Source |
|----------|---------|--------|
| `VITE_SUPABASE_URL` | Supabase project URL | Supabase Dashboard |
| `VITE_SUPABASE_ANON_KEY` | Supabase anonymous key | Supabase Dashboard |
| `VITE_API_URL` | Backend API endpoint | RunPod API container |

#### Vercel (Automatic)
Vercel injects these via the Dashboard or `vercel-action` workflow. No manual setup needed.

#### GitHub Pages (Manual — Required)
GitHub Pages is static hosting and cannot read secrets at runtime. You must:
1. Add `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` to **Repo → Settings → Secrets → Actions**
2. Pass them in the workflow build step:
```yaml
- name: Build
  run: npm run build
  env:
    VITE_SUPABASE_URL: ${{ secrets.VITE_SUPABASE_URL }}
    VITE_SUPABASE_ANON_KEY: ${{ secrets.VITE_SUPABASE_ANON_KEY }}
```

#### Known Issue: GitHub Pages CSP & Stripe
`github.io` domains enforce stricter Content-Security-Policy and block third-party cookies. If using GitHub Pages, add this to `index.html`:
```html
<meta http-equiv="Content-Security-Policy" 
  content="default-src 'self'; connect-src 'self' https://*.supabase.co https://*.stripe.com; script-src 'self' 'unsafe-inline' https://*.stripe.com; style-src 'self' 'unsafe-inline';">
```

**Recommendation**: Use **Vercel as Production Primary** — it handles Auth, Stripe, and SPA routing natively.

---

## Appendix: Mercury AI Usage in Alpha

### 1. Where Mercury Is Used in Alpha
Mercury is used for **Simulation Setup Assistance** and **Notebook Generation**. It helps interpret user inputs and summarize simulation results with numerical anchoring.

### 2. Simple Mercury Health Test
```bash
curl https://api.inceptionlabs.ai/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mercury",
    "messages": [
      {"role":"user","content":"reply SIMHPC_OK"}
    ]
  }'
```
Expected output: `SIMHPC_OK`
