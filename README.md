# lazyassign
Lazily assigned variables in Python

## Example
```py
def assigned(scope):
    return "hello"

var = LazyVariable(assigned, name="var", scope="function")

def func():
    # on first 'var' expression f_locals['var'] = assigned(f_locals) is triggered
    print(var, type(var))

func()
```
outputs
```
hello <class 'str'>
```
