from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import TYPE_CHECKING, Generic, TypeVar

from injection.compat import get_frame

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from typing_extensions import ParamSpec, TypeAlias

    Locals: TypeAlias = "dict[str, Any]"


Object = TypeVar("Object")


class InjectionKey(str):
    def __init__(self, key: str, early: EarlyObject) -> None:
        self.__origin = key
        self.__hash = hash(key)
        self.__reset__ = False
        self.__early = early

    def __new__(cls, key: str, early: EarlyObject) -> None:
        return super().__new__(cls, key)

    def __eq__(self, other: str) -> bool:
        if self.__origin != other:
            return False

        if self.__reset__:
            self.__reset__ = False
            return True

        caller_locals = get_frame(1).f_locals

        if caller_locals.get("__no_inject__"):
            return True

        with self.__early.__mutex__:
            __no_inject__ = True
            self.__early.__inject__(caller_locals)
        return True

    def __hash__(self) -> int:
        return self.__hash


@dataclass
class Injection(Generic[Object]):
    aliases: list[str]
    factory: Callable[[Locals], Object]
    once: bool = False
    dynamic: bool = False

    def mount(self, *, into: Locals) -> list[str]:
        dynamic = self.dynamic
        state = ObjectState(once=self.once, factory=self.factory)
        for alias in self.aliases:
            early = EarlyObject(alias, state, dynamic)
            key = InjectionKey(alias, early)
            into[key] = early


SENTINEL = object()


class ObjectState(Generic[Object]):
    object: Object

    def __init__(self, once: bool, factory: Callable[[Locals], Object]) -> None:
        self.object = SENTINEL
        self.once = once
        self.factory = factory

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
        scope: Locals | None = None,
    ) -> None:
        if scope is None:
            scope = get_frame(1).f_locals

        __no_inject__ = True

        key = next(filter(self.__alias.__eq__, scope), None)
        if key is None:
            return

        self.__state.create(scope)
        obj, alias = self.__state.object, self.__alias

        with self.__mutex__:
            del scope[alias]
            scope[alias] = obj

            if self.__dynamic:
                del scope[alias]
                key.__reset__ = True
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
