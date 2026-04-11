---
name: ghcr-deploy
description: Deploy SimHPC to RunPod using GitHub Container Registry (GHCR) — clean, reliable, public image workflow for beta.
version: 2.8.2
license: MIT
compatibility: opencode
---

# GHCR Deploy Skill Set (v2.8.2)

**Goal**: Push from GitHub → GHCR → RunPod pod with zero 502 / IPv6 / pull errors.

### Why GHCR (Recommended for SimHPC)
- GitHub Actions can push directly (no extra Docker Hub secrets).
- Public images require **no registry auth** on RunPod.
- Clean `:latest` + SHA tags.
- Faster and more reliable than Docker Hub for this project.

---

## 1. Exact Image Reference (Use This)

```text
ghcr.io/neXusEvents/simhpc-unified:latest
```

(Replace `neXusEvents` only if your GitHub username/org is different.)

---

## 2. GitHub Workflow (`deploy.yml`) – GHCR Version

Replace your `.github/workflows/deploy.yml` with this:

```yaml
name: Deploy SimHPC (GHCR)

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build & Push to GHCR
        uses: docker/build-push-action@v6
        with:
          context: .
          file: ./Dockerfile.unified
          push: true
          tags: ghcr.io/${{ github.repository_owner }}/simhpc-unified:latest,ghcr.io/${{ github.repository_owner }}/simhpc-unified:${{ github.sha }}
          platforms: linux/amd64
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Update RunPod + podReset
        env:
          RUNPOD_API_KEY: ${{ secrets.RUNPOD_API_KEY }}
          RUNPOD_ID: ${{ secrets.RUNPOD_ID }}
        run: |
          echo "Updating pod $RUNPOD_ID to ghcr.io/${{ github.repository_owner }}/simhpc-unified:latest"

          # Stop → Update image → Start (forces fresh pull)
          curl -s -X POST "https://api.runpod.io/graphql" \
            -H "Authorization: Bearer $RUNPOD_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"mutation { podStop(input: { podId: \\\"$RUNPOD_ID\\\" }) { id } }\"}" || true

          sleep 20

          curl -s -X POST "https://api.runpod.io/graphql" \
            -H "Authorization: Bearer $RUNPOD_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"mutation { podUpdate(input: { podId: \\\"$RUNPOD_ID\\\", imageName: \\\"ghcr.io/${{ github.repository_owner }}/simhpc-unified:latest\\\" }) { id } }\"}"

          sleep 10

          curl -s -X POST "https://api.runpod.io/graphql" \
            -H "Authorization: Bearer $RUNPOD_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"mutation { podResume(input: { podId: \\\"$RUNPOD_ID\\\", gpuCount: 1 }) { id } }\"}"

          echo "Waiting 90 seconds for startup..."
          sleep 90

          # Health check
          for i in {1..8}; do
            STATUS=$(curl -s -o /dev/null -w "%{http_code}" -m 12 "https://$RUNPOD_ID-8080.proxy.runpod.net/api/v1/health" || echo "000")
            echo "Attempt $i → $STATUS"
            if [ "$STATUS" = "200" ]; then
              echo "✅ API is healthy!"
              exit 0
            fi
            sleep 12
          done

          echo "❌ Health check failed"
          exit 1
```

---

## 3. Final `Dockerfile.unified` (Optimized)

```dockerfile
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PYTHONPATH=/app

WORKDIR $APP_HOME

RUN apt-get update && apt-get install -y --no-install-recommends curl tini && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py worker.py start.sh ./
COPY app/ ./app/

RUN chmod +x start.sh && mkdir -p /workspace

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["./start.sh"]
```

---

## 4. Final `start.sh`

```bash
#!/bin/bash
set -e
echo "🚀 [SimHPC] Starting Unified Pod - GHCR Beta ($(date))"
fuser -k 8080/tcp || true
exec python3 -m uvicorn api:app --host 0.0.0.0 --port 8080 --workers 2 --log-level info
```

---

## Next Steps (Do This Now)

1. Save the files above.
2. Commit & push:

```bash
git add Dockerfile.unified start.sh .github/workflows/deploy.yml requirements.txt api.py
git commit -m "beta: switch to GHCR + clean unified deploy"
git push origin main
```

3. GitHub will build → push to GHCR → update your pod.

After the workflow finishes, test:

```powershell
Invoke-WebRequest -Uri "https://ikzejthq1q7yt9-8080.proxy.runpod.net/api/v1/health" -TimeoutSec 15
```

---

**This SKILL.md** is now your single source of truth for GHCR + RunPod deployments.

