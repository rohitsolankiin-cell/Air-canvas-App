"""Hook manager for Air Canvas extension points."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, DefaultDict, Dict, List

Callback = Callable[..., Any]


class EventHook:
    """A simple multi-subscriber event object."""

    def __init__(self) -> None:
        self._callbacks: List[Callback] = []

    def register(self, callback: Callback) -> None:
        self._callbacks.append(callback)

    def unregister(self, callback: Callback) -> None:
        self._callbacks.remove(callback)

    def emit(self, *args: Any, **kwargs: Any) -> None:
        for callback in list(self._callbacks):
            callback(*args, **kwargs)


class HookManager:
    """Registry of named hooks for runtime extension and event handling."""

    def __init__(self) -> None:
        self._hooks: DefaultDict[str, EventHook] = defaultdict(EventHook)

    def register(self, event_name: str, callback: Callback) -> None:
        self._hooks[event_name].register(callback)

    def unregister(self, event_name: str, callback: Callback) -> None:
        self._hooks[event_name].unregister(callback)

    def emit(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        self._hooks[event_name].emit(*args, **kwargs)


hooks = HookManager()
