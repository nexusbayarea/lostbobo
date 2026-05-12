from backend.core.skill.models import ToolDefinition


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register_tool(self, tool: ToolDefinition):
        self._tools[tool.name] = tool

    def unregister_tool(self, name: str):
        self._tools.pop(name, None)

    def get_tool(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)

    def call_tool(self, name: str, *args, **kwargs):
        tool = self._tools.get(name)
        if not tool:
            raise KeyError(f"Tool {name} not found")
        return tool.function(*args, **kwargs)
