# avereno
Yet another retry utility in Python,
_avereno_ being the Malagasy word for _retry_.

## Usage

```python
$ python3 -m pip install avereno
$ python3
from random import random
def a_sometimes_failing_hello():
    if random() < 0.5:
      print("Hello!")
    else:
      raise RuntimeError()

from avereno import retry
retry(a_sometimes_failing_hello, on_retry=lambda __1, __2: print("Oops..."))
> Oops...
> Oops...
> Oops...
> Hello!
```

## Features

The retry policy can be customized through the following arguments,
as described in `help(avereno.retry)`:

```
Optional Keyword Arguments:
  max_retries:        number of retries after which GiveUpRetryError will be raised
  max_sleep:          cumulated sleep (backoff) after which GiveUpRetryError will be raised
  on_retry:           function to invoke _before_ each retry
  init_backoff:       initial backoff that will potentially increase afterwards
  backoff_multiplier: multiplication factor between consecutive backoffs
                      set it to  1 for constant backoff
                      set it to >1 for exponential backoff
```
