# injection
The most implicit dependency injection Python has ever seen

## Example
```py
def factory(scope):
    return "hello"

# if once is True, the factory is called once and reused in every child scope.
# once doesnt matter for global scope setting which makes the injection
# object unretrievable after first reference (the given variable names are assigned the injected object
# and the injection object gets freed)
var = injection("var", factory=factory, scope="local", once=True)

def func():
    # on first 'var' expression f_locals['var'] = factory(f_locals) is triggered
    print(var, type(var))

print(var)  # prints the injection object because of scope="local" (this is global scope)
func()
```
outputs
```
<Injection 'var' scope='local' once=True>
hello <class 'str'>
```
