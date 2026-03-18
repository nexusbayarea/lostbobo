# SimHPC Mission Control Cockpit

The SimHPC Frontend is **LIVE** and accessible at [https://simhpc.com](https://simhpc.com).

This is the public-facing repository for the SimHPC Mission Control Cockpit, a premium interface for aerospace and thermal engineering simulations.

## v1.6.0-ALPHA: Operations Center
- **TelemetryPanel**: 240Hz solver streams.
- **OperatorConsole**: High-stakes engineering actions (Intercept, Clone, Boost, Certify).
- **SimulationLineage**: Visual ancestry and Flux Delta tracking.
- **GuidanceEngine**: Mercury AI-powered strategy recommendations.

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
- **Primary**: [https://simhpc.com](https://simhpc.com)
- **Backup**: [https://NexusBayArea.github.io/lostbobo](https://NexusBayArea.github.io/lostbobo)

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
