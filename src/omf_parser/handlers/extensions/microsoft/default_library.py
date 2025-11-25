"""Microsoft Default Library Search extension (0x9F)."""

from .. import VendorExtension
from . import VENDOR_NAME


class DefaultLibraryExtension(VendorExtension):
    """Default Library Search (COMENT class 0x9F).

    Specifies default libraries to search during linking.
    """

    vendor_name = VENDOR_NAME
    extension_name = "Default Library Search"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0x9F:
            parser.track_extension('coment', '0x9F', self.vendor_name, self.extension_name)
            if text:
                try:
                    lib_name = text.decode('ascii', errors='replace') if isinstance(text, bytes) else text
                    print(f"      Library: {lib_name}")
                except:
                    print(f"      Library: {text.hex().upper() if isinstance(text, bytes) else text}")
            return True
        return False
