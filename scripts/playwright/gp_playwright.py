"""
Public launcher for GP register automation.

The protected implementation lives in gp_core.py. Release builds should ship the
PyArmor-obfuscated gp_core.py plus this lightweight launcher, not the cleartext
source core.
"""

from gp_core import main


if __name__ == "__main__":
    main()
