"""Microsoft Memory Model extension (0x9D)."""

from .. import VendorExtension
from . import VENDOR_NAME


class MemoryModelExtension(VendorExtension):
    """Memory Model (COMENT class 0x9D).

    Specifies the memory model used by the compiler (Small, Medium, Compact, Large, Huge).
    """

    vendor_name = VENDOR_NAME
    extension_name = "Memory Model"

    def handle_coment(self, parser, sub, cls, flags, text):
        if cls == 0x9D:
            parser.track_extension('coment', '0x9D', self.vendor_name, self.extension_name)
            if sub.bytes_remaining() >= 1:
                model = sub.read_byte()
                models = {
                    0x53: "Small",
                    0x43: "Compact",
                    0x4D: "Medium",
                    0x4C: "Large",
                    0x48: "Huge"
                }
                model_name = models.get(model, f"Unknown(0x{model:02X})")
                print(f"      Memory Model: {model_name}")
            return True
        return False
