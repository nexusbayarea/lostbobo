# Progress Log

## Current Status
- **v1.6.0-ALPHA**: Mission Control Cockpit (Modular Design Intelligence Platform).
- **v1.5.1-ALPHA**: Alpha Control Room (4-Panel UI).
- **v1.4.0-BETA**: Direct Vercel Deployment & RunPod Orchestration.

---

## Toast Notification System Fix (March 18, 2026)

### Problem
The `<Toaster />` component from sonner was **never mounted** in the React tree. All 12 `toast()` calls were silently doing nothing.

### Fix
1. Created `src/main.tsx`, `src/App.tsx` with `<Toaster />` (6s default, 8s success, 10s error, cyan theme, rounded corners)
2. Created `index.html`, `src/index.css` (toast CSS overrides), `vite.config.ts`
3. Created `src/lib/supabase.ts` — Supabase client
4. Created `src/hooks/useSimulationUpdates.ts` — Supabase Realtime hook for `simulation_history` table
5. Updated `Dashboard.tsx` — `toast.promise()` pattern for submission; real-time simulation history table with status badges + clickable rows
6. Updated `OperatorConsole.tsx` — Loading→success for operator commands
7. Updated `AlphaControlRoom.tsx` — Loading→success for certificate generation
8. Created `src/components/SimulationDetailModal.tsx` — AI insights, physics metrics, PDF download
9. Created `src/pages/AdminAnalytics.tsx` — Admin Control at `/admin/analytics` with lead qualification

### Custom Domain & First-Party Auth (March 18, 2026)
- DNS: A `@ → 76.76.21.21`, CNAME `auth → [project-ref].supabase.co`
- Eliminates "Cookie Rejected" errors by making Supabase Auth first-party
- CORS hardened in `api.py` from `["*"]` to explicit allow-list

---

## Frontend Deployment Diagnosis (March 18, 2026)

### GitHub Pages vs Vercel: Root Cause Analysis
Console logs revealed that the GitHub Pages deployment (`https://NexusBayArea.github.io/lostbobo`) fails while Vercel (`https://simhpc.com`) works due to:

1. **Environment Variable Injection**: Vite requires `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` at **build time**. Vercel injects these automatically; GitHub Pages does not — resulting in "Supabase Credentials Missing" errors.
2. **CSP Restrictions**: `github.io` enforces `'style-src self'` which blocks Stripe.js inline styles. Vercel has permissive CSP defaults.
3. **Third-Party Cookie Blocks**: Enhanced Tracking Protection on `github.io` blocks Supabase Auth session cookies and Stripe payment redirects.

### Decision
**Vercel retained as Production Primary.** GitHub Pages remains as backup/staging with env var injection fix applied if needed.

---

### March 18, 2026 (SaaS Deployment & Production Launch)

- **Frontend Deployment**: Successfully pushed the finalized `v1.6.0-ALPHA` cockpit to `lostbobo.git`.
- **Production Status**: SimHPC SaaS is LIVE at **https://simhpc.com**.
- **Conflict Resolution**: Resolved git rebase conflicts and synchronized the frontend repository with the latest component updates.
- **Documentation**: Updated all READMEs and progress logs to reflect the live production status.

### March 16, 2026 (Mission Control Cockpit Redesign - v1.6.0)

- **Modular Component Architecture**: Decoupled the Alpha Control Room into production-grade components: `TelemetryPanel`, `ActiveSimulations`, `SimulationLineage`, `OperatorConsole`, and `GuidanceEngine`.
- **Mercury AI Integration**: Fully transitioned to Mercury AI for simulation assistance and notebook generation.
- **System Health LEDs**: Real-time status indicators for Mercury AI, Supabase, and RunPod.
