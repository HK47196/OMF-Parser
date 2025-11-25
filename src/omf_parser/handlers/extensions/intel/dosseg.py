"""Intel DOSSEG extension (0x9E)."""

from .. import VendorExtension
from . import VENDOR_NAME


class DOSSEGExtension(VendorExtension):
    """DOSSEG (COMENT class 0x9E).

    Requests DOS segment ordering convention.
    """

    vendor_name = VENDOR_NAME
    extension_name = "DOSSEG"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0x9E:
            parser.track_extension('coment', '0x9E', self.vendor_name, self.extension_name)
            print(f"      DOS segment ordering requested")
            return True
        return False
