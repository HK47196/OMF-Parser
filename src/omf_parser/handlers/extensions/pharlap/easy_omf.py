"""PharLap Easy OMF-386 extension."""

from .. import VendorExtension
from . import VENDOR_NAME
from ....constants import MODE_PHARLAP


class PharLapEasyOMFExtension(VendorExtension):
    """PharLap 386|DOS-Extender Easy OMF-386 format.

    This extension changes core parsing behavior:
    - 0xAA comment class signals 32-bit mode
    - All offset/length fields become 4 bytes
    - LIDATA32 still uses 2-byte repeat counts (not 4-byte)
    - Additional FIXUPP location types (0x0D, 0x0E)
    - SEGDEF may have extended attributes
    """

    vendor_name = VENDOR_NAME
    extension_name = "Easy OMF-386"

    def is_active(self, parser):
        """Active when PharLap mode is detected.

        Mode detection happens via detect_mode() before parsing starts,
        so this extension only activates for files already identified as PharLap.
        """
        return parser.target_mode == MODE_PHARLAP

    def handle_coment(self, parser, sub, cls, flags, text):
        """Handle 0xAA Easy OMF marker comment."""
        if cls == 0xAA:
            parser.track_extension('coment', '0xAA', self.vendor_name,
                                 f'{self.extension_name} marker')
            if text:
                try:
                    marker_text = text.decode('ascii', errors='replace') if isinstance(text, bytes) else text
                    print(f"      Marker: {marker_text}")
                except:
                    print(f"      Marker data: {text.hex().upper() if isinstance(text, bytes) else text}")
            return True
        return False

    def get_offset_field_size(self, parser, is_32bit):
        """PharLap uses 4-byte fields in all offset/length positions."""
        if parser.target_mode == MODE_PHARLAP:
            return 4
        return None

    def handle_segdef_extension(self, parser, sub, is_32bit, seg_info):
        """PharLap SEGDEF may have extended attributes."""
        if parser.target_mode != MODE_PHARLAP:
            return None

        # Check for extended attributes
        if sub.bytes_remaining() >= 1:
            ext_flags = sub.read_byte()
            if ext_flags is not None:
                parser.track_extension('segdef_ext', 'flags', self.vendor_name,
                                     f'Extended flags: 0x{ext_flags:02X}')
                print(f"      Extended flags: 0x{ext_flags:02X}")
                return {'extended_flags': ext_flags}

        return None

    def get_segdef_alignment_name(self, parser, align):
        """PharLap defines alignment 6 as 4K page boundary."""
        if parser.target_mode != MODE_PHARLAP:
            return None

        if align == 6:
            return "4K Page"
        return None

    def handle_fixupp_location_type(self, parser, loc_type):
        """PharLap redefines location types 5 and 6 for 386.

        Per Easy OMF-386 spec:
        - Loc=5: 32-bit offset (replaces standard 'Ldr-Offset(16)')
        - Loc=6: Base + 32-bit offset / long pointer (replaces 'Reserved(6)')
        """
        if parser.target_mode != MODE_PHARLAP:
            return None

        # PharLap redefines these standard location types
        pharlap_types = {
            5: ("Offset(32)", 4),           # 32-bit offset
            6: ("Ptr(16:32)", 6),            # Base + 32-bit offset (48-bit pointer)
        }

        if loc_type in pharlap_types:
            type_name, size = pharlap_types[loc_type]
            parser.track_extension('fixupp_loc', f'0x{loc_type:02X}', self.vendor_name,
                                 f'{self.extension_name}: {type_name}')
            return (type_name, size)

        return None

    def handle_lidata_repeat_count_size(self, parser, is_32bit):
        """PharLap uses 2-byte repeat counts even in LIDATA32.

        This differs from TIS standard which uses 4-byte in LIDATA32.
        """
        if parser.target_mode == MODE_PHARLAP and is_32bit:
            parser.track_extension('lidata', 'repeat_count', self.vendor_name,
                                 f'{self.extension_name}: LIDATA32 uses 2-byte repeat count')
            return 2
        return None
