"""Microsoft Date extension (0xDC)."""

from .. import VendorExtension
from . import VENDOR_NAME


class DateExtension(VendorExtension):
    """Date (COMENT class 0xDC).

    Compilation date.
    """

    vendor_name = VENDOR_NAME
    extension_name = "Date"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0xDC:
            parser.track_extension('coment', '0xDC', self.vendor_name, self.extension_name)
            if text:
                try:
                    date_text = text.decode('ascii', errors='replace') if isinstance(text, bytes) else text
                    print(f"      Date: {date_text}")
                except:
                    print(f"      Date: {text.hex().upper() if isinstance(text, bytes) else text}")
            return True
        return False
