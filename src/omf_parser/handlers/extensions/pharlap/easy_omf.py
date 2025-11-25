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

    def handle_fixupp_location_type(self, parser, loc_type):
        """PharLap has additional location types for 386."""
        if parser.target_mode != MODE_PHARLAP:
            return None

        # PharLap-specific location types
        pharlap_types = {
            0x0D: ("PharLap:386-Offset32", 4),
            0x0E: ("PharLap:386-Pointer48", 6),
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
