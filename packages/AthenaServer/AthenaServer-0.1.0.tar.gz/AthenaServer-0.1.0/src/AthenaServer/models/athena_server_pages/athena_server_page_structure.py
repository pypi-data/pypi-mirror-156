# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
from dataclasses import dataclass, field

# Custom Library

# Custom Packages
from AthenaServer.models.athena_server_pages.athena_server_page_logic import AthenaServerPageLogic
from AthenaServer.models.athena_server_pages.athena_server_page import AthenaServerPage

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
@dataclass(match_args=True, slots=True)
class AthenaServerStructure(AthenaServerPageLogic):
    root_page:AthenaServerPage=None

    # ------------------------------------------------------------------------------------------------------------------
    # - init -
    # ------------------------------------------------------------------------------------------------------------------
    def __post_init__(self):
        # the root_page is necessary because the structure needs a root to flatten from
        #   Else the pages defined with the manager will not be able to be flattened correctly
        if self.root_page is None:
            self.root_page = AthenaServerPage(name=self.name)
        # always check that the pages are inherited correctly
        elif not isinstance(self.root_page, AthenaServerPage):
            raise TypeError

    # ------------------------------------------------------------------------------------------------------------------
    # - Context Manager -
    # ------------------------------------------------------------------------------------------------------------------
    def __exit__(self, exc_type, exc_val, exc_tb):
        super(AthenaServerStructure, self).__exit__(exc_type, exc_val, exc_tb)
        self.structure[(self.root_page.name,)] = self.root_page # add the root page to itself

    # ------------------------------------------------------------------------------------------------------------------
    # - dunders -
    # ------------------------------------------------------------------------------------------------------------------
    def __getitem__(self, item:tuple):
        # done for ease of use
        return self.structure[item]
