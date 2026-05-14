from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from pydantic import BaseModel, Field

SDK_VERSION = "1.0.0"


class ReproducibilityCertificate(BaseModel):
    capability: str
    plugin_name: str
    plugin_version: str
    inputs_hash: str
    outputs_hash: str | None = None
    seed: int | None = None
    kernel_version: str = SDK_VERSION
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    signature: str | None = None

    def compute_fingerprint(self) -> str:
        canonical = json.dumps(
            {
                "capability": self.capability,
                "plugin_name": self.plugin_name,
                "plugin_version": self.plugin_version,
                "inputs_hash": self.inputs_hash,
                "outputs_hash": self.outputs_hash,
                "seed": self.seed,
                "kernel_version": self.kernel_version,
                "timestamp": self.timestamp.isoformat(),
            },
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(canonical.encode()).hexdigest()

    def sign(self, private_key_pem: str) -> None:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
        fingerprint = self.compute_fingerprint()
        signature = key.sign(
            fingerprint.encode(),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        self.signature = signature.hex()

    def verify(self, public_key_pem: str) -> bool:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        key = serialization.load_pem_public_key(public_key_pem.encode())
        fingerprint = self.compute_fingerprint()
        try:
            key.verify(
                bytes.fromhex(self.signature),
                fingerprint.encode(),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except InvalidSignature:
            return False
