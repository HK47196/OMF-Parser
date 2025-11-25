"""Intel Link Pass Separator extension (0xA2)."""

from .. import VendorExtension
from . import VENDOR_NAME


class LinkPassSeparatorExtension(VendorExtension):
    """Link Pass Separator (COMENT class 0xA2).

    Separates multi-pass linker operations.
    """

    vendor_name = VENDOR_NAME
    extension_name = "Link Pass Separator"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0xA2:
            parser.track_extension('coment', '0xA2', self.vendor_name, self.extension_name)
            print(f"      Link pass separator (multi-pass linker)")
            return True
        return False
