"""
Manage the local License Key for GP register automation.

This plaintext helper only knows local key paths. License server access is
performed by the protected gp_core module.

Usage:
  python scripts/license_check.py setup <LicenseKey>
  python scripts/license_check.py path
  python scripts/license_check.py path --absolute
  python scripts/license_check.py show
  python scripts/license_check.py info
  python scripts/license_check.py clear
"""

import argparse
import io
import os
import sys

from gp_config import license_key_path, license_key_relative_path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYWRIGHT_DIR = os.path.join(SCRIPTS_DIR, "playwright")


def _mask_key(key: str) -> str:
    if len(key) <= 8:
        return "*" * len(key)
    return f"{key[:4]}{'*' * (len(key) - 8)}{key[-4:]}"


def read_key() -> str:
    path = license_key_path()
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def write_key(key: str):
    key = key.strip()
    if not key:
        raise ValueError("License Key cannot be empty")
    path = license_key_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(key + "\n")
    return path


def clear_key() -> bool:
    path = license_key_path()
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def license_info_from_core():
    if PLAYWRIGHT_DIR not in sys.path:
        sys.path.insert(0, PLAYWRIGHT_DIR)
    try:
        from gp_core import get_license_info
    except Exception as e:
        return {"ok": False, "error": f"Cannot load protected core: {e}"}
    return get_license_info()


def cmd_setup(args):
    path = write_key(args.key)
    print(f">>> License Key saved: {path}")
    print(f">>> Current Key: {_mask_key(args.key.strip())}")


def cmd_path(args):
    if getattr(args, "absolute", False):
        print(license_key_path())
    else:
        print(license_key_relative_path())


def cmd_show(args):
    key = read_key()
    if not key:
        print(">>> License Key is not set")
        print(f">>> Relative path: {license_key_relative_path()}")
        print(f">>> Absolute path: {license_key_path()}")
        return 1
    print(f">>> License Key: {_mask_key(key)}")
    print(f">>> Relative path: {license_key_relative_path()}")
    print(f">>> Absolute path: {license_key_path()}")
    return 0


def cmd_info(args):
    if not read_key():
        print(">>> License Key is not set")
        print(">>> Run: python scripts/license_check.py setup <YOUR_LICENSE_KEY>")
        return 1
    result = license_info_from_core()
    if not result.get("ok"):
        print(f">>> [License] {result.get('error')}")
        return 1
    print(f">>> [License] OK, remaining {result.get('remaining', '?')} calls")
    return 0


def cmd_clear(args):
    if clear_key():
        print(f">>> License Key removed: {license_key_relative_path()}")
    else:
        print(f">>> No local License Key found: {license_key_relative_path()}")


def main():
    parser = argparse.ArgumentParser(description="GP License Key manager")
    sub = parser.add_subparsers(dest="command", required=True)

    setup = sub.add_parser("setup", help="Save License Key")
    setup.add_argument("key", help="Your License Key")
    setup.set_defaults(func=cmd_setup)

    path_cmd = sub.add_parser("path", help="Show License Key path")
    path_cmd.add_argument("--absolute", action="store_true", help="Show resolved absolute path")
    path_cmd.set_defaults(func=cmd_path)

    show = sub.add_parser("show", help="Show masked saved key")
    show.set_defaults(func=cmd_show)

    info = sub.add_parser("info", help="Check remaining quota without deduction")
    info.set_defaults(func=cmd_info)

    clear = sub.add_parser("clear", help="Remove local License Key")
    clear.set_defaults(func=cmd_clear)

    args = parser.parse_args()
    code = args.func(args)
    if isinstance(code, int):
        sys.exit(code)


if __name__ == "__main__":
    main()
