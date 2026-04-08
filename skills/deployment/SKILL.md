---
name: deployment
description: Complete deployment pipeline for SimHPC - Vercel, GitHub, Docker Hub, Supabase, and RunPod.
version: 2.5.6
license: MIT
compatibility: opencode
---

# Deployment Skill Set

Complete deployment pipeline for SimHPC v2.5.6.

## Version: 2.5.6

## Docker Images

All images pushed to Docker Hub:

| Image | Tag | Purpose |
| :--- | :--- | :--- |
| simhpcworker/simhpc-unified | latest | Combined API + Worker + Autoscaler (Port 8888) |
| simhpcworker/simhpc-worker | latest | GPU physics worker |
| simhpcworker/simhpc-api | latest | FastAPI orchestrator |
| simhpcworker/simhpc-autoscaler | latest | RunPod autoscaler |

## Supabase Keys (SB Prefix)

**Important**: Infisical doesn't allow "SUPABASE" in key names. Use SB_ prefix:

| Infisical Key | Mapped To |
|--------------|-----------|
| SB_URL | VITE_SUPABASE_URL / SUPABASE_URL |
| SB_ANON_KEY | VITE_SUPABASE_ANON_KEY / SUPABASE_ANON_KEY |
| SB_SERVICE_ROLE_KEY | SUPABASE_SERVICE_ROLE_KEY |
| SB_PROJECT_ID | Supabase project ref |

## Quick Start

Use the master deploy script for one-click deployment:

```bash
bash scripts/deploy_all.sh
```

## Master Script (deploy_all.sh)

```bash
#!/bin/bash

set -e

echo "[1/4] Syncing to GitHub..."
git add . 
git commit -m "ci: trigger docker build and deploy to RunPod"
git push origin main

echo "[2/4] Waiting for Docker build..."
sleep 30

echo "[3/4] Deploying to RunPod..."
gh workflow run auto-deploy-runpod.yml

echo "[4/4] Deployment triggered."
```

## GitHub Actions Workflow (deploy.yml)

**Important**: Uses **Infisical GitHub App Integration** (native sync). Secrets are automatically synced from Infisical to GitHub Repository secrets. No Infisical CLI needed in CI.

### Workflow Steps

1. **Checkout** - Fetch code
2. **Login to Docker Hub** - Uses natively synced secrets
3. **Build & Push** - Build unified, worker, autoscaler images
4. **Deploy to RunPod** - Trigger pod deployment

```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_LOGIN }}
    password: ${{ secrets.DOCKER_PW_TOKEN }}
```

### Required Secrets (Synced from Infisical)

| Secret | Source | Purpose |
|--------|--------|---------|
| `DOCKER_LOGIN` | Infisical → GitHub App | Docker Hub username |
| `DOCKER_PW_TOKEN` | Infisical → GitHub App | Docker Hub password/token |
| `RUNPOD_API_KEY` | Infisical → GitHub App | RunPod provisioning |
| `INFISICAL_CLIENT_ID` | GitHub Secrets | Machine Identity |
| `INFISICAL_CLIENT_SECRET` | GitHub Secrets | Machine Identity |

### Why Native Sync Works

1. **Infisical GitHub App** automatically syncs secrets to GitHub
2. **GitHub Actions** reads secrets directly from `${{ secrets.KEY }}`
3. **No CLI needed** in CI pipeline

### Troubleshooting 401 Errors

If Docker login fails:
1. Check GitHub App has **Read and Write** access to Secrets
2. Verify environment slug matches (production/beta)
3. Check secret names in GitHub Settings → Secrets → Actions

## Skills Overview

### 1. Vercel Deploy
See: `vercel-deploy.md`

Deploy frontend with Infisical secret injection.

### 2. GitHub Safe Push
See: `github-safe-push.md`

Secure push with secret scanning and linting.

### 3. Supabase Sync
See: `supabase-sync.md`

Sync SB_ secrets to VITE_SUPABASE_ for Vercel.

## Deployment Flow

```
┌─────────────────┐
│  Sync Infisical  │ ← Push latest secrets
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Sync SB Secrets │ ← Rename SB_ to VITE_SUPABASE_
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Deploy to Vercel │ ← Production build
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Git Push      │ ← Safe push with scan
└─────────────────┘
```

## Manual Steps

### Deploy RunPod (Separate)

```bash
# Build unified image
docker build -f Dockerfile.unified -t simhpcworker/simhpc-unified:latest .

# Push to Docker Hub
docker push simhpcworker/simhpc-unified:latest

# Deploy to RunPod
python scripts/deploy_unified.py
```

### Update Vercel API URL

```bash
echo "https://{POD_ID}-8000.proxy.runpod.net" | vercel env add VITE_API_URL production
vercel --prod --yes
```

## Examples

- "Deploy to Vercel with Infisical secrets"
- "Safe push to GitHub with secret scan"
- "Run the full deploy_all script"
