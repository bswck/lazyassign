# lazyassign
Lazily assigned variables in Python

## Example
```py
def factory(scope):
    return "hello"

var = LazyAssignment(name="var", factory=factory, scope="local")

def func():
    # on first 'var' expression f_locals['var'] = factory(f_locals) is triggered
    print(var, type(var))

print(var)  # prints the lazy variable object because of scope="local" (this is global scope)
func()
```
outputs
```
<LazyAssignment 'var' scope='local'>
hello <class 'str'>
```
