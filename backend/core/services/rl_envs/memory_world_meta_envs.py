import gymnasium as gym
import numpy as np

from backend.kernel.kernel import Kernel


class ObservationalMemoryRLEnv(gym.Env):
    def __init__(self, kernel: Kernel):
        super().__init__()
        self.kernel = kernel
        self.action_space = gym.spaces.Discrete(4)
        self.observation_space = gym.spaces.Box(low=-1, high=1, shape=(128,), dtype=np.float32)

    def step(self, action):
        result = self.kernel.command_bus.route_sync({"type": "OBSERVE_REFLECT", "payload": {"rl_action": int(action)}})
        reward = float(
            result.get("convergence_improved", 0.0) * 0.8 + (1.0 if not result.get("loop_detected") else -1.0)
        )
        obs = self.kernel.services["cognition"].get_fused_vector(result)
        return obs, reward, False, False, {}

    def reset(self, *, seed=None, options=None):
        return np.zeros(128, dtype=np.float32), {}


class WorldModelRLEnv(gym.Env):
    def __init__(self, kernel: Kernel):
        super().__init__()
        self.kernel = kernel
        self.action_space = gym.spaces.Discrete(4)
        self.observation_space = gym.spaces.Box(low=-1, high=1, shape=(128,), dtype=np.float32)

    def step(self, action):
        result = self.kernel.command_bus.route_sync(
            {"type": "WORLD_MODEL_UPDATE", "payload": {"rl_action": int(action)}}
        )
        reward = float(result.get("consistency_score", 0.0) * 0.7 + result.get("uncertainty_reduced", 0.0) * 0.3)
        obs = self.kernel.services["cognition"].get_fused_vector(result)
        return obs, reward, False, False, {}

    def reset(self, *, seed=None, options=None):
        return np.zeros(128, dtype=np.float32), {}


class MetaOrchestrationRLEnv(gym.Env):
    def __init__(self, kernel: Kernel):
        super().__init__()
        self.kernel = kernel
        self.action_space = gym.spaces.Discrete(4)
        self.observation_space = gym.spaces.Box(low=-1, high=1, shape=(128,), dtype=np.float32)

    def step(self, action):
        result = self.kernel.command_bus.route_sync({"type": "META_ROUTE", "payload": {"rl_action": int(action)}})
        reward = float(result.get("overall_efficiency", 0.0))
        obs = self.kernel.services["cognition"].get_fused_vector(result)
        return obs, reward, False, False, {}

    def reset(self, *, seed=None, options=None):
        return np.zeros(128, dtype=np.float32), {}
