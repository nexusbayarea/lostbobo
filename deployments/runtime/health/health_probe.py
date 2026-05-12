#!/usr/bin/env python3
"""Docker health check — calls the kernel health endpoint."""

from __future__ import annotations

import sys

import httpx


def main():
    try:
        resp = httpx.get("http://localhost:8000/health", timeout=5)
        if resp.status_code == 200 and resp.json().get("healthy"):
            sys.exit(0)
    except Exception:
        pass
    sys.exit(1)


if __name__ == "__main__":
    main()
