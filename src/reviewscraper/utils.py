import logging
from functools import wraps
import time

def setup_logger(name: str) -> logging.Logger:
    fmt = "[%(asctime)s] %(levelname)s:%(name)s: %(message)s"
    logging.basicConfig(format=fmt, level=logging.INFO)
    return logging.getLogger(name)

def retry(exc_types: tuple, tries: int = 3, delay: float = 1.0):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for i in range(tries):
                try:
                    return fn(*args, **kwargs)
                except exc_types as e:
                    logging.warning(f"Retry {i+1}/{tries} after {e}")
                    time.sleep(delay)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
