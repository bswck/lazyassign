from random import randint
from injection import injection

k: int

k_inj = injection("k", into=locals(), dynamic=True, factory=lambda scope: randint(1, 6))

for i in range(5):
    print(k)
