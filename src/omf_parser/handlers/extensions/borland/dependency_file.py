"""Borland Dependency File extension (0xE9)."""

from .. import VendorExtension
from . import VENDOR_NAME


class DependencyFileExtension(VendorExtension):
    """Dependency File (COMENT class 0xE9).

    Specifies source file dependencies for incremental compilation.
    """

    vendor_name = VENDOR_NAME
    extension_name = "Dependency File"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0xE9:
            parser.track_extension('coment', '0xE9', self.vendor_name, self.extension_name)
            if text:
                try:
                    dep_text = text.decode('ascii', errors='replace') if isinstance(text, bytes) else text
                    print(f"      Dependency: {dep_text}")
                except:
                    print(f"      Dependency: {text.hex().upper() if isinstance(text, bytes) else text}")
            return True
        return False
