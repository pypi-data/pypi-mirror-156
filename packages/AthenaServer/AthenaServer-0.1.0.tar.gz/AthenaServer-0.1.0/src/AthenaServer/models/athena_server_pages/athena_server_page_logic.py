# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
from dataclasses import dataclass, field

# Custom Library

# Custom Packages

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
@dataclass(match_args=True, slots=True)
class AthenaServerPageLogic:
    name:str
    structure: dict[str:AthenaServerPageLogic]=field(default_factory=dict)

    #non init
    manager:AthenaServerPageLogicManager=field(init=False, repr=False)

    # ------------------------------------------------------------------------------------------------------------------
    # - Context Manager -
    # ------------------------------------------------------------------------------------------------------------------
    def __enter__(self) -> AthenaServerPageLogicManager:
        self.manager = AthenaServerPageLogicManager(parent_name=self.name)
        return self.manager

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.structure = self.manager.pages
        del self.manager # this way it doesn't get tampered with after context manager has done it's job

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
@dataclass(slots=True)
class AthenaServerPageLogicManager:
    parent_name:str
    pages: dict[tuple:AthenaServerPageLogic]=field(default_factory=dict)

    def add_page(self, page:AthenaServerPageLogic) -> AthenaServerPageLogicManager:
        # if there are child structures present, we need to flatten them
        #   This makes the job of the server's data handler a lot easier,
        #   because a single tuple is easier to find as a key in a dictionary
        for child_tuple, child_obj in page.structure.items():
            self.pages[(self.parent_name, *child_tuple)] = child_obj

        # If the page is already allocated, throw an error
        #   as there cannot be multiple behaviors for the same objects
        if (page_tuple := (self.parent_name, page.name)) in self.pages:
            raise ValueError
        self.pages[page_tuple] = page
        return self # done for easy chaining of commands