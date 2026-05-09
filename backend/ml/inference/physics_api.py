from dataclasses import dataclass
from enum import Enum


class ModelSource(Enum):
    SIMHPC_FINE_TUNED = "simhpc_fine_tuned"
    BASE_MODEL = "base_model"


@dataclass
class PhysicsInferenceRequest:
    task_type: str
    domain: str
    solver: str
    prompt: str
    prefer_model: ModelSource = ModelSource.SIMHPC_FINE_TUNED


class PhysicsInferenceAPI:
    async def infer(self, request: PhysicsInferenceRequest):
        # Implementation to call internal inference service
        return {"completion": "...", "confidence_score": 0.95}


def get_physics_inference_api():
    return PhysicsInferenceAPI()
