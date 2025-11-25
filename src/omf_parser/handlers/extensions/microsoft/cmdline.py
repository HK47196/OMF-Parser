"""Microsoft Command Line extension (0xFF)."""

from .. import VendorExtension
from . import VENDOR_NAME


class CommandLineExtension(VendorExtension):
    """Command Line (COMENT class 0xFF).

    QuickC command line options.
    """

    vendor_name = VENDOR_NAME
    extension_name = "Command Line (QuickC)"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0xFF:
            parser.track_extension('coment', '0xFF', self.vendor_name, self.extension_name)
            if text:
                try:
                    cmdline_text = text.decode('ascii', errors='replace') if isinstance(text, bytes) else text
                    print(f"      Command Line: {cmdline_text}")
                except:
                    print(f"      Command Line: {text.hex().upper() if isinstance(text, bytes) else text}")
            return True
        return False
