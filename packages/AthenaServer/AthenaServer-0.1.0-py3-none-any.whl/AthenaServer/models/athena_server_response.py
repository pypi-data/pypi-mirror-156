# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
from dataclasses import dataclass
# Custom Library

# Custom Packages
import AthenaServer.data.return_codes as  return_codes

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
@dataclass(slots=True, match_args=True)
class AthenaServerResponse:
    code:return_codes.Information|return_codes.Success|return_codes.Redirection|return_codes.ErrorClient|return_codes.ErrorServer
    body:dict

    def to_dict(self):
        return {
            "code": self.code.value,
            "body": self.body
        }