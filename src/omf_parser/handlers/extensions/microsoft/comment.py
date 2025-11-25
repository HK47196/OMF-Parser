"""Microsoft Comment extension (0xDA)."""

from .. import VendorExtension
from . import VENDOR_NAME


class CommentExtension(VendorExtension):
    """Comment (COMENT class 0xDA).

    General-purpose comment text.
    """

    vendor_name = VENDOR_NAME
    extension_name = "Comment"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0xDA:
            parser.track_extension('coment', '0xDA', self.vendor_name, self.extension_name)
            if text:
                try:
                    comment_text = text.decode('ascii', errors='replace') if isinstance(text, bytes) else text
                    print(f"      Comment: {comment_text}")
                except:
                    print(f"      Comment: {text.hex().upper() if isinstance(text, bytes) else text}")
            return True
        return False
