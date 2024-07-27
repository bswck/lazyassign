# injection
The most implicit dependency injection Python has ever seen

## Example
```py
def factory(scope):
    return "hello"

var = Injection(name="var", factory=factory, scope="local")

def func():
    # on first 'var' expression f_locals['var'] = factory(f_locals) is triggered
    print(var, type(var))

print(var)  # prints the injection object because of scope="local" (this is global scope)
func()
```
outputs
```
<LazyAssignment 'var' scope='local'>
hello <class 'str'>
```
