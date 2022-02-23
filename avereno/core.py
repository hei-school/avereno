import time
from datetime import timedelta
from typing import TypeVar, Callable


class GiveUpRetryError(Exception):
    pass


T = TypeVar("T")


def retry(
    unreliable_function: Callable[[], T],
    max_retries=5,
    max_sleep=timedelta(minutes=10),
    on_retry: Callable[[int, Exception], None] = (
        lambda current_nb_retries, current_error: None
    ),
    init_backoff=timedelta(seconds=1),
    backoff_multiplier=2,
    **kwargs
) -> T:
    """Try unreliable_function then retry it in case of failure.

    Optional Keyword Arguments:
        max_retries:        number of retries after which GiveUpRetryError will be raised
        max_sleep:          cumulated sleep (backoff) after which GiveUpRetryError will be raised
        on_retry:           function to invoke _before_ each retry
        init_backoff:       initial backoff that will potentially increase afterwards
        backoff_multiplier: multiplication factor between consecutive backoffs
                            set it to  1 for constant backoff
                            set it to >1 for exponential backoff
        **kwargs: any argument to send in the target function

    Returns:
        Result of unreliable_function if its invocations eventually succeed.
        Otherwise raise GiveUpRetryError with the last error set as its __cause__
    """
    _check_input_max_retries(max_retries)
    _check_input_backoff_multiplier(backoff_multiplier)
    nb_retries = 0
    backoff_in_seconds = init_backoff.total_seconds()
    while True:
        try:
            return unreliable_function(**kwargs)
        except Exception as e:
            nb_retries += 1
            _check_giveup_max_retries(max_retries, nb_retries, e)
            _check_giveup_max_sleep(
                max_sleep, nb_retries, e, init_backoff, backoff_multiplier
            )
            on_retry(nb_retries, e)
            time.sleep(backoff_in_seconds)
            backoff_in_seconds *= backoff_multiplier


def _check_input_max_retries(max_retries):
    if max_retries < 1:
        raise ValueError("Must satisfy: max_retries >= 1")


def _check_input_backoff_multiplier(backoff_multiplier):
    if backoff_multiplier < 1:
        raise NotImplementedError("reducing backoff over time")


def _check_giveup_max_retries(
    max_retries: int, nb_retries: int, current_error: Exception
):
    if nb_retries > max_retries:
        raise GiveUpRetryError(f"max_retries={max_retries} reached") from current_error


def _check_giveup_max_sleep(
    max_sleep: timedelta,
    nb_retries: int,
    current_error: Exception,
    init_backoff: timedelta,
    backoff_multiplier: timedelta,
):
    init_backoff_in_seconds = init_backoff.total_seconds()
    next_cumulated_sleep_in_seconds = (
        init_backoff_in_seconds * nb_retries
        if backoff_multiplier == 1
        else (init_backoff_in_seconds * backoff_multiplier ** nb_retries - 1)
    )
    if next_cumulated_sleep_in_seconds > max_sleep.total_seconds():
        message = f"will exceed max_sleep={max_sleep} if sleeping once more"
        raise GiveUpRetryError(message) from current_error
