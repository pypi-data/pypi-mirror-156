# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
from abc import ABC, abstractmethod

# Custom Library

# Custom Packages

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
class Output(ABC):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def json_not_found(self):
        pass

    @abstractmethod
    def wrong_format(self):
        pass