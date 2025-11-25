"""Intel NOPAD extension (0xA7)."""

from .. import VendorExtension
from . import VENDOR_NAME


class NOPADExtension(VendorExtension):
    """NOPAD (COMENT class 0xA7).

    Requests no segment padding.
    """

    vendor_name = VENDOR_NAME
    extension_name = "NOPAD"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0xA7:
            parser.track_extension('coment', '0xA7', self.vendor_name, self.extension_name)
            print(f"      No segment padding")
            return True
        return False
