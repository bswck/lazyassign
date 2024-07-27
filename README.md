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

print(var)  # prints the lazy variable object because of scope="function"
func()
```
outputs
```
<LazyVariable 'var'>
hello <class 'str'>
```
