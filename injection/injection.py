from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import TYPE_CHECKING, Generic, TypeVar

from injection.compat import get_frame

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from typing_extensions import TypeAlias

    Locals: TypeAlias = "dict[str, Any]"


Object = TypeVar("Object")


class InjectionKey(str):
    def __init__(self, key: str, early: EarlyObject) -> None:
        self.origin = key
        self.hash = hash(key)
        self.reset = False
        self.early = early

    def __new__(cls, key: str, early: EarlyObject) -> None:
        return super().__new__(cls, key)

    def __eq__(self, other: str) -> bool:
        if self.origin != other:
            return False

        if self.reset:
            self.reset = False
            return True

        caller_locals = get_frame(1).f_locals

        if caller_locals.get("__injection_recursive_guard__"):
            return True

        with self.early.__mutex__:
            __injection_recursive_guard__ = True
            self.early.__inject__(self)
        return True

    def __hash__(self) -> int:
        return self.hash


@dataclass
class Injection(Generic[Object]):
    aliases: list[str]
    factory: Callable[[Locals], Object]
    once: bool = False
    dynamic: bool = False

    def mount(self, *, into: Locals) -> list[str]:
        dynamic = self.dynamic
        state = ObjectState(once=self.once, scope=into, factory=self.factory)
        for alias in self.aliases:
            early = EarlyObject(alias, state, dynamic)
            key = InjectionKey(alias, early)
            into[key] = early


SENTINEL = object()


class ObjectState(Generic[Object]):
    def __init__(
        self,
        once: bool,
        scope: Locals,
        factory: Callable[[Locals], Object],
    ) -> None:
        self.object = SENTINEL
        self.once = once
        self.factory = factory
        self.scope = scope

    def create(self, scope: Locals) -> None:
        if self.object is SENTINEL or not self.once:
            self.object = self.factory(scope)


class EarlyObject(Generic[Object]):
    def __init__(self, alias: str, state: ObjectState[Object], dynamic: bool) -> None:
        self.__mutex__ = RLock()
        self.__dynamic = dynamic
        self.__alias = alias
        self.__state = state

    def __inject__(
        self,
        key: InjectionKey,
    ) -> None:
        scope = self.__state.scope

        __injection_recursive_guard__ = True

        # To ever know if we're in a child scope:
        # req_scope = get_frame(1).f_locals
        # in_child_scope = next(filter(self.__alias.__eq__, req_scope), None) is None

        self.__state.create(scope)
        obj, alias = self.__state.object, self.__alias

        with self.__mutex__:
            del scope[alias]
            scope[alias] = obj

            if self.__dynamic and not self.__state.once:
                del scope[key]
                key.reset = True
                scope[key] = obj

    def __repr__(self) -> str:
        return "<early>"


def injection(
    *aliases: str,
    into: Locals | None = None,
    factory: Callable[[Locals], Object],
    once: bool = False,
    dynamic: bool = False,
) -> Injection[Object]:
    """
    Create an injection.

    Parameters
    ----------
    *aliases
        Aliases to the injection. Must be valid Python identifiers.
    into
        The [`locals()`][locals] dictionary to automatically mount into.
    factory
        A callable that creates the injected object.
    once
        Whether to only create the object once and reuse it everywhere.
    dynamic
        Whether to still trigger recreating the object in the same scope
        after successful creation. Useful as a replacement for `ContextVar` proxies.
    stack_offset
        How far (in frames) is the actual caller from this function's frame.
    """
    inj = Injection(aliases=[*aliases], factory=factory, dynamic=dynamic, once=once)
    if into is not None:
        inj.mount(into=into)
    return inj
