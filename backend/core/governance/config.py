"""
Governance Settings — Pulled from Infisical (no .env files)
"""

import logging
import subprocess

log = logging.getLogger(__name__)


class GovernanceSettings:
    """
    Dynamic settings loaded from Infisical at runtime.
    """

    def __init__(self):
        self._cache = {}
        self._load_settings()

    def _load_settings(self):
        """Fetch all governance config from Infisical"""
        try:
            # These keys should exist in your Infisical project
            self.USER_REQUEST_RPM = int(self._get_secret("GOV_USER_REQUEST_RPM", "20"))
            self.USER_REQUEST_RPH = int(self._get_secret("GOV_USER_REQUEST_RPH", "200"))

            self.TOKEN_BUDGET_HOURLY = int(self._get_secret("GOV_TOKEN_BUDGET_HOURLY", "500000"))
            self.MAX_CONTEXT_TOKENS = int(self._get_secret("GOV_MAX_CONTEXT_TOKENS", "12000"))
            self.MAX_COMPLETION_TOKENS = int(self._get_secret("GOV_MAX_COMPLETION_TOKENS", "4000"))

            self.MAX_STREAM_SECONDS = int(self._get_secret("GOV_MAX_STREAM_SECONDS", "60"))
            self.MAX_STREAM_IDLE_SECONDS = int(self._get_secret("GOV_MAX_STREAM_IDLE_SECONDS", "30"))

            self.MAX_CONCURRENT_SIMULATIONS = int(self._get_secret("GOV_MAX_CONCURRENT_SIMULATIONS", "2"))
            self.MAX_QUEUE_DEPTH = int(self._get_secret("GOV_MAX_QUEUE_DEPTH", "20"))

            self.MAX_AGENT_HOPS = int(self._get_secret("GOV_MAX_AGENT_HOPS", "5"))
            self.MAX_RECURSION_DEPTH = int(self._get_secret("GOV_MAX_RECURSION_DEPTH", "3"))

            self.PRIORITY_WEIGHTS: dict[str, int] = {"critical": 100, "premium": 50, "normal": 10, "background": 1}

            log.info("✅ Governance settings loaded from Infisical")
        except Exception as e:
            log.error(f"Failed to load governance config from Infisical: {e}")
            # Fallback to safe defaults
            self._set_defaults()

    def _get_secret(self, key: str, default: str) -> str:
        """Get secret from Infisical with fallback using CLI"""
        try:
            # Using CLI as the standard access method in the environment
            result = subprocess.run(
                ["infisical", "secrets", "get", key, "--plain"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except Exception:
            return default

    def _set_defaults(self):
        """Safe fallback values"""
        self.USER_REQUEST_RPM = 20
        self.USER_REQUEST_RPH = 200
        self.TOKEN_BUDGET_HOURLY = 500_000
        self.MAX_CONTEXT_TOKENS = 12000
        self.MAX_STREAM_SECONDS = 60
        self.MAX_CONCURRENT_SIMULATIONS = 2
        self.MAX_QUEUE_DEPTH = 20
        self.MAX_AGENT_HOPS = 5
        self.MAX_RECURSION_DEPTH = 3

    # Allow runtime refresh if needed
    def refresh(self):
        self._load_settings()


# Singleton
_gov_settings: GovernanceSettings | None = None


def get_governance_settings() -> GovernanceSettings:
    global _gov_settings
    if _gov_settings is None:
        _gov_settings = GovernanceSettings()
    return _gov_settings
