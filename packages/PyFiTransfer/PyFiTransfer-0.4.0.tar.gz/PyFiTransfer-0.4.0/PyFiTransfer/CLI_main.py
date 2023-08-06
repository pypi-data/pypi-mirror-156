#!/usr/bin/env python3

import sys
from os import chdir
from os.path import dirname

sys.path.insert(0, dirname(
    dirname(__file__)))  # Ensure main module can be found by Python.

# > Set CWD:
chdir(dirname(__file__))

from PyFiTransfer.appevents.CLI_loop import CLI_loop
from PyFiTransfer.appevents.events import logger


def CLI_main() -> None:
    """CLI entry point.

    ---

    :return: start CLI program.
    :rtype: None
    """

    logger.info("PyFiTransfer-CLI Started...\n")
    return CLI_loop()


if __name__ == "__main__":
    CLI_main()
