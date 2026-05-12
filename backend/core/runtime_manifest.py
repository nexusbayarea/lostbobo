from __future__ import annotations

import os

from pydantic import BaseModel


class RuntimeManifest(BaseModel):
    kernel_version: str = "1.0.0"
    image_hash: str = "dev"
    cuda_version: str = "12.4"
    torch_version: str = "2.4.0"
    plugin_abi: str = "1.0.0"

    @classmethod
    def from_env(cls) -> RuntimeManifest:
        return cls(
            image_hash=os.getenv("SIMHPC_IMAGE_HASH", "dev"),
        )
