"""Intel LIBMOD extension (0xA3)."""

from .. import VendorExtension
from . import VENDOR_NAME


class LIBMODExtension(VendorExtension):
    """LIBMOD (COMENT class 0xA3).

    Library module name.
    """

    vendor_name = VENDOR_NAME
    extension_name = "LIBMOD"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0xA3:
            parser.track_extension('coment', '0xA3', self.vendor_name, self.extension_name)
            if text:
                try:
                    libmod_text = text.decode('ascii', errors='replace') if isinstance(text, bytes) else text
                    print(f"      Library module: {libmod_text}")
                except:
                    print(f"      Library module: {text.hex().upper() if isinstance(text, bytes) else text}")
            return True
        return False
