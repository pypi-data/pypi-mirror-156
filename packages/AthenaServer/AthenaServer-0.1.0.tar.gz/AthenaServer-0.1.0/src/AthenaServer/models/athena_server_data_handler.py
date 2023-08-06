# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Callable

# Custom Library

# Custom Packages
from AthenaServer.models.athena_server_pages import AthenaServerStructure, AthenaServerPage
from AthenaServer.models.athena_server_response import AthenaServerResponse

import AthenaServer.data.return_codes as return_codes

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
@dataclass(slots=True, kw_only=True)
class AthenaServerDataHandler:
    pages_structure: AthenaServerStructure

    # ------------------------------------------------------------------------------------------------------------------
    # - factory, needed for asyncio.AbstractEventLoop.create_connection protocol_factory kwarg used in Launcher -
    # ------------------------------------------------------------------------------------------------------------------
    async def handle(self, data: bytearray) -> AthenaServerResponse:
        match data.decode("utf_8").split(" ", 2):
            case "GET", str(pages), str(json_args):
                callback = lambda page, json_dict: page.GET(**json_dict)
                return await self.handle_data(pages, json_args, callback)

            case "PUT", str(pages), str(json_args):
                callback = lambda page, json_dict: page.PUT(**json_dict)
                return await self.handle_data(pages, json_args, callback)

            case "PATCH", str(pages), str(json_args):
                callback = lambda page, json_dict: page.PATCH(**json_dict)
                return await self.handle_data(pages, json_args, callback)

            case "POST", str(pages), str(json_args):
                callback = lambda page, json_dict: page.POST(**json_dict)
                return await self.handle_data(pages, json_args, callback)

            case "DELETE", str(pages), str(json_args):
                callback = lambda page, json_dict: page.DELETE(**json_dict)
                return await self.handle_data(pages, json_args, callback)

            case "OPTIONS", str(pages), str(json_args):
                callback = lambda page, json_dict: page.OPTIONS(**json_dict)
                return await self.handle_data(pages, json_args, callback)

            case "HEAD", str(pages), str(json_args):
                callback = lambda page, json_dict: page.HEAD(**json_dict)
                return await self.handle_data(pages, json_args, callback)

            case _:
                return AthenaServerResponse(code=return_codes.ErrorClient.NotFound, body={})



    def find_page(self, pages:str) -> AthenaServerPage:
        return self.pages_structure[tuple(pages.split("/"))]

    async def handle_data(self, pages:str, json_args:str, callback:Callable):
        try:
            page: AthenaServerPage = self.find_page(pages)
        except KeyError:
            return AthenaServerResponse(code=return_codes.ErrorClient.NotFound, body={})
        try:
            json_dict = json.loads(json_args)
        except json.JSONDecodeError:
            return AthenaServerResponse(code=return_codes.ErrorClient.BadRequest, body={})
        try:
            return AthenaServerResponse(
                code=return_codes.Success.Ok,
                body=await callback(page, json_dict)
            )
        except TypeError:
            return AthenaServerResponse(code=return_codes.ErrorClient.NotAcceptable, body={})

