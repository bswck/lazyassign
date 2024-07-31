from __future__ import annotations
from typing import TYPE_CHECKING

from injection.injection import injection

if TYPE_CHECKING:
    from contextvars import ContextVar
    from typing import TypeVar

    from injection.injection import Locals, Injection

    T = TypeVar("T")


def contextvar_injection(
    *aliases: str, into: Locals, cv: ContextVar[T]
) -> Injection[T]:
    return injection(*aliases, into=into, factory=cv.get, dynamic=True)
