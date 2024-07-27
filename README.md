# injection
The most implicit dependency injection Python has ever seen

## Example
```py
def factory(scope):
    return "hello"

# if once is True, the factory is called once and reused in every child scope
# if the scope is global, the injection is unretrievable after first reference and replaced with the injected object
var = injection(name="var", factory=factory, scope="local", once=True)

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
