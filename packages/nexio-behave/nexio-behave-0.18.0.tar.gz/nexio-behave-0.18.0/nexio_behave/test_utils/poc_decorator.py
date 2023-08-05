"""Contains functions for the nexio-behave POC"""
from typing import Any, Callable

from loguru import logger


def poc_setup_env(func: Callable) -> Callable:
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
        func(*args)

    return wrapper
