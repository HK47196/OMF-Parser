"""Intel EXESTR extension (0xA4)."""

from .. import VendorExtension
from . import VENDOR_NAME


class EXESTRExtension(VendorExtension):
    """EXESTR (COMENT class 0xA4).

    Executable string.
    """

    vendor_name = VENDOR_NAME
    extension_name = "EXESTR"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0xA4:
            parser.track_extension('coment', '0xA4', self.vendor_name, self.extension_name)
            if text:
                try:
                    exe_text = text.decode('ascii', errors='replace') if isinstance(text, bytes) else text
                    print(f"      Executable string: {exe_text}")
                except:
                    print(f"      Executable string: {text.hex().upper() if isinstance(text, bytes) else text}")
            return True
        return False
