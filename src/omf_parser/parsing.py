"""Low-level OMF parsing utilities."""

import struct
from typing import TYPE_CHECKING

from .constants import IndexFlags, VarlenMarkers, AsciiRange

if TYPE_CHECKING:
    from .variant import Variant


class RecordParser:
    """Parser for reading structured data from a record's content bytes.

    Provides methods for reading OMF's various field types:
    - Bytes, words, dwords
    - Variable-length indexes
    - Length-preceded strings
    - Variable-length integers (COMDEF style)
    """

    def __init__(self, data: bytes, variant: 'Variant | None' = None, big_endian: bool = False) -> None:
        from .variant import TIS_STANDARD
        self.data = data
        self.offset = 0
        self.variant = variant or TIS_STANDARD
        self.big_endian = big_endian

    def read_byte(self) -> int | None:
        if self.offset >= len(self.data):
            return None
        b = self.data[self.offset]
        self.offset += 1
        return b

    def read_bytes(self, n: int | None) -> bytes | None:
        if n is None or self.offset + n > len(self.data):
            return None
        b = self.data[self.offset:self.offset + n]
        self.offset += n
        return b

    def peek_byte(self) -> int | None:
        if self.offset >= len(self.data):
            return None
        return self.data[self.offset]

    def bytes_remaining(self) -> int:
        return len(self.data) - self.offset

    def at_end(self) -> bool:
        return self.offset >= len(self.data)

    def parse_index(self) -> int:
        """Parse OMF Index field (1 or 2 bytes)."""
        b1 = self.read_byte()
        if b1 is None:
            return 0
        if b1 & IndexFlags.TWO_BYTE_FLAG:
            b2 = self.read_byte()
            if b2 is None:
                return 0
            return ((b1 & IndexFlags.HIGH_MASK) << 8) + b2
        return b1

    def parse_name(self) -> str:
        """Parse length-preceded string."""
        length = self.read_byte()
        if length is None or length == 0:
            return ""
        raw = self.read_bytes(length)
        if not raw:
            return ""
        try:
            return raw.decode('ascii', errors='replace')
        except Exception:
            return raw.hex()

    def parse_numeric(self, size_bytes: int) -> int:
        """Parse numeric value of specified size (1-4 bytes)."""
        raw = self.read_bytes(size_bytes)
        if not raw:
            return 0
        if size_bytes == 1:
            return raw[0]

        endian = '>' if self.big_endian else '<'

        if size_bytes == 2:
            result: int = struct.unpack(f'{endian}H', raw)[0]
            return result
        if size_bytes == 3:
            if self.big_endian:
                result = struct.unpack('>I', b'\x00' + raw)[0]
            else:
                result = struct.unpack('<I', raw + b'\x00')[0]
            return result
        if size_bytes == 4:
            result = struct.unpack(f'{endian}I', raw)[0]
            return result
        return 0

    def get_offset_field_size(self, is_32bit: bool) -> int:
        """Determine size for offset/displacement/length fields.

        Delegates to variant for proper sizing.
        """
        return self.variant.offset_field_size(is_32bit)

    def get_lidata_repeat_count_size(self, is_32bit: bool) -> int:
        """Determine size for LIDATA repeat count fields.

        Delegates to variant for proper sizing.
        """
        return self.variant.lidata_repeat_count_size(is_32bit)

    def parse_variable_length_int(self) -> int:
        """Parse variable-length numeric for COMDEF/TYPDEF."""
        b = self.read_byte()
        if b is None:
            return 0
        if b <= VarlenMarkers.MAX_1BYTE:
            return b
        if b == VarlenMarkers.MARKER_2BYTE:
            return self.parse_numeric(2)
        if b == VarlenMarkers.MARKER_3BYTE:
            return self.parse_numeric(3)
        if b == VarlenMarkers.MARKER_4BYTE:
            return self.parse_numeric(4)
        return b


def format_hex(data: bytes) -> str:
    """Format bytes as uppercase hex string."""
    return data.hex().upper() if data else ""


def format_hex_with_ascii(data: bytes) -> str:
    """Format bytes as hex with ASCII representation."""
    if not data:
        return ""
    hex_str = data.hex().upper()
    ascii_str = ''.join(
        chr(b) if AsciiRange.PRINTABLE_MIN <= b < AsciiRange.PRINTABLE_MAX else '.'
        for b in data
    )
    return f"{hex_str} (\"{ascii_str}\")"
