"""Behave framework environment configuration. This file holds all hooks and environment setup."""
from behave.model import Feature, Scenario, Step, Tag
from behave.runner import Context

from nexio_behave.test_utils.default_env_decorators import (
    default_after_feature,
    default_before_all,
)


@default_before_all
def before_all(ctx: Context) -> None:
    """Hook that runs before all features

    Args:
        ctx: The behave context

    """
    pass


def before_tag(ctx: Context, tag: Tag) -> None:
    """Hook that runs before a specific tag

    Args:
        ctx: The behave context
        tag: Behave tag

    """
    pass


def before_feature(ctx: Context, feature: Feature) -> None:
    """Hook that runs before every feature

    Args:
        ctx: The behave context
        feature: The behave feature

    """
    pass


def before_scenario(ctx: Context, scenario: Scenario) -> None:
    """Hook that runs before every scenario

    Args:
        ctx: The behave context
        scenario: The behave scenario

    """
    pass


def before_step(ctx: Context, step: Step) -> None:
    """Hook that runs before every step

    Args:
        ctx: The behave context
        step: The behave step

    """
    pass


def after_all(ctx: Context) -> None:
    """Hook that runs after all features

    Args:
        ctx: The behave context

    """
    pass


def after_tag(ctx: Context, tag: Tag) -> None:
    """Hook that runs after a specific tag

    Args:
        ctx: The behave context
        tag: the behave tag

    """
    pass


@default_after_feature
def after_feature(ctx: Context, feature: Feature) -> None:
    """Hook that runs after every feature

    Args:
        ctx: The behave context
        feature: The behave feature

    """


def after_scenario(ctx: Context, scenario: Scenario) -> None:
    """Hook that runs after every scenario

    Args:
        ctx: The behave context
        scenario: The behave scenario

    """
    pass


def after_step(ctx: Context, step: Step) -> None:
    """Hook that runs after every step

    Args:
        ctx: The behave context
        step: The behave step

    """
    pass
