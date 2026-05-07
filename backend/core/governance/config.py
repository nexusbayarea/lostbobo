from pydantic_settings import BaseSettings, SettingsConfigDict


class GovernanceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GOV_", env_file=".env", extra="ignore")

    # Request limits
    USER_REQUEST_RPM: int = 20
    USER_REQUEST_RPH: int = 200

    # Token budget
    TOKEN_BUDGET_HOURLY: int = 500_000
    MAX_CONTEXT_TOKENS: int = 12000
    MAX_COMPLETION_TOKENS: int = 4000

    # Streaming
    MAX_STREAM_SECONDS: int = 60
    MAX_STREAM_IDLE_SECONDS: int = 30

    # Simulation (A40 protection)
    MAX_CONCURRENT_SIMULATIONS: int = 2
    MAX_QUEUE_DEPTH: int = 20
    SIMULATION_COST_UNITS: int = 50

    # Agent / A2A protection
    MAX_AGENT_HOPS: int = 5
    MAX_RECURSION_DEPTH: int = 3

    # Priority weights
    PRIORITY_WEIGHTS: dict[str, int] = {"critical": 100, "premium": 50, "normal": 10, "background": 1}


# Singleton
_gov_settings: GovernanceSettings | None = None


def get_governance_settings() -> GovernanceSettings:
    global _gov_settings
    if _gov_settings is None:
        _gov_settings = GovernanceSettings()
    return _gov_settings
