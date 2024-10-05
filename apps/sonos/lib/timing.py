import logging
import time
from contextlib import contextmanager


@contextmanager
def timing(msg:str, log_level: str=logging.INFO):
    """Log the time taken to execute some context."""
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        logging.log( log_level, f"Elapsed time for {msg}: {elapsed_time:.4f} seconds" )
