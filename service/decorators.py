from .exceptions import BreakOutOfRetry
import functools
import time


def retry_on_exception(max_retries, fail_response=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts_left = max_retries

            while attempts_left > 0:
                try:
                    result = func(*args, **kwargs)
                    return result
                except BreakOutOfRetry:
                    return fail_response

                except:
                    attempts_left -= 1
                    time.sleep(1)

            return fail_response

        return wrapper

    return decorator
