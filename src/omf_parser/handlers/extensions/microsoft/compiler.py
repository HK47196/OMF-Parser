"""Microsoft Compiler extension (0xDB)."""

from .. import VendorExtension
from . import VENDOR_NAME


class CompilerExtension(VendorExtension):
    """Compiler (COMENT class 0xDB).

    Identifies the compiler that generated the object file.
    """

    vendor_name = VENDOR_NAME
    extension_name = "Compiler"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0xDB:
            parser.track_extension('coment', '0xDB', self.vendor_name, self.extension_name)
            if text:
                try:
                    compiler_text = text.decode('ascii', errors='replace') if isinstance(text, bytes) else text
                    print(f"      Compiler: {compiler_text}")
                except:
                    print(f"      Compiler: {text.hex().upper() if isinstance(text, bytes) else text}")
            return True
        return False
