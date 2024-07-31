from injection import injection

k: int

k_inj = injection("k", into=locals(), factory=lambda sc: 5)

print(k)  # 5
print("k" in locals())  # True
print(type(k))  # <class 'int'>
