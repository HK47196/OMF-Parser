"""Intel Translator extension (0x00)."""

from .. import VendorExtension
from . import VENDOR_NAME


class TranslatorExtension(VendorExtension):
    """Translator (COMENT class 0x00).

    Identifies the translator (compiler/assembler) that generated the object file.
    """

    vendor_name = VENDOR_NAME
    extension_name = "Translator"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0x00:
            parser.track_extension('coment', '0x00', self.vendor_name, self.extension_name)
            if text:
                try:
                    translator_text = text.decode('ascii', errors='replace') if isinstance(text, bytes) else text
                    print(f"      Translator: {translator_text}")
                except:
                    print(f"      Translator: {text.hex().upper() if isinstance(text, bytes) else text}")
            return True
        return False
