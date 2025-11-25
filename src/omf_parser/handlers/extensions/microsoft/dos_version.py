"""Microsoft MS-DOS Version extension (0x9C)."""

from .. import VendorExtension
from . import VENDOR_NAME


class DOSVersionExtension(VendorExtension):
    """MS-DOS Version (COMENT class 0x9C).

    Obsolete Microsoft extension specifying target MS-DOS version.
    """

    vendor_name = VENDOR_NAME
    extension_name = "MS-DOS Version (obsolete)"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0x9C:
            parser.track_extension('coment', '0x9C', self.vendor_name, self.extension_name)
            if sub.bytes_remaining() >= 2:
                version = sub.parse_numeric(2)
                major = version >> 8
                minor = version & 0xFF
                print(f"      MS-DOS Version: {major}.{minor}")
            return True
        return False
