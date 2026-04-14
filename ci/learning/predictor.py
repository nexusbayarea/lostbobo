from .fix_registry import get_known_fixes

def predict(stderr: str):
    fixes = get_known_fixes()

    for f in fixes:
        if f["match"] in stderr:
            return f["fix"]

    return None
