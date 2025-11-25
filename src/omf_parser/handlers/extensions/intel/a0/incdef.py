"""Intel/TIS INCDEF extension (A0 subtype 0x03)."""

from ... import VendorExtension
from . import VENDOR_NAME


class INCDEFExtension(VendorExtension):
    """INCDEF - Incremental Compilation (A0 subtype 0x03).

    Incremental compilation information.
    """

    vendor_name = VENDOR_NAME
    extension_name = "INCDEF (Incremental Compilation)"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls != 0xA0 or sub.bytes_remaining() < 1:
            return False

        subtype = sub.peek_byte()
        if subtype != 0x03:
            return False

        sub.read_byte()  # Consume subtype

        parser.track_extension('a0_subtype', '0x03', self.vendor_name, self.extension_name)

        if sub.bytes_remaining() > 0:
            data = sub.read_bytes(sub.bytes_remaining())
            print(f"      INCDEF data: {data.hex().upper()}")

        return True
