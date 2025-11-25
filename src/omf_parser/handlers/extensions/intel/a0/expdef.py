"""Intel/TIS EXPDEF extension (A0 subtype 0x02)."""

from ... import VendorExtension
from . import VENDOR_NAME


class EXPDEFExtension(VendorExtension):
    """EXPDEF - Export Definition (A0 subtype 0x02).

    Specifies exported symbols to DLLs.
    """

    vendor_name = VENDOR_NAME
    extension_name = "EXPDEF (Export Definition)"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls != 0xA0 or sub.bytes_remaining() < 1:
            return False

        subtype = sub.peek_byte()
        if subtype != 0x02:
            return False

        sub.read_byte()  # Consume subtype

        parser.track_extension('a0_subtype', '0x02', self.vendor_name, self.extension_name)

        exported_name = sub.parse_name()
        internal_idx = sub.parse_index()

        print(f"      EXPDEF: '{exported_name}' Internal={parser.get_extdef(internal_idx)}")

        return True
