"""CLI that packages and runs the nexio behave tests for other services.

This allows for an easy entry point
into running these tests without having to provide a ton of options. The CLI will add those
out of the box to the behave_main runner.

"""
import os
import shutil
from shutil import SameFileError

import click
from loguru import logger

# Global Variables
from nexio_behave.cli_nexio_behave.constants import (
    BEHAVE_INI_TEMPLATE,
    ENVIRONMENT_TEMPLATE,
    FEATURE_DIR,
    FEATURE_TEMPLATE,
    STEP_DIR,
    STEP_TEMPLATE,
    TEST_DIR,
)

# from click import Context
# from nexio_behave.cli_nexio_behave.config import BehaveConfig
# from nexio_behave.cli_nexio_behave.config import BehaveRunner


INIT_PACKAGE = "init"
INTEGRATION_TESTS = "tests_integration"
E2E_TESTS = "tests_e2e"
ENVIRONMENTS = ["ci", "dev", "functional", "prod"]
BROWSERS = ["chrome", "safari"]


@click.group()
def cli() -> None:
    """Lexio Behave CLI that has the ability to run behave tests in any Lexio stack."""
    logger.info("Welcome to the Nexio Behave CLI. We are glad you are here!")


@cli.command()
def init() -> None:
    """Initializes the Nexio Behave framework inside the new project"""
    logger.info("Initializing the Nexio Behave's default framework.")

    # Creating the root test dir
    try:
        os.mkdir(TEST_DIR)
        open(f"{TEST_DIR}/__init__.py", "w")
        logger.info(f"Directory: {TEST_DIR} Created")
    except FileExistsError:
        logger.info(f"Directory: {TEST_DIR} already exists. Nothing else is required.")

    # Creating the features dir
    try:
        os.mkdir(FEATURE_DIR)
        logger.info(f"Directory: {FEATURE_DIR} Created")
    except FileExistsError:
        logger.info(
            f"Directory: {FEATURE_DIR} already exists. Nothing else is required."
        )

    # Creating the steps dir
    try:
        os.mkdir(STEP_DIR)
        logger.info(f"Directory: {STEP_DIR} Created")
    except FileExistsError:
        logger.info(f"Directory: {STEP_DIR} already exists. Nothing else is required.")

    # Copying the default files from the framework over into the new package
    try:
        shutil.copyfile(ENVIRONMENT_TEMPLATE, f"{TEST_DIR}/environment.py")
    except SameFileError:
        logger.info(
            f"File: {ENVIRONMENT_TEMPLATE} already exists. Nothing else is required."
        )

    try:
        shutil.copyfile(BEHAVE_INI_TEMPLATE, f"{TEST_DIR}/behave.ini")
    except SameFileError:
        logger.info(
            f"File: {BEHAVE_INI_TEMPLATE} already exists. Nothing else is required."
        )

    try:
        shutil.copyfile(FEATURE_TEMPLATE, f"{FEATURE_DIR}/default_feature.feature")
    except SameFileError:
        logger.info(
            f"File: {FEATURE_TEMPLATE} already exists. Nothing else is required."
        )

    try:
        shutil.copyfile(STEP_TEMPLATE, f"{STEP_DIR}/import_steps.py")
    except SameFileError:
        logger.info(f"File: {STEP_TEMPLATE} already exists. Nothing else is required.")


if __name__ == "__main__":
    cli()


# @click.option(
#     "--environment",
#     type=click.Choice(ENVIRONMENTS),
#     default="dev",
#     help="The environment to run tests against.",
# )
# @click.option(
#     "--use-common-app/--no-use-common-app",
#     "common_app",
#     default=False,
#     help="Use common SalesForce app in tests.",
# )
# @click.option(
#     "--stack-name",
#     type=click.types.STRING,
#     default="functional-talos-application",
#     help="The stack name to run tests against.",
# )
# @click.option(
#     "--debug/--no-debug",
#     default=False,
#     help="Run the tests in debug mode. This turns on DEBUG logs.",
# )
# @click.option(
#     "--tags",
#     type=click.types.STRING,
#     help="The desired tags of tests to run. Space separated list IE: '@functional @config'",
# )
# @click.option(
#     "--file-pattern",
#     type=click.types.STRING,
#     help="The name or feature file pattern to run.",
# )
# @click.option(
#     "--files",
#     type=click.types.STRING,
#     help="A comma separated list of feature files to run",
# )
# @click.option(
#     "--test-report-dir",
#     type=click.types.STRING,
#     help="The directory override to where the behave test reports are saved.",
# )
# @cli.command()
# @click.pass_context
# def tests_integration(
#     ctx: Context,
#     environment: str,
#     common_app: bool,
#     stack_name: str,
#     debug: bool,
#     tags: str,
#     file_pattern: str,
#     files: str,
#     test_report_dir: str,
# ) -> None:
#     """Run behave integration tests"""
#     logger.info("Starting Behave Integration tests.")
#     behave_config = BehaveConfig(
#         "behave_integration",
#         environment,
#         common_app,
#         stack_name,
#         debug,
#         tags=tags,
#         file_pattern=file_pattern,
#         files=files,
#         test_report_dir=test_report_dir,
#     )
#     BehaveRunner.run_behave(INTEGRATION_TESTS, behave_config.to_args())
#
#
# @click.option(
#     "--environment",
#     type=click.Choice(ENVIRONMENTS),
#     default="dev",
#     help="The environment to run tests against.",
# )
# @click.option(
#     "--use-common-app/--no-use-common-app",
#     "common_app",
#     default=False,
#     help="Use common SalesForce app in tests.",
# )
# @click.option(
#     "--stack-name",
#     type=click.types.STRING,
#     default="functional-talos-application",
#     help="The stack name to run tests against",
# )
# @click.option(
#     "--debug/--no-debug",
#     default=False,
#     help="Run the tests in debug mode. This turns on DEBUG logs.",
# )
# @click.option(
#     "--tags",
#     type=click.types.STRING,
#     help="The desired tags of tests to run. Space separated list IE: '@functional @config'",
# )
# @click.option(
#     "--browser",
#     type=click.Choice(BROWSERS),
#     default="chrome",
#     help="The desired browser to run the tests against.",
# )
# @click.option(
#     "--max-attempts",
#     type=click.types.INT,
#     default=3,
#     help="The max number of retry attempts oer scenario if a scenario fails.",
# )
# @click.option(
#     "--default-timeout",
#     type=click.types.INT,
#     default=25,
#     help="Default selenium wait timeout in seconds.",
# )
# @click.option(
#     "--latency", type=click.types.INT, default=0, help="The browser latency in seconds."
# )
# @click.option(
#     "--file-pattern",
#     type=click.types.STRING,
#     help="The name or feature file pattern to run.",
# )
# @click.option(
#     "--files",
#     type=click.types.STRING,
#     help="A comma separated list of feature files to run",
# )
# @click.option(
#     "--test-report-dir",
#     type=click.types.STRING,
#     help="The directory override to where the behave test reports are saved.",
# )
# @cli.command()
# @click.pass_context
# def tests_e2e(
#     ctx: Context,
#     environment: str,
#     common_app: bool,
#     stack_name: str,
#     debug: bool,
#     tags: str,
#     browser: str,
#     max_attempts: int,
#     default_timeout: int,
#     latency: int,
#     file_pattern: str,
#     files: str,
#     test_report_dir: str,
# ) -> None:
#     """Run behave E2E tests"""
#     logger.info("Starting Behave E2E tests.")
#     behave_config = BehaveConfig(
#         "behave_e2e",
#         environment,
#         common_app,
#         stack_name,
#         debug,
#         tags=tags,
#         browser=browser,
#         max_attempts=max_attempts,
#         default_timeout=default_timeout,
#         latency=latency,
#         file_pattern=file_pattern,
#         files=files,
#         test_report_dir=test_report_dir,
#     )
#     BehaveRunner.run_behave(E2E_TESTS, behave_config.to_args())
