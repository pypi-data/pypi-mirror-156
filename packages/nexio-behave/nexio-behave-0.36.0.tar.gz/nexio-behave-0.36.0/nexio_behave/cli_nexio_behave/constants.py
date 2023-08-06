"""Constants and environment variables used for the behave CLI"""
import os
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[1]
WORKING_ROOT = os.getcwd()
TEST_DIR = f"{WORKING_ROOT}/behave_tests"
FEATURE_TEMPLATE = f"{PACKAGE_ROOT}/default_templates/default_feature.feature"
STEP_TEMPLATE = f"{PACKAGE_ROOT}/default_templates/import_steps.py"
ENVIRONMENT_TEMPLATE = f"{PACKAGE_ROOT}/default_templates/environment.py"
BEHAVE_INI_TEMPLATE = f"{PACKAGE_ROOT}/default_templates/behave.ini"
