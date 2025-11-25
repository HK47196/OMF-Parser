"""Microsoft User extension (0xDF)."""

from .. import VendorExtension
from . import VENDOR_NAME


class UserExtension(VendorExtension):
    """User (COMENT class 0xDF).

    User-defined comment.
    """

    vendor_name = VENDOR_NAME
    extension_name = "User"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0xDF:
            parser.track_extension('coment', '0xDF', self.vendor_name, self.extension_name)
            if text:
                try:
                    user_text = text.decode('ascii', errors='replace') if isinstance(text, bytes) else text
                    print(f"      User: {user_text}")
                except:
                    print(f"      User: {text.hex().upper() if isinstance(text, bytes) else text}")
            return True
        return False
