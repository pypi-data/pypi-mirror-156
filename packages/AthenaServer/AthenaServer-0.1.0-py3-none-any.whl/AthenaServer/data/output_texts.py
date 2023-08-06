# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
import json

# Custom Library

# Custom Packages

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
JSON_NOT_FOUND:bytes = json.dumps({"error": "No valid json structure found"}).encode("utf_8")
WRONG_FORMAT:bytes = json.dumps({"error": "Format of the json structure could not be mapped to a valid format"}).encode("utf_8")