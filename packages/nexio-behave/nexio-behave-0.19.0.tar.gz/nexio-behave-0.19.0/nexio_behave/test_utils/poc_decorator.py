"""Contains functions for the nexio-behave POC"""
from typing import Any, Callable

from loguru import logger

from nexio_behave.environment import before_all


def default_before_all(func: Callable) -> Callable:
    """Decorator for the POC for overriding environment file

    Args:
        func: The function to be called to be run through the wrapper

    """

    def wrapper(*args: Any) -> None:
        """Will print the line below when called

        Args:
            args: Anything

        """
        logger.debug("Running before the function inside decorator")
        before_all(*args)  # Will run the frameworks defaulted 'before_all' first
        func(
            *args
        )  # Will then run the new services 'before_all' second. Which will overwrite any defaults if set.

    return wrapper
