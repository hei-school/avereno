import pytest
from avereno import retry, GiveUpRetryError
from datetime import timedelta


class Counter:
    def __init__(self, value: int):
        self.value = value

    def add_one_then_fail(self) -> None:
        self.value += 1
        raise Exception(f"counter.value={self.value}")


class Message:
    def __init__(self, value: str):
        self.value = value

    def set_value(self, value: str) -> None:
        self.value = value


def test_retry_exp_with_nb_of_retries_as_limit():
    attempts = Counter(0)
    error_message = Message("")
    max_retries = 10

    with pytest.raises(GiveUpRetryError) as giveup_error:
        retry(
            lambda: attempts.add_one_then_fail(),
            max_retries=max_retries,
            on_retry=lambda current_nb_retries, current_error: error_message.set_value(
                f"Retries: {current_nb_retries} out of {max_retries}"
            ),
            init_backoff=timedelta(milliseconds=20),
            # backoff_multiplier=2,
        )

    assert attempts.value == 11  # 1 TRY + 10 RETRIES
    err_value = giveup_error.value
    assert str(err_value) == "max_retries=10 reached"
    assert error_message.value == "Retries: 10 out of 10"
    cause_error = err_value.__cause__
    assert isinstance(cause_error, Exception)
    assert cause_error.args[0] == "counter.value=11"


def test_retry_exp_with_max_sleep_as_limit():
    attempts = Counter(0)

    with pytest.raises(GiveUpRetryError) as giveup_error:
        retry(
            lambda: attempts.add_one_then_fail(),
            max_retries=1000,
            max_sleep=timedelta(seconds=10),
            # init_backoff=timedelta(seconds=1)
            # backoff_multiplier=2,
        )

    # TRY + 1sec...RETRY + 2sec...RETRY + 4sec...RETRY = only 4 attempts possible within 10s
    assert attempts.value == 4
    err_value = giveup_error.value
    assert str(err_value) == "will exceed max_sleep=0:00:10 if sleeping once more"
    cause_error = err_value.__cause__
    assert isinstance(cause_error, Exception)
    assert cause_error.args[0] == "counter.value=4"


def test_retry_const_with_max_sleep_as_limit():
    attempts = Counter(0)

    with pytest.raises(GiveUpRetryError):
        retry(
            lambda: attempts.add_one_then_fail(),
            max_retries=1000,
            max_sleep=timedelta(seconds=10),
            # init_backoff=timedelta(seconds=1)
            backoff_multiplier=1,
        )

    assert attempts.value == 11  # TRY + 10 RETRIES (1 RETRY per second)


def test_bad_max_retries():
    attempts = Counter(0)

    with pytest.raises(ValueError) as value_error:
        retry(lambda: attempts.add_one_then_fail(), max_retries=0)

    assert attempts.value == 0  # Not even a TRY
    assert str(value_error.value) == "Must satisfy: max_retries >= 1"
