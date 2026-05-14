from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from collections.abc import Awaitable

EventHandler = Callable[[dict], Awaitable[None]]


class EventAlreadyRegistered(Exception):
    pass


class EventNotRegistered(Exception):
    pass


@dataclass
class EventHandlerEntry:
    event_type: str
    handler: EventHandler
    plugin_name: str
    filter_expression: Optional[str] = None
    priority: int = 0


class EventRegistry:
    def __init__(self):
        self._handlers: Dict[str, List[EventHandlerEntry]] = {}

    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
        plugin_name: str,
        filter_expression: Optional[str] = None,
        priority: int = 0,
    ) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(
            EventHandlerEntry(
                event_type=event_type,
                handler=handler,
                plugin_name=plugin_name,
                filter_expression=filter_expression,
                priority=priority,
            )
        )
        self._handlers[event_type].sort(key=lambda e: e.priority, reverse=True)

    def unsubscribe(self, event_type: str, plugin_name: str) -> None:
        handlers = self._handlers.get(event_type, [])
        self._handlers[event_type] = [h for h in handlers if h.plugin_name != plugin_name]

    def get_handlers(self, event_type: str) -> List[EventHandlerEntry]:
        return self._handlers.get(event_type, [])

    async def dispatch(self, event_type: str, payload: Dict[str, Any]) -> None:
        handlers = self.get_handlers(event_type)
        for entry in handlers:
            await entry.handler(payload)

    def list_subscribed_events(self, plugin_name: str) -> List[str]:
        return [
            event_type
            for event_type, handlers in self._handlers.items()
            for h in handlers
            if h.plugin_name == plugin_name
        ]

    @property
    def registered_events(self) -> List[str]:
        return list(self._handlers.keys())
