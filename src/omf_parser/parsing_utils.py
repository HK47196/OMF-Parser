"""Low-level OMF parsing utilities."""

import struct


class ParsingMixin:
    """Mixin providing low-level parsing utilities for OMF records."""

    def read_byte(self):
        if self.offset >= len(self.data):
            return None
        b = self.data[self.offset]
        self.offset += 1
        return b

    def read_bytes(self, n):
        if n is None or self.offset + n > len(self.data):
            return None
        b = self.data[self.offset:self.offset + n]
        self.offset += n
        return b

    def peek_byte(self):
        if self.offset >= len(self.data):
            return None
        return self.data[self.offset]

    def bytes_remaining(self):
        return len(self.data) - self.offset

    def parse_index(self):
        """Parse OMF Index field (1 or 2 bytes). Spec Page 3."""
        b1 = self.read_byte()
        if b1 is None:
            return 0
        if b1 & 0x80:
            b2 = self.read_byte()
            if b2 is None:
                return 0
            return ((b1 & 0x7F) << 8) + b2
        return b1

    def parse_name(self):
        """Parse length-preceded string. Spec Page 3."""
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

    def parse_numeric(self, size_bytes):
        """Parse numeric value of specified size (1-4 bytes)."""
        raw = self.read_bytes(size_bytes)
        if not raw:
            return 0
        if size_bytes == 1:
            return raw[0]

        # Select endianness based on mode
        endian = '>' if self.is_big_endian else '<'

        if size_bytes == 2:
            return struct.unpack(f'{endian}H', raw)[0]
        if size_bytes == 3:
            # 3-byte values: add padding byte on correct side
            if self.is_big_endian:
                return struct.unpack('>I', b'\x00' + raw)[0]
            else:
                return struct.unpack('<I', raw + b'\x00')[0]
        if size_bytes == 4:
            return struct.unpack(f'{endian}I', raw)[0]
        return 0

    def parse_variable_length_int(self):
        """Parse variable-length numeric for COMDEF/TYPDEF. Spec Page 55."""
        b = self.read_byte()
        if b is None:
            return 0
        if b <= 0x80:
            return b
        if b == 0x81:
            return self.parse_numeric(2)
        if b == 0x84:
            return self.parse_numeric(3)
        if b == 0x88:
            return self.parse_numeric(4)
        return b

    def validate_checksum(self, record_data, checksum):
        """Validate record checksum. Spec Page 2."""
        if checksum == 0:
            return True, "Skipped (0)"
        total = sum(record_data) & 0xFF
        if total == 0:
            return True, "Valid"
        return False, f"Invalid (sum={total:02X})"
