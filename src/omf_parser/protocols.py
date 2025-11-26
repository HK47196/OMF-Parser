"""Protocol definitions for breaking circular imports."""

from typing import Protocol

from .parsing import RecordParser
from .scanner import RecordInfo
from .variant import Variant


class OMFFileProtocol(Protocol):
    """Protocol defining the interface that record handlers need from OMFFile.

    This allows handlers to be typed without importing OMFFile directly,
    breaking the circular import between file.py and records/.
    """

    data: bytes | None
    variant: Variant
    features: set[str]

    lnames: list[str]
    segdefs: list[str]
    grpdefs: list[str]
    extdefs: list[str]
    typdefs: list[str]

    last_data_record: tuple[str, int, int] | None

    lib_page_size: int
    lib_dict_offset: int
    lib_dict_blocks: int

    def make_parser(self, record: RecordInfo) -> RecordParser: ...
    def get_lname(self, index: int | None) -> str: ...
    def get_segdef(self, index: int | None) -> str: ...
    def get_grpdef(self, index: int | None) -> str: ...
    def get_extdef(self, index: int) -> str: ...
    def get_typdef(self, index: int) -> str: ...
