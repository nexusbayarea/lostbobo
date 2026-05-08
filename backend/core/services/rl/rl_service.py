from dataclasses import dataclass
from typing import Any

import gymnasium as gym
import numpy as np
import structlog
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

from backend.app.kernel.command_bus import command_bus
from backend.core.supabase_job_store import SupabaseJobStore
from backend.kernel.kernel import Kernel

log = structlog.get_logger(__name__)


@dataclass
class RLStep:
    state_hash: str
    action: str
    reward: float
    next_state_hash: str | None
    done: bool
    metadata: dict[str, Any]


class SimHPCEnv(gym.Env):
    """Custom Gym environment using Execution Attention Graph as observation space."""

    def __init__(self, kernel: Kernel):
        super().__init__()
        self.kernel = kernel
        self.action_space = gym.spaces.Discrete(6)
        self.observation_space = gym.spaces.Box(low=-1, high=1, shape=(128,), dtype=np.float32)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        # Placeholder for real fused vector
        return np.zeros(128, dtype=np.float32), {}

    def step(self, action: int):
        # Dispatch via command bus
        action_name = ["reason", "tool_call", "reflect", "verify", "simulate", "halt"][action]
        result = self.kernel.command_bus.route_sync({"type": f"ACTION_{action_name.upper()}", "payload": {}})
        reward = float(result.get("reward", 0.0))
        done = result.get("done", False)
        obs = np.zeros(128, dtype=np.float32)
        return obs, reward, done, False, {}


class ReinforcementLearningService:
    """Kernel-centered RL for agent policy learning and simulation optimization."""

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.supabase = SupabaseJobStore()
        self.env = make_vec_env(lambda: SimHPCEnv(kernel), n_envs=1)
        self.model = PPO(
            "MlpPolicy",
            self.env,
            verbose=1,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
        )

    async def step(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Single step using current PPO policy"""
        # Get fused vector from cognition service
        obs = await self.kernel.services["cognition"].get_fused_vector(payload.get("state", {}))
        action, _ = self.model.predict(obs, deterministic=False)

        # Execute
        result = await command_bus.route({"type": "AGENT_RUN", "payload": {"agent": "autonomous", "input": payload}})

        return {"action": int(action), "reward": result.get("reward", 0.0), "next_state": result}

    def save_policy(self):
        self.model.save("models/simhpc_ppo.zip")
