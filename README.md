# lazyassign
Lazily assigned variables in Python

## Example
```py
def provide(scope):
    return "hello"

var = LazyVariable(provide, scope="function")

def func():
    # on first 'var' expression f_locals['var'] = provide(f_locals) is triggered
    print(var, type(var))

func()
```
outputs
```
hello <class 'str'>
```
