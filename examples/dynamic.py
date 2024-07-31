from __future__ import annotations

from random import randint
from typing import TYPE_CHECKING

from injection import injection

if TYPE_CHECKING:
    from injection import Locals

k: int
j: int


def random(scope: Locals) -> int:
    return randint(1, 6)


k_inj = injection("k", into=locals(), dynamic=True, factory=random)
j_inj_once = injection("j", into=locals(), dynamic=True, once=True, factory=random)


def child_scope() -> None:
    print("k", k, type(next(key for key in globals() if key == "k")))
    print("j", j, type(next(key for key in globals() if key == "j")))


for i in range(5):
    child_scope()
