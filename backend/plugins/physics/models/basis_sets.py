from __future__ import annotations

COMMON_BASIS_SETS: list[str] = [
    "sto-3g",
    "3-21g",
    "6-31g",
    "6-31g*",
    "6-311g",
    "cc-pvdz",
    "cc-pvtz",
    "cc-pvqz",
    "aug-cc-pvdz",
    "aug-cc-pvtz",
    "def2-svp",
    "def2-tzvp",
    "def2-qzvp",
]


def is_valid_basis_set(name: str) -> bool:
    return name.lower() in {b.lower() for b in COMMON_BASIS_SETS}
