"""Constants and environment variables used for the behave CLI"""
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[1]
TEST_DIR = f"{PACKAGE_ROOT}/behave_tests"
FEATURE_DIR = f"{PACKAGE_ROOT}/behave_tests/features"
STEP_DIR = f"{PACKAGE_ROOT}/behave_tests/steps"
FEATURE_TEMPLATE = f"{PACKAGE_ROOT}/default_templates/default_feature.feature"
STEP_TEMPLATE = f"{PACKAGE_ROOT}/default_templates/import_steps.py"
ENVIRONMENT_TEMPLATE = f"{PACKAGE_ROOT}/default_templates/environment.py"
BEHAVE_INI_TEMPLATE = f"{PACKAGE_ROOT}/default_templates/behave.ini"
