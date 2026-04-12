import os


class EnvError(RuntimeError):
    pass


def require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvError(f"Missing required env var: {key}")
    return value


def normalize_env():
    """
    Maps raw infra SB_* variables into internal application schema.
    No domain assumptions regarding providers (e.g. Supabase vs. Custom).
    This establishes a canonical contract between the infrastructure and the logic.
    """

    mapping = {
        # core connectivity
        "APP_URL": "SB_URL",
        "DATA_URL": "SB_DATA_URL",

        # auth/security
        "JWT_SECRET": "SB_JWT_SECRET",
        "PUBLIC_KEY": "SB_PUB_KEY",
        "SECRET_KEY": "SB_SECRET_KEY",

        # generic API token
        "API_TOKEN": "SB_TOKEN",
    }

    # Only map if the source exists, allowing for partial infra configurations
    # for specific services (e.g. Workers might only need a subset).
    for internal, external in mapping.items():
        value = os.getenv(external)
        if value is not None:
            os.environ[internal] = value
        elif internal in ("APP_URL", "API_TOKEN", "SECRET_KEY"):
            # These are strictly required for the backbone
            # We don't raise here yet to allow Pydantic to handle the validation
            # and provide a better error report.
            pass
