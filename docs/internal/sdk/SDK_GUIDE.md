# SimHPC Skill Developer Kit (SDK)

This guide defines how to wrap a specialized simulation model into a **SimHPC Gamma Module**.

## 1. Directory Structure
Every skill must reside in the `skills/` workspace. Use the following boilerplate:

```text
/skills/[skill-name]/
├── pyproject.toml      # Dependency lock for this specific skill
├── manifest.json       # Metadata for the Registry
├── main.py             # Entry point (The Handler)
└── solver/             # (Optional) JIT-loaded physics binaries
```

## 2. The Skill Manifest (manifest.json)
The orchestrator uses this to provision the correct hardware on RunPod.

```json
{
  "slug": "market-physics",
  "display_name": "Market Dynamics and Alpha Solver",
  "category": "finance",
  "entry_point": "skills.market_physics.main:execute_node",
  "requirements": {
    "gpu": true,
    "min_vram": 12,
    "cuda_version": "12.1"
  }
}
```

## 3. The Implementation (main.py)
All skills must implement the `execute_node` function.

```python
from backend.lib.contracts import SkillResponse
from backend.lib.logging import logger

def execute_node(node_id: str, params: dict, context: dict) -> SkillResponse:
    """
    Standard entry point for SimHPC Gamma Modules.
    """
    logger.info(f"Skill execution started for Node: {node_id}")
    
    try:
        # 1. Your Specialized Physics/Logic here
        # 2. Return the standard contract response
        return SkillResponse(
            status="success",
            payload={"alpha": 0.042, "variance": 0.001},
            trace_hash=context['expected_hash']
        )
    except Exception as e:
        return SkillResponse(status="error", message=str(e))
```

## 4. Deployment Workflow
1. **Archive:** Compress the skill folder: `tar -czvf skill-market.tar.gz skills/market-physics/`.
2. **Hash:** Generate the fingerprint: `sha256sum skill-market.tar.gz`.
3. **Registry:** Insert the metadata into the `skill_registry` table in Supabase.
4. **Storage:** Upload the `.tar.gz` to the `sim-assets` bucket.
