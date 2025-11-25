"""Intel/TIS IMPDEF extension (A0 subtype 0x01)."""

from ... import VendorExtension
from . import VENDOR_NAME


class IMPDEFExtension(VendorExtension):
    """IMPDEF - Import Definition (A0 subtype 0x01).

    Specifies imported symbols from DLLs.
    """

    vendor_name = VENDOR_NAME
    extension_name = "IMPDEF (Import Definition)"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls != 0xA0 or sub.bytes_remaining() < 1:
            return False

        subtype = sub.peek_byte()
        if subtype != 0x01:
            return False

        sub.read_byte()  # Consume subtype

        parser.track_extension('a0_subtype', '0x01', self.vendor_name, self.extension_name)

        internal_idx = sub.parse_index()
        module_name = sub.parse_name()
        import_name = sub.parse_name()

        print(f"      IMPDEF: Internal={parser.get_extdef(internal_idx)} "
              f"Module='{module_name}' Import='{import_name}'")

        return True
