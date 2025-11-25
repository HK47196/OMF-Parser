"""Intel Copyright extension (0x01)."""

from .. import VendorExtension
from . import VENDOR_NAME


class CopyrightExtension(VendorExtension):
    """Intel Copyright (COMENT class 0x01).

    Intel copyright notice.
    """

    vendor_name = VENDOR_NAME
    extension_name = "Intel Copyright"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0x01:
            parser.track_extension('coment', '0x01', self.vendor_name, self.extension_name)
            if text:
                try:
                    copyright_text = text.decode('ascii', errors='replace') if isinstance(text, bytes) else text
                    print(f"      Copyright: {copyright_text}")
                except:
                    print(f"      Copyright: {text.hex().upper() if isinstance(text, bytes) else text}")
            return True
        return False
