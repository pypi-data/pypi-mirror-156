"""Contains decorator functions for the Nexio-Behave"""
from typing import Any, Callable

from nexio_behave.environment import after_feature, before_all


def default_before_all(func: Callable) -> Callable:
    """Decorator for 'before_all' functions, will call the frameworks 'before_all'.

    Args:
        func: The function to be called to be run through the wrapper

    """

    def wrapper(*args: Any) -> None:
        """The wrapper for the default_before_all decorator.

        Args:
            args: Any input

        """
        before_all(*args)  # Will run the frameworks defaulted 'before_all' first
        func(
            *args
        )  # Will then run the new services 'before_all' second. Which will overwrite any defaults

    return wrapper


def default_after_feature(func: Callable) -> Callable:
    """Decorator for 'after_feature' functions, will call the frameworks 'after_feature'.

    Args:
        func: The function to be called to be run through the wrapper.

    """

    def wrapper(*args: Any) -> None:
        """The wrapper for the default_after_feature decorator.

        Args:
            args: Any input

        """
        after_feature(*args)  # Will run the frameworks defaulted 'after_feature' first
        func(
            *args
        )  # Will then run the new services 'after_feature' second. Which will overwrite any defaults

    return wrapper
