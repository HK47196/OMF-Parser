"""Intel New OMF Extension (0xA1)."""

from .. import VendorExtension
from . import VENDOR_NAME


class NewOMFExtension(VendorExtension):
    """New OMF Extension (COMENT class 0xA1).

    Indicates new OMF extensions.
    """

    vendor_name = VENDOR_NAME
    extension_name = "New OMF Extension"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0xA1:
            parser.track_extension('coment', '0xA1', self.vendor_name, self.extension_name)
            if sub.bytes_remaining() > 0:
                raw = sub.read_bytes(sub.bytes_remaining())
                print(f"      Data: {raw.hex().upper()}")
            return True
        return False
