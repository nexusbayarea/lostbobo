from __future__ import annotations


async def solve_beam(payload: dict):
    return {
        "status": "ok",
        "solver": "beam",
        "payload": payload,
    }
