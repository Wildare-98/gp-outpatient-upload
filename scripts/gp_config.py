"""
Public local configuration for GP register automation.

This file is intentionally readable. It only exposes local package-relative
paths. Server endpoints live inside the protected core module.
"""

import os

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_ROOT = os.path.dirname(SCRIPTS_DIR)
LICENSE_KEY_RELATIVE = os.path.join("scripts", ".license_key")
LICENSE_KEY_FILE = os.path.join(PACKAGE_ROOT, LICENSE_KEY_RELATIVE)


def license_key_relative_path() -> str:
    return LICENSE_KEY_RELATIVE


def license_key_path() -> str:
    return os.path.normpath(LICENSE_KEY_FILE)
