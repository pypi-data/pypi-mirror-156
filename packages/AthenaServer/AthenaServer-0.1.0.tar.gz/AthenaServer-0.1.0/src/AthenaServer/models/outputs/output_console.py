# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
import asyncio

# Custom Library

# Custom Packages
from AthenaServer.models.outputs.output import Output

from AthenaServer.data.output_texts import JSON_NOT_FOUND, WRONG_FORMAT

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
class OutputConsole(Output):
    def json_not_found(self):
        print(JSON_NOT_FOUND)

    def wrong_format(self):
        print(WRONG_FORMAT)