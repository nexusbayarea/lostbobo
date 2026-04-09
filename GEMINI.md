# SimHPC Development Guidelines

## Project Structure (v2.5.1)

We follow a strict monorepo structure to separate concerns and protect intellectual property. All legacy components from `apps/frontend` have been consolidated into the root `src/` directory.

- **`apps/frontend/src/`**: React Cockpit application (Unified frontend source).
- **`services/api/`**: FastAPI orchestrator (Mercury AI integration, fleet management).
- **`services/worker/`**: Unified compute plane (Physics execution + Scaling + Reports).
- **`packages/`**: Shared libraries, SDKs, and internal tools.
- **`docs/`**: Centralized documentation.
- **`legacy_archive/`**: Consolidated legacy artifacts and deprecated `apps/frontend` submodule.

## Database Schema (v2.5.1)

The core database table is `simulations`. A backward-compatible view named `simulations` exists for legacy code.

**Key columns**: `id`, `user_id`, `org_id`, `job_id`, `scenario_name`, `status`, `prompt`, `input_params`, `result_summary`, `gpu_result`, `audit_result`, `hallucination_score`, `report_url`, `pdf_url`, `certificate_id`, `error`, `created_at`, `updated_at`.

**Supporting tables**: `certificates`, `documents`, `document_chunks`, `simulation_events`, `platform_alerts`.

**TypeScript types** live in `apps/frontend/src/types/`:

- `db.ts` — Exact Supabase schema mirror
- `audit.ts` — Audit + verification types
- `api.ts` — API response contracts
- `realtime.ts` — Supabase realtime partial update types
- `view.ts` — UI view models + mapper

## Best Practices

1. **Isolation**: Maintain clear boundaries between apps and services.
2. **Environment**: Store all secrets in `.env`. Never commit `.env` files.
3. **Documentation**: Keep `README.md` and `ARCHITECTURE.md` updated with any structural changes.
4. **Consistency**: Follow existing naming conventions (kebab-case for folders).
5. **Cleanliness**: Regularly clean up temporary files, build artifacts, and logs.
6. **Git Security**: Always use a standard `.gitignore` file. Never commit `.env` or any file containing secrets.

## Deployment Notes

- **Vercel is Production Primary**: Handles root `src/` build and deployment automatically via native GitHub integration.
- **RunPod HTTP Proxy (v2.3.0)**: Always use the RunPod HTTP Proxy URL for `VITE_API_URL` to prevent "Offline" errors.
- **Production Port 8888**: RunPod Public Proxy defaults to Port 8888 for stable routing. 
- **Jupyter Conflict Resolution**: Always include `fuser -k 8888/tcp || true` in `start.sh` to terminate default Jupyter processes before starting the FastAPI app.
- **Vercel API Configuration**: Ensure `API_BASE_URL` in Vercel follows the `https://[POD_ID]-8888.proxy.runpod.net` format and requires a manual redeploy after Infisical sync.
- **`no_active_pods` Resolution**: If Vercel reports `no_active_pods`, verify:
  1. `RUNPOD_POD_ID` is correctly set in Infisical/Vercel (just the ID, e.g., `pod-v68079mny6m1i0`).
  2. `MERCURY_API_URL` (or `API_BASE_URL`) matches the new Pod's 8888 Proxy URL.
  3. A fresh Vercel deployment has been triggered to pull updated environment variables.
- **Google Auth (v2.5.1)**: Google Client ID `552738566412-t6ba9ar8jnsk7vsd399vhh206569p61e.apps.googleusercontent.com`.
- **Infisical Setup**: Run `infisical init` in the project root. Secrets may use `SB_URL`/`SB_ANON_KEY` naming.
- **Supabase Client Naming**: `src/lib/supabase.ts` checks `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON`, and `VITE_SUPABASE_ANON_KEY` with fallbacks to `SUPABASE_URL`/`SUPABASE_ANON_KEY`.

## Mission Control Dashboards (v2.5.1)

- **Admin Analytics**: `apps/frontend/src/pages/admin/AdminAnalyticsPage.tsx` — Protected by `requireAdmin`. Features Fleet HUD, Panic Button, and Scaling Events.
- **Alpha Control Room**: `apps/frontend/src/pages/AlphaControlRoom.tsx` — Expert-level cockpit with O-D-I-A-V loop components (Telemetry, Lineage, Console).
- **Active Telemetry**: Driven by `useSimulations` hook with Supabase Realtime synchronization.

## AI Project Guardrails

### 1. Critical File Naming & Security

- **FORBIDDEN**: Never name the ignore file `_gitignore`. It MUST be exactly `.gitignore`.
- **ACTION**: If `_gitignore` is detected, rename it to `.gitignore` immediately.

### 2. Structural Separation

- **Frontend**: `apps/frontend/` directory. No Python or GPU logic.
- **Backend**: `services/` directory. Handles all physics and AI orchestration.

### 3. Environment Variable Policy

- **Build Time**: `VITE_` prefixed variables are injected at build time.
- **Zero-Trust**: Administrative tasks MUST use `infisical run --` for secret injection.
