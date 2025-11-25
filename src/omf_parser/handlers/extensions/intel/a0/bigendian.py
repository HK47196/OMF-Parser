"""Intel/TIS Big-endian extension (A0 subtype 0x06)."""

from ... import VendorExtension
from . import VENDOR_NAME


class BigEndianExtension(VendorExtension):
    """Big-endian (A0 subtype 0x06).

    Indicates big-endian byte order.
    """

    vendor_name = VENDOR_NAME
    extension_name = "Big-endian"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls != 0xA0 or sub.bytes_remaining() < 1:
            return False

        subtype = sub.peek_byte()
        if subtype != 0x06:
            return False

        sub.read_byte()  # Consume subtype

        parser.track_extension('a0_subtype', '0x06', self.vendor_name, self.extension_name)

        print(f"      Big-endian byte order")
        parser.is_big_endian = True

        return True
