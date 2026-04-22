from typing import Any, TypedDict


class TaskPayload(TypedDict):
    task: str
    inputs: dict
    context: dict


class TaskResult(TypedDict):
    result: Any
