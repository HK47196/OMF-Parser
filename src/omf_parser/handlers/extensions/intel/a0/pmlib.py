"""Intel/TIS Protected Memory Library extension (A0 subtype 0x04)."""

from ... import VendorExtension
from . import VENDOR_NAME


class ProtectedMemoryLibraryExtension(VendorExtension):
    """Protected Memory Library (A0 subtype 0x04).

    Indicates protected memory library.
    """

    vendor_name = VENDOR_NAME
    extension_name = "Protected Memory Library"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls != 0xA0 or sub.bytes_remaining() < 1:
            return False

        subtype = sub.peek_byte()
        if subtype != 0x04:
            return False

        sub.read_byte()  # Consume subtype

        parser.track_extension('a0_subtype', '0x04', self.vendor_name, self.extension_name)

        print(f"      Protected memory library")

        return True
