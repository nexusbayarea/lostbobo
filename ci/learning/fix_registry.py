def get_known_fixes():
    return [
        {
            "match": "F841",
            "fix": ["ruff", "check", ".", "--fix"]
        },
        {
            "match": "No virtual environment found",
            "fix": ["uv", "venv", "--clear"]
        },
        {
            "match": "repository name must be lowercase",
            "fix": ["bash", "-c", "echo 'Fix tag casing in workflow'"]
        },
    ]
