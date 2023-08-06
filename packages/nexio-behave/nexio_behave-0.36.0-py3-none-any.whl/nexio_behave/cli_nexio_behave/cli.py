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
    FEATURE_TEMPLATE,
    STEP_TEMPLATE,
    TEST_DIR,
)

# from click import Context
# from nexio_behave.cli_nexio_behave.config import BehaveConfig
# from nexio_behave.cli_nexio_behave.config import BehaveRunner


INIT_PACKAGE = "init"
TEST_TYPE = ["integration", "e2e"]
INTEGRATION_TESTS = "tests_integration"
E2E_TESTS = "tests_e2e"
ENVIRONMENTS = ["ci", "dev", "functional", "prod"]
BROWSERS = ["chrome", "safari"]


@click.group()
def cli() -> None:
    """Lexio Behave CLI that has the ability to run behave tests in any Lexio stack."""
    logger.info("Welcome to the Nexio Behave CLI. We are glad you are here!")


@click.option(
    "--test-type",
    type=click.Choice(TEST_TYPE),
    default="integration",
    help="The type of test suite to initialize.",
)
@cli.command()
def init(test_type: str) -> None:
    """Initializes the Nexio Behave framework inside the new project"""
    logger.info("Initializing the Nexio Behave's default framework.")

    # Creating the root test directory and copying over root files
    try:
        os.mkdir(TEST_DIR)
        open(f"{TEST_DIR}/__init__.py", "w")
        logger.info(f"Directory: {TEST_DIR} Created")
        shutil.copyfile(ENVIRONMENT_TEMPLATE, f"{TEST_DIR}/environment.py")
        shutil.copyfile(BEHAVE_INI_TEMPLATE, f"{TEST_DIR}/behave.ini")
    except FileExistsError:
        pass
    except SameFileError:
        pass

    # Creating the integration test directory and copying over files
    if test_type == "integration":
        os.mkdir(f"{TEST_DIR}/tests_integration")
        int_features = f"{TEST_DIR}/tests_integration/features"
        int_steps = f"{TEST_DIR}/tests_integration/steps"
        try:
            os.mkdir(int_features)
            os.mkdir(int_steps)
            shutil.copyfile(FEATURE_TEMPLATE, f"{int_features}/default_feature.feature")
            shutil.copyfile(STEP_TEMPLATE, f"{int_steps}/import_steps.py")
        except FileExistsError:
            pass
        except SameFileError:
            pass

    # Creating the e2e test directory and copying over files
    if test_type == "e2e":
        os.mkdir(f"{TEST_DIR}/tests_e2e")
        e2e_features = f"{TEST_DIR}/tests_e2e/features"
        e2e_steps = f"{TEST_DIR}/tests_e2e/steps"
        try:
            os.mkdir(e2e_features)
            os.mkdir(e2e_steps)
            shutil.copyfile(FEATURE_TEMPLATE, f"{e2e_features}/default_feature.feature")
            shutil.copyfile(STEP_TEMPLATE, f"{e2e_steps}/import_steps.py")
        except FileExistsError:
            pass
        except SameFileError:
            pass


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
