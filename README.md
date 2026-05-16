# SimHPC Gamma — Containerized Distributed Runtime

Distributed HPC simulation platform with RAG, multi-agent orchestration, and GPU-accelerated simulation.

## Architecture

```
┌──────────────┐    ┌────────────┐    ┌──────────────┐
│   Gateway    │───▶│ RAG Service│───▶│    Ollama    │
│  (FastAPI)   │    │  (gRPC)    │    │  (Embeddings)│
├──────────────┤    ├────────────┤    ├──────────────┤
│   Redis      │    │  Worker    │    │Module Runtime│
│  (Queues)    │    │ (Consumer) │    │ (Plugin Host)│
├──────────────┤    └────────────┘    └──────────────┘
│  Supabase    │
│  (pgvector)  │
└──────────────┘

GPU Node:
┌──────────────────┐
│Simulation Runtime│
│  (gRPC, CUDA)    │
└──────────────────┘
```

## Quick Start

```bash
cp deployment/.env.example .env
# Edit .env with Supabase credentials and JWT secret

docker compose -f deployment/docker-compose-cpu.yml up --build -d
bash deployment/scripts/health-check.sh
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Gateway | 8080 | API ingress, auth, routing |
| RAG | 50051 | Embeddings, retrieval, GraphRAG |
| Ollama | 11434 | Local LLM inference |
| Module Runtime | 50052 | Plugin host (EV, Trading) |
| Worker | - | Background job processor |
| Redis | 6379 | Queues, caching |
| Simulation (GPU) | 50053 | Physics simulation on A40 |

## Deployment Workflow

1. **Develop locally**: `docker compose up --build`
2. **Push to GitHub**: CI builds and pushes images to GHCR
3. **Deploy to RunPod**: `git pull && docker compose pull && docker compose up -d`

## Environment Variables

See `deployment/.env.example` for all required variables.
