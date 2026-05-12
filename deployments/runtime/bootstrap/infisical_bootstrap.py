"""
Infisical secret hydration at kernel boot.
Called before any other kernel subsystem initializes.
"""

from __future__ import annotations

import os

from infisical_client import Client, GetSecretsOptions


async def bootstrap_secrets():
    token = os.environ.get("INFISICAL_TOKEN")
    if not token:
        raise RuntimeError("INFISICAL_TOKEN environment variable not set")

    client = Client(token=token)

    secrets = client.secrets.list(GetSecretsOptions(environment="prod", path="/simhpc"))

    for secret in secrets:
        os.environ[secret.secretKey] = secret.secretValue
