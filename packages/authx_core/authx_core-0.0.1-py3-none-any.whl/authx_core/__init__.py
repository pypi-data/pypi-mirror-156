"""Utilities to help reduce boilerplate and reuse common functionality, Based to Support Building of Authx & Authx-lite"""

__version__ = "0.0.1"

from authx_core.engine import authxDB
from authx_core.guid import GUID, postgresql

__all__ = [
    "GUID",
    "postgresql",
    "authxDB",
]
