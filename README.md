# avereno
Yet another retry utility in Python,
_avereno_ being the Malagasy word for _retry_.

## Usage

```python
$ python3 -m pip install avereno
$ python3
>>> from random import random
>>> def a_sometimes_failing_hello():
...   if random() < 0.5:
...     print("Hello!")
...   else:
...     raise RuntimeError()

>>> from avereno import retry
>>> retry(a_sometimes_failing_hello, on_retry=lambda __1, __2: print("Oops..."))
Oops...
Oops...
Oops...
Oops...
Hello!
```
