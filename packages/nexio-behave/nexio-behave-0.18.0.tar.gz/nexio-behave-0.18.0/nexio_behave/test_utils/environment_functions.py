"""Functions for globally common environment actions used by before and after behave hooks

Keeping this file clean with only global functions is very important for dependency management.
We do not want to load dependencies in test environments that are not needed. Specific functions for
very specific actions should be kept somewhere else.
"""
from typing import Any, Callable

from behave.runner import Context
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


def setup_logging(ctx: Context) -> None:
    """Sets up logging for the behave logger using loguru

    Args:
        ctx: The behave context

    """
    pass


def initialize_context_variables(ctx: Context) -> None:
    """Initializes variables on the behave context

    Args:
        ctx: The behave context

    """
    # Start the framework with these variables set
    ctx.headers = {}


def reset_context_vars(ctx: Context) -> None:
    """Resets a few context vars that should be cleared

    Args:
        ctx: The behave context

    """
    logger.debug("Resetting context vars")
    ctx.headers = {}
    logger.debug("Context vars successfully reset")


def set_user_data(ctx: Context) -> None:
    """Retrieves behave user data from the behave.ini and saves it to the context

    Args:
        ctx: The behave context

    """
    logger.debug("Setting user data from the behave.ini or environment variables")
    user_data = ctx.config.userdata
    ctx.base_url = user_data.get("base_url", "http://localhost")
    ctx.environment = user_data.get("environment", "ci")
    logger.debug(f"User data from configs and environment variables: {user_data}")
