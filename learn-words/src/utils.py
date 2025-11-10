import time
import functools
import logging

logger = logging.getLogger(__name__)


def async_timer(func):
    """A decorator that logs the execution time of an ASYNC function."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):  # 1. Make the wrapper async
        # Record the start time
        start_time = time.perf_counter()

        # Await the original async function and store its result
        result = await func(*args, **kwargs)  # 2. Await the function call

        # Record the end time
        end_time = time.perf_counter()

        # Calculate the elapsed time
        elapsed_time = end_time - start_time

        # Log the result
        logger.info(f"Async function '{func.__name__}' took {elapsed_time:.4f} seconds to execute.")

        # Return the original function's result
        return result

    return wrapper
