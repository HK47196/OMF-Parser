"""Intel LZEXT extension (0xA9)."""

from .. import VendorExtension
from . import VENDOR_NAME


class LZEXTExtension(VendorExtension):
    """LZEXT (COMENT class 0xA9).

    Lazy external definition - symbol resolved on first use.
    """

    vendor_name = VENDOR_NAME
    extension_name = "LZEXT (Lazy External)"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0xA9:
            parser.track_extension('coment', '0xA9', self.vendor_name, self.extension_name)
            if sub.bytes_remaining() >= 1:
                lazy_idx = sub.parse_index()
                print(f"      Lazy: {parser.get_extdef(lazy_idx)}")
            return True
        return False
