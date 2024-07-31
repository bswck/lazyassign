from injection import injection

k: int

k_inj = injection("k", into=locals(), dynamic=True, factory=lambda sc: 5)

print(k)  # 5
print("k" in locals())  # True
print(type(k))  # <class 'int'>
print(next(type(key) for key in locals() if key == "k"))  # <class 'InjectionKey'>
