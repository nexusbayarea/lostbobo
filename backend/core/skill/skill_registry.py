from __future__ import annotations

from backend.core.skill.models import SkillDefinition


class SkillRegistry:
    def __init__(self):
        self._skills: dict[str, SkillDefinition] = {}

    def register_skill(self, skill: SkillDefinition):
        self._skills[skill.name] = skill

    def unregister_skill(self, name: str):
        self._skills.pop(name, None)

    def get_skill(self, name: str) -> SkillDefinition | None:
        return self._skills.get(name)

    def list_skills(self) -> list[str]:
        return list(self._skills.keys())
