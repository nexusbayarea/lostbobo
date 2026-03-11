# SimHPC Platform - Progress Report

## Overview

SimHPC is a cloud-based GPU-accelerated finite element simulation platform with integrated robustness analysis and AI-generated engineering reports. Built for engineering teams that require stable, defensible results.

**Live URL:** https://simhpc.com

---

## Project Structure

```
SimHPC/
├── app/                          # React frontend application
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Page components
│   │   │   ├── Dashboard.tsx         # Main dashboard with robustness
│   │   │   ├── Benchmarks.tsx        # NAFEMS Verification Vault
│   │   │   └── ...
│   │   ├── sections/            # Landing page sections
│   │   └── lib/
│   │       └── api.ts           # Centralized API client
├── robustness_orchestrator/      # Python backend services
│   ├── api.py                   # FastAPI orchestration layer
│   ├── robustness_service.py    # Parameter sweep logic
│   ├── ai_report_service.py     # AI interpretation layer
│   └── pdf_service.py           # Engineering PDF generation
└── sdk/
    └── python/
        └── example.py           # Python automation SDK
```

---

## Features Implemented

### 1. Theme System
- **Day Mode:** Off-white background (#fdfbf6) with slate text
- **Night Mode:** Dark slate background (#080E1C) with light text
- **Persistent:** Theme preference saved to localStorage

### 2. Landing Page Sections
- **Hero:** Animated mesh and confidence interval visualization
- **Stack:** Deterministic physics core (SUNDIALS, MFEM)
- **Who It's For:** Battery R&D, Hardware Startups, National Labs

### 3. Verification Benchmark Library (The "Validation Vault")
- Dedicated page showcasing SimHPC results vs. NAFEMS Benchmarks
- Side-by-side comparison with Analytical solutions and Ansys/COMSOL
- Verified cases: LE10 (Stress), FV32 (Thermal), BM3 (Structural)
- Direct link from main navigation for engineering trust

### 4. Dashboard
- **Model Configuration:**
  - Support for CAD formats: STEP, IGES, Parasolid (.x_t), STL
  - Integrated mesh upload and solver selection (SUNDIALS, MFEM)
- **Robustness Analysis:**
  - Parameter sampling (±5%, ±10%, Latin Hypercube, Monte Carlo)
  - **Sobol GSA (Enterprise):** Implementation of Global Sensitivity Analysis using Saltelli sampling. Calculates First-order ($S_1$) and Total ($S_T$) indices.
  - **Interaction Detection:** Identifies multi-variable coupling effects ($S_T - S_1$) to guide joint optimization.
  - **Efficiency:** Baseline result caching to prevent redundant GPU computations.
  - **Clamping:** Input validation ensures all perturbations respect physical parameter bounds (min/max).
  - **Concurrency Control:** Explicit thread/job capping (max 8 concurrent) to prevent GPU resource exhaustion.
- **"Kill Switch" & Telemetry:**
  - **Live Heartbeat:** WebSocket-driven telemetry bridge streaming step size (h) and solver convergence in real-time.
  - Real-time "Cancel and Refund Credits" button in Run Control.
  - **Resilience:** Convergence timeout enforcement (default 300s).

### 5. AI Engineering Reports
- **LLM Integration:** Tenacity-backed retry logic for resilient LLM communication (OpenAI/Groq ready).
- **Sobol Integration:** AI now interprets multi-variable interactions and suggests joint optimization strategies based on $S_1$ vs $S_T$ discrepancies.
- **Governance:** 
  - **Scientific Tone:** Mandatory length constraints (100-1000 chars) and keyword enforcement ("suggests" vs "proves").
  - **Cache Invalidation:** 24-hour TTL for technical interpretations to ensure data freshness.
- **Numerical Anchor:** Hard-coded integrity verification system that cross-checks AI conclusions against raw simulation metrics (max_temp, stability).
- **Export Formats:** Technical delivery via Markdown, JSON, and HTML.

### 6. Security & Persistence
- **Authentication:** Unified Supabase Authentication (Google OAuth & Email Magic Link) with JWT verification.
- **Backend Verification:** FastAPI middleware verifies Supabase JWTs using `python-jose`.
- **Frontend Auth:** `useAuth` hook for managing user sessions and protecting routes.
- **Token Escrow & Pricing:** 
  - Credit management logic that locks user tokens during simulation runs.
  - **Tiered Pricing:** 2 tokens/run for Enterprise Sobol, 5 tokens/run for standard sweeps.
- **Distributed Persistence:** 
  - **Redis:** High-speed persistence for job states and real-time telemetry queuing.
  - **Rate Limiting:** Redis-backed limiters (10 simulations/hour per user) to protect GPU capacity.
- **Monitoring:** Structured JSON logging for all service-level events.


---

## Technical Stack

### Infrastructure & DevOps
- **Orchestration:** Docker Compose (v3.8)
- **Container Architecture:** 
  - `simhpc/api`: FastAPI orchestrator service
  - `simhpc/physics-worker`: Heavy-lift container running SUNDIALS & MFEM with NVIDIA GPU runtime
  - `redis:7-alpine`: Message broker and telemetry store
- **GPU Support:** NVIDIA runtime enabled for RunPod A40 instances
- **Environment:** `${SUPABASE_JWT_SECRET}` for auth, configurable CORS origins
- **Volumes:** Persistent storage (`sim_data`) for simulation outputs

### Frontend
- **Framework:** React 18 (Vite) + TypeScript
- **Authentication:** Supabase Auth (@supabase/supabase-js)
- **Styling:** Tailwind CSS + shadcn/ui
- **Animations:** Framer Motion
- **State Management:** React Context for theme and Auth state
- **Build:** Vercel deployment with edge caching

### Backend (Python Services)
- **Orchestrator:** FastAPI + Uvicorn
- **Auth Utils:** JWT verification for Supabase tokens
- **Physics Utils:** NumPy for parameter sampling
- **Reporting:** AI-driven text generation + FPDF for PDF export

---

## Recent Changes (March 2026)

### March 4, 2026 (Compliance & Documentation Expansion)
- **Legal & Compliance:**
  - Implemented **California Consumer Privacy Act (CCPA)** and **Data Processing Addendum (DPA)** pages.
  - Added a comprehensive **Cookie Policy** page.
  - Developed and integrated a global **Cookie Consent Banner** with persistent storage and California-specific opt-out logic.
- **Documentation & Reference:**
  - Created a dedicated **Documentation** page covering SUNDIALS, MFEM, and AI Engine integrations.
  - Launched an interactive **API Reference** page detailing endpoints, authentication, and error handling.
  - Added an **About** page detailing the SimHPC mission and engineering values.
- **Site Navigation & Footer:**
  - Streamlined Footer by removing Careers/Blog/GitHub and adding legal compliance links (CCPA, DPA).
  - Updated social media presence: Migrated Twitter icon to **X branding**.
  - Improved header navigation with direct links to Documentation and About.
- **Visual & Brand Consistency:**
  - Standardized **PageLayout** across all pages to ensure consistent header/footer and theme responsiveness.
  - Refined **SimHPC Logo** to ensure "SIM" text renders in absolute black during day mode for better brand definition.
  - Verified mobile responsiveness for all newly added pages and components.

### March 4, 2026 (Auth & Report Hardening)
- **Supabase Integration:**
  - Implemented Google OAuth and Email Magic Link sign-in in `SignIn.tsx`.
  - Added `supabase.ts` client and `useAuth` hook for frontend session management.
  - Created `auth_utils.py` for backend JWT verification.
  - Updated `api.py` to use Supabase JWT for authenticated requests.
- **Kimi AI SDK:** Added `openai>=1.0.0` to requirements.txt (Moonshot AI uses OpenAI-compatible API)
- **AI Report Service:**
  - Implemented Kimi API calls with proper system prompts for scientific tone
  - Made template generation data-driven by parsing JSON context from prompts.
  - Tightened temperature integrity regex (`\b\d{2,4}(?:\.\d+)?\s*K\b`) to prevent false positives.
  - Converted `get_ai_report_service` to a proper singleton for multi-worker efficiency.
  - Added HTML escaping and newline normalization (\n/\r\n) to `to_html()` for XSS prevention and consistent rendering.
- **Fallback System:** Graceful fallback to template generation if Kimi API unavailable
- **Dockerfile:**
  - Added environment variables for KIMI_API_KEY, KIMI_MODEL, SUPABASE_JWT_SECRET, SIMHPC_API_KEY
  - Added auto-download of DejaVu fonts if not present
  - Added HEALTHCHECK for container orchestration
  - Optimized layer caching (system deps → requirements → app code)
- **API (api.py):**
  - Lazy API key validation (no runtime error if not set at import)
  - Redis connection validation at startup
  - Graceful handling when API key not configured
- **PDF Service:** Added font path hardening with multiple fallback locations
- **Dockerignore:** Created to reduce build context size

### March 3, 2026 (Bug Fixes & Security Hardening)
- **API (api.py):**
  - Fixed corrupted `RobustnessRunRequest` Pydantic model.
  - Fixed active run counter by using `hget` on Redis hashes instead of `get`.
  - Removed redundant `.decode()` calls in `get_job()` (handled by `decode_responses=True`).
  - Decoupled AI report plan check from run submission to allow flexible generation.
  - Removed hardcoded fallback API key; service now requires `SIMHPC_API_KEY` environment variable.
  - Implemented real JWT verification using `python-jose` with `JWT_SECRET_KEY` support.
  - Optimized PDF endpoint to use `BytesIO` and `Response` for direct streaming without disk I/O.
  - Fixed `UserPlan` enum normalization in background tasks.
- **Robustness Service (robustness_service.py):**
  - Fixed `non_convergent_count` type mismatch in results summary.
  - Added seeded RNG to `SimulationRunner` for fully reproducible physics approximations.
  - Implemented `MAX_CACHE_SIZE` for `baseline_cache` with FIFO eviction to prevent memory leaks.
  - Improved `_percentage_sampling` to use true uniform distribution instead of alternating sweeps.
  - Added graceful fallback for `SobolAnalyzer` when enterprise modules are missing.
  - Fixed `run_robustness_analysis` signature mismatch in demo code.
- **AI Report Service (ai_report_service.py):**
  - Made template generation data-driven by parsing JSON context from prompts.
  - Tightened temperature integrity regex (`\b\d{2,4}(?:\.\d+)?\s*K\b`) to prevent false positives.
  - Converted `get_ai_report_service` to a proper singleton for multi-worker efficiency.
  - Added HTML escaping and newline normalization (\n/\r\n) to `to_html()` for XSS prevention and consistent rendering.- **Infrastructure (pdf_service.py & Dockerfile):**
  - Resolved font loading failures by using paths relative to `__file__`.
  - Hardened Docker image with `appuser` non-root account and proper permission ownership.
  - Streamlined container startup by running `uvicorn` directly, removing redundant CORS middleware layers.

### March 2, 2026
- **Visual Design:** Updated day mode background to premium off-white (#fdfbf6).
- **Navigation:** Decoupled Pricing from landing page into a dedicated high-conversion page.
- **Billing Integration:** Integrated Stripe/Clover checkout sessions with tiered compute plans.
- **Responsive UX:** Implemented mobile-first sidebar drawer and header for the Dashboard.
- **Frontend Refactoring:** Standardized layout components (Navigation/Footer) across all routes.
- **Deployment:** Successfully deployed frontend to Vercel with custom domain (https://simhpc.com).
- **Backend Sync:** Unified CORS for production and fixed missing dependencies for RunPod updates.

### March 1, 2026
- **Distributed State:** Migrated from in-memory to Redis-backed job storage and rate limiting.
- **Scientific AI Governance:** Enforced length and keyword constraints on all engineering reports.
- **Numerical Verification:** Added automated anchor system to verify AI reports against solver metrics.
- **Compute Efficiency:** Implemented baseline caching and clamped input perturbations.
- **Resilient AI:** Integrated Tenacity retry logic for more reliable LLM report generation.
- **Unified Auth:** Implemented middleware supporting both JWT and X-API-Key authentication.
- **Monte Carlo:** Added standard Monte Carlo sampling method for baseline uncertainty studies.
- **Distributed Architecture:** Transitioned from monolithic API to Orchestrator-Worker pattern using Docker Compose.

---

## Architectural Improvements

### AI Report Service (`ai_report_service.py`) ✅ COMPLETED

#### 1. Multi-User Safe Cache System ✅
- **Current:** File-based cache (`./ai_report_cache`) without user/simulation scoping
- **Issues:** No expiration, no concurrency protection, race conditions on parallel writes
- **Fix:** Migrate to Redis-backed cache with per-user and per-simulation scoping, TTL enforcement, and atomic operations

#### 2. Stable Report ID Hashing ✅
- **Current:** `json.dumps(data, sort_keys=True)` vulnerable to float precision drift and dict ordering
- **Fix:** Normalize floats (round), strip metadata fields, define canonical schema before hashing

#### 3. Enhanced Vocabulary Enforcement ✅
- **Current:** Only enforces prohibited phrases
- **Fix:** 
  - Enforce allowed indicator usage
  - Block speculative language
  - Block modal certainty drift
  - Add Pydantic validation for structured JSON output from LLM

#### 4. Singleton Pattern Safety ✅
- **Current:** Global singleton not safe for multi-worker Uvicorn/Gunicorn
- **Fix:** Remove reliance on singleton for shared cache; use Redis for all shared state

#### 5. Deterministic Metadata Lock ✅
- **Current:** Only stores `input_hash` and `version`
- **Fix:** Add structured metadata:
  - `simulation_id`, `solver_version`, `mesh_checksum`, `parameter_hash`
  - `ai_prompt_version` for cache versioning

---

### Robustness Service (`robustness_service.py`) ✅ COMPLETED

#### 1. Deterministic Isolation ✅
- **Principle:** Robustness layer must NEVER call AI, modify solver outputs, or reformat results
- **Contract:** `run_simulation(params) → raw_result`, `aggregate_results(results) → statistics`

#### 2. Random Seed Control (Enterprise Critical) ✅
- **Current:** No seed parameter or logging
- **Fix:** 
  - Accept user-defined seed parameter
  - Log seed in metadata: `random.seed(user_defined_seed)`, `np.random.seed(user_defined_seed)`
  - Return seed in metadata for reproducibility

#### 3. Concurrency & GPU Safety ✅
- **Current:** ThreadPoolExecutor for CPU-bound work
- **Fix:** Use `ProcessPoolExecutor` or external worker system; implement GPU over-subscription guards

#### 4. Sensitivity Ranking Correctness ✅
- **Fix:** 
  - Normalize influence coefficients
  - Guard against zero variance with epsilon
  - Handle signed values and ranking stability for close values

#### 5. Non-Convergence Handling ✅
- **Fix:**
  - Track failed runs separately
  - Exclude from variance calculations
  - Log all non-convergent cases with reason

#### 6. Statistical Integrity ✅
- **Current:** Confidence intervals assume normal distribution
- **Fix:** Document distribution assumption in metadata

#### 7. Structured Output ✅
- **Fix:** Return structured object:
  ```python
  {
    "raw_results": [...],
    "statistics": {...},
    "metadata": {
      "seed", "sampling_method", "run_count", "solver_version"
    }
  }
  ```

---

### API Layer (`api.py`) ✅ COMPLETED

#### 1. Authentication Enforcement ✅
- **Critical:** All protected endpoints must validate JWT and extract user ID
- **Never trust frontend for plan checks or rate limits**

#### 2. Token/Plan Enforcement (Backend) ✅
- **Enforce inside API layer:**
  ```python
  if user.plan == "free" and run_count > 5:
      raise HTTPException(403)
  ```

#### 3. AI Report Endpoint Metering ✅
- **Critical:** Check subscription, deduct tokens, prevent double deduction
- **Implement idempotency key to prevent retry charges**

#### 4. Background Tasks for Long-Running Simulations ✅
- **Current:** Blocking request handler
- **Fix:** Submit job → Return job_id → Poll status → Store results

#### 5. Input Validation ✅
- **Fix:** Use Pydantic models for all request types to prevent missing fields, type mismatches, and malicious payloads

#### 6. Rate Limiting ✅
- **Apply to:** Report generation, simulation runs, status polling
- **Use Redis-backed rate limiters

---

### Enterprise Readiness Gaps ✅ COMPLETED

Required for enterprise clients:
- [x] Solver version logged in all responses
- [x] Random seed logged and returned in metadata
- [x] Reproducibility guarantee with seed
- [x] Raw run data export capability
- [x] AI report versioning
- [x] Robustness algorithm versioning

### Tiered Access Model

| Feature | Free | Professional | Enterprise |
|---------|------|--------------|------------|
| Simulation runs | 5 max | 50 | Unlimited |
| Perturbation runs | 5 | 50 | Unlimited |
| AI reports | - | ✓ | ✓ |
| PDF export | - | ✓ | ✓ |
| Cached reports | - | ✓ | ✓ |
| API access | - | - | ✓ |
| Custom sampling | - | - | ✓ |
| Priority queue | - | - | ✓ |

---

## Technical Summary

### Live Architecture
- **Website (Frontend):** Deployed to Vercel (https://simhpc.com)
- **Physics Core (Backend):** NVIDIA A40 GPU Instance on RunPod
- **API Endpoint:** Available via RunPod proxy

---

*Last Updated: March 3, 2026*
