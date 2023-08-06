# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
from enum import Enum

# Custom Library

# Custom Packages

# ----------------------------------------------------------------------------------------------------------------------
# - All -
# ----------------------------------------------------------------------------------------------------------------------
__all__ = [
    "Information", "Success", "Redirection", "ErrorClient", "ErrorServer"
]

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
class Information(Enum):
    Continue = 100
    SwitchProtocol = 101
    Processing = 102

class Success(Enum):
    Ok = 200
    Created = 201
    Accepted = 202
    NonAuthoritativeInformation = 203 #wtf does this mean?
    NoContent = 204
    ResetContent = 205
    PartialContent = 206
    MultiStatus = 207
    AlreadyReported = 208 # wtf is this

class Redirection(Enum):
    MultipleChoice = 300
    MovedPermanently = 301
    Found = 302
    SeeOther = 303
    TemporaryRedirect = 307
    PermanentRedirect = 308

class ErrorClient(Enum):
    BadRequest = 400
    Unauthorized = 401
    PaymentRequired = 402 # this won't even be used anywhere
    Forbidden = 403
    NotFound = 404
    MethodNotAllowed = 405
    NotAcceptable = 406
    ProxyAuthenticationRequired = 407
    RequestTimeout = 408
    Conflict = 409
    Gone = 410
    LengthRequired = 411
    PreconditionFailed = 412
    RequestEntityTooLarge = 413
    RequestURITooLong = 414
    UnsupportedMediaType = 415
    RequestedRangeNotSatisfiable = 416
    ExpectationFailed = 417
    UpgradeRequired = 426
    PreconditionRequired = 428
    TooManyRequests = 429 # use this for rate limiting
    RequestHeaderFieldTooLarge = 431
    UnavailableForLegalReasons = 451

class ErrorServer(Enum):
    InternalError = 500
    NotImplemented = 501
    BadGateway = 502
    ServiceUnavailable = 503
    GatewayTimeout = 504
    VersionNotSupported = 505
    InsufficientStorage = 507
    LoopDetected = 508
    NotExtended = 510
    NetworkAuthenticationRequired = 511

