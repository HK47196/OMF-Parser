"""Intel WKEXT extension (0xA8)."""

from .. import VendorExtension
from . import VENDOR_NAME


class WKEXTExtension(VendorExtension):
    """WKEXT (COMENT class 0xA8).

    Weak external definition - allows alternative if primary symbol not found.
    """

    vendor_name = VENDOR_NAME
    extension_name = "WKEXT (Weak External)"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0xA8:
            parser.track_extension('coment', '0xA8', self.vendor_name, self.extension_name)
            if sub.bytes_remaining() >= 2:
                weak_idx = sub.parse_index()
                default_idx = sub.parse_index()
                print(f"      Weak: {parser.get_extdef(weak_idx)} "
                      f"Default: {parser.get_extdef(default_idx)}")
            return True
        return False
