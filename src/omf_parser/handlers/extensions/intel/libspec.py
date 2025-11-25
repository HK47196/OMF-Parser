"""Intel Library Specifier extension (0x81)."""

from .. import VendorExtension
from . import VENDOR_NAME


class LibrarySpecifierExtension(VendorExtension):
    """Library Specifier (COMENT class 0x81).

    Obsolete library specifier.
    """

    vendor_name = VENDOR_NAME
    extension_name = "Library Specifier (obsolete)"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0x81:
            parser.track_extension('coment', '0x81', self.vendor_name, self.extension_name)
            if text:
                try:
                    lib_text = text.decode('ascii', errors='replace') if isinstance(text, bytes) else text
                    print(f"      Library: {lib_text}")
                except:
                    print(f"      Library: {text.hex().upper() if isinstance(text, bytes) else text}")
            return True
        return False
