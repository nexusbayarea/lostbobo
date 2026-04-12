from app.core.bootstrap import bootstrap


def init_app() -> None:
    """Initialize environment validation and normalization before app imports."""
    bootstrap()
