import functools
import traceback
from typing import Any

def catch_exception(log_to: str = "errors.log", 
        return_value: Any=None):
    """Decorator to silently catch, log exceptions, and return a default value.

    Args:
        log_to (str, optional): File path to log errors.
        return_value (any, optional): Value to return in case of an exception.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_log = f"Exception in {func.__name__}(): {str(e)}\n{traceback.format_exc()}\n"
                
                if log_to:
                    with open(log_to, "a") as f:
                        f.write(error_log)
                return return_value
        return wrapper
    return decorator