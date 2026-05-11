from __future__ import annotations

from backend.core.sdk.base_plugin import (
    BasePlugin,
)


class Plugin(BasePlugin):
    async def register(self, kernel) -> None:
        kernel.capabilities.register(
            "materials.predict",
            self.predict,
        )

    async def predict(
        self,
        payload: dict,
    ):
        return {
            "plugin": "materials",
            "payload": payload,
        }
