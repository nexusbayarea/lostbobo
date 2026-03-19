# SimHPC Development Guidelines

## Project Structure
We follow a strict monorepo structure to separate concerns and protect intellectual property.

- **`apps/`**: Deployable applications (e.g., React frontend, Next.js starter).
- **`services/`**: Backend microservices and workers.
- **`packages/`**: Shared libraries, SDKs, and internal tools.
- **`docs/`**: Centralized documentation.

## Best Practices
1. **Isolation**: Maintain clear boundaries between apps and services. Do not cross-import code directly between them; use shared `packages/` if necessary.
2. **Environment**: Store all secrets in `.env` (root or per-service). Never commit `.env` files. For Vercel, inject `VITE_` vars via Dashboard or `vercel-envs` in workflow. For GitHub Pages, pass secrets in the `env:` block of the build step.
3. **Documentation**: Keep `README.md` and `ARCHITECTURE.md` updated with any structural changes.
4. **Consistency**: Follow existing naming conventions (kebab-case for folders).
5. **Cleanliness**: Regularly clean up temporary files, build artifacts, and logs.

## Deployment Notes
- **Vercel is Production Primary**: Handles `VITE_` env injection, SPA routing, and CSP for Stripe/Supabase automatically.
- **GitHub Pages is Backup/Staging**: Requires manual env var injection in workflow and CSP meta tag in `index.html`.
- **Known Issue (v1.6.0-ALPHA)**: GitHub Pages fails with "Supabase Credentials Missing" and CSP violations. Fix: add `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` to GitHub Secrets and pass them in the build step.
- **Custom Domain (v2.1.2)**: App at `simhpc.nexusbayarea.com`, Auth at `auth.nexusbayarea.com`. DNS: A `@ → 76.76.21.21`, CNAME `auth → [project-ref].supabase.co`. Update Supabase Redirect URLs and Stripe JS Origins after domain is live.

## Toast System (v2.1.2)
- **Library**: sonner (`^2.0.7`)
- **Mount Point**: `<Toaster />` in `src/App.tsx`
- **Config**: 6s default, 8s success, 10s error, 350px min-width, bottom-right, cyan theme `#00f2ff`, rounded corners
- **Pattern**: `toast.promise()` for submission; `toast.loading()` → `toast.success/error()` with same ID for other async ops
- **CSS**: Overrides in `src/index.css` for dark terminal styling
- **Realtime**: `useSimulationUpdates` hook subscribes to Supabase `simulation_history` table — triggers 10s completion toast at top-center

## Tooling
- **PowerShell**: Used for local environment management.
- **Docker Compose**: Used for local orchestration of services.
- **Vercel**: Primary hosting and deployment platform for the frontend.
- **Git**: Primary version control. Do not stage/commit unless requested.

---

## Appendix: Mercury AI Usage in Alpha

### 1. Where Mercury Is Used in Alpha

In your current Alpha architecture, **Mercury should only be used in two places**:

#### 1️⃣ Simulation Setup Assistance

Mercury helps interpret user inputs into simulation parameters.

Example:

User input:
```
simulate high temperature stress
```

Mercury converts it into structured parameters:
```
temperature: 45
duration: 48h
wind: moderate
```

Then the simulation module runs.

So the flow is:
```
User Input
↓
Mercury interpretation
↓
Simulation parameters
↓
RunPod simulation
```

#### 2️⃣ Notebook Generation

Mercury writes the **explanatory text** inside the notebook.

Example:

Simulation output:
```
voltage_drop = 8%
temperature = 42C
```

Mercury generates:
```
The simulation indicates that elevated temperatures resulted in an 8% voltage drop,
suggesting increased thermal stress on the battery system.
```

So the flow is:
```
Simulation results
↓
Mercury explanation
↓
Notebook summary
```

### 2. Where Mercury Should NOT Be Used in Alpha

Avoid using Mercury for:

❌ actual physics simulations
❌ experiment selection
❌ simulation validation

### 3. Simple Mercury Health Test

The easiest test is to create a **test endpoint**.

Example:

Node.js example:
```javascript
export async function testMercury(req, res) {
  const response = await fetch("https://api.inceptionlabs.ai/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${process.env.MERCURY_API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "mercury",
      messages: [
        { role: "user", content: "Return the word SIMHPC_OK" }
      ]
    })
  });

  const data = await response.json();
  res.json(data);
}
```

Expected response:
```
SIMHPC_OK
```

If you get that, Mercury is working.

### 4. Test From Terminal

You can test Mercury directly with curl:
```
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

Expected output:
```
SIMHPC_OK
```

### 5. What Alpha Mercury Usage Should Look Like

Ideal Alpha flow:
```
User runs simulation
↓
RunPod executes model
↓
Results returned
↓
Mercury writes explanation
↓
Notebook generated
```

So Mercury is **assistive**, not core.

### 6. Quick Mercury Test Inside Your System

The fastest test you can run right now:

Add this temporary call inside notebook generation:

Prompt:
```
Explain the following simulation result in one sentence.
```

If the notebook text appears → **Mercury is working**.
