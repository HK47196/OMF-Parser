"""Microsoft Timestamp extension (0xDD)."""

from .. import VendorExtension
from . import VENDOR_NAME


class TimestampExtension(VendorExtension):
    """Timestamp (COMENT class 0xDD).

    Compilation timestamp.
    """

    vendor_name = VENDOR_NAME
    extension_name = "Timestamp"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0xDD:
            parser.track_extension('coment', '0xDD', self.vendor_name, self.extension_name)
            if text:
                try:
                    timestamp_text = text.decode('ascii', errors='replace') if isinstance(text, bytes) else text
                    print(f"      Timestamp: {timestamp_text}")
                except:
                    print(f"      Timestamp: {text.hex().upper() if isinstance(text, bytes) else text}")
            return True
        return False
