"""Contains decorator functions for the Nexio Behave framework"""
from typing import Any, Callable

from nexio_behave.environment import after_feature, before_all


def export_function(func: Callable) -> Callable:
    """A helper decorator that when given a function will add it to the __all__ list.

    Args:
        func: The function to be added to the __all__ list.

    Returns:
        func: Returns the function passed in to be used

    """
    # mod = sys.modules[func.__module__]
    # if hasattr(mod, "__all__"):
    #     mod.__all__.append(func.__name__)
    # else:
    #     mod.__all__ = [func.__name__]
    # return func


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
