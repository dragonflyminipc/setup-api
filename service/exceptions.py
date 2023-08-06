# Special exception to break out of @retry_on_exception decorators
class BreakOutOfRetry(Exception):
    pass
