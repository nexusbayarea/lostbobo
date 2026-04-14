import re

def normalize(stderr: str) -> str:
    # remove paths, timestamps, hashes
    stderr = re.sub(r"/[^\s]+", "<path>", stderr)
    stderr = re.sub(r"\d+", "<num>", stderr)
    return stderr.strip()

def fingerprint(stderr: str) -> str:
    norm = normalize(stderr)
    return norm[:300]  # bounded signature
