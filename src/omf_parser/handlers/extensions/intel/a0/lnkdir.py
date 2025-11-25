"""Intel/TIS LNKDIR extension (A0 subtype 0x05)."""

from ... import VendorExtension
from . import VENDOR_NAME


class LNKDIRExtension(VendorExtension):
    """LNKDIR - Linker Directive (A0 subtype 0x05).

    Linker directives.
    """

    vendor_name = VENDOR_NAME
    extension_name = "LNKDIR (Linker Directive)"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls != 0xA0 or sub.bytes_remaining() < 1:
            return False

        subtype = sub.peek_byte()
        if subtype != 0x05:
            return False

        sub.read_byte()  # Consume subtype

        parser.track_extension('a0_subtype', '0x05', self.vendor_name, self.extension_name)

        if sub.bytes_remaining() > 0:
            directive = sub.read_bytes(sub.bytes_remaining())
            try:
                directive_text = directive.decode('ascii', errors='replace')
                print(f"      Directive: {directive_text}")
            except:
                print(f"      Directive: {directive.hex().upper()}")

        return True
