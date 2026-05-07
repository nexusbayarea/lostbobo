from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    admin = "admin"
    analyst = "analyst"
    plugin_dev = "plugin_dev"
    viewer = "viewer"
    service = "service"


class AuthContext(BaseModel):
    """Carried everywhere in the system"""

    user_id: str
    tenant_id: str = "public"
    roles: list[Role] = Field(default_factory=list)
    agent_id: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    request_id: str | None = None

    def has_role(self, role: Role) -> bool:
        return role in self.roles or Role.admin in self.roles

    def can_access_simulation(self, estimated_cost: int = 0) -> bool:
        if Role.admin in self.roles:
            return True
        if estimated_cost > 30 and Role.analyst not in self.roles:
            return False
        return True
