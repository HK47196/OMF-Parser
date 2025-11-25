"""Intel INCERR extension (0xA6)."""

from .. import VendorExtension
from . import VENDOR_NAME


class INCERRExtension(VendorExtension):
    """INCERR (COMENT class 0xA6).

    Incremental compilation error recovery.
    """

    vendor_name = VENDOR_NAME
    extension_name = "INCERR"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0xA6:
            parser.track_extension('coment', '0xA6', self.vendor_name, self.extension_name)
            print(f"      Incremental compilation error recovery")
            return True
        return False
