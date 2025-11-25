"""Obsolete Intel 8086 record handlers."""

from ..constants import REGISTER_NAMES


class ObsoleteHandlersMixin:

    def handle_rheadr(self, sub):
        """Handle RHEADR (6EH) - R-Module Header. Spec Appendix 3."""
        print("  [Obsolete] R-Module Header")
        print("    Identifies a module processed by LINK-86/LOCATE-86")
        name = sub.parse_name()
        if name:
            print(f"    Name: {name}")
        if sub.bytes_remaining() > 0:
            print(f"    Attributes: {sub.format_hex_with_ascii(sub.data[sub.offset:])}")

    def handle_regint(self, sub):
        """Handle REGINT (70H) - Register Initialization. Spec Appendix 3."""
        print("  [Obsolete] Register Initialization")
        print("    Provides initial values for 8086 registers")
        while sub.bytes_remaining() >= 3:
            reg_type = sub.read_byte()
            value = sub.parse_numeric(2)
            print(f"    {REGISTER_NAMES.get(reg_type, f'Reg{reg_type}')}: 0x{value:04X}")

    def handle_redata_pedata(self, sub, rec_type):
        """Handle REDATA (72H) / PEDATA (84H). Spec Appendix 3."""
        if rec_type == 0x72:
            # REDATA: Relocatable Enumerated Data - uses Segment Index
            print(f"  [Obsolete] REDATA (Relocatable) Enumerated Data")
            seg_idx = sub.parse_index()
            print(f"    Segment: {self.get_segdef(seg_idx)}")
            offset = sub.parse_numeric(2)
            print(f"    Offset: 0x{offset:04X}")
        else:
            # PEDATA: Physical Enumerated Data - uses Frame Number (physical address)
            print(f"  [Obsolete] PEDATA (Physical) Enumerated Data")
            frame = sub.parse_numeric(2)
            print(f"    Frame Number: 0x{frame:04X}")
            offset = sub.parse_numeric(2)
            print(f"    Offset: 0x{offset:04X}")
            print(f"    Physical Address: 0x{(frame << 4) + offset:06X}")

        data_len = sub.bytes_remaining()
        print(f"    Data Length: {data_len} bytes")
        if data_len > 0:
            preview = sub.data[sub.offset:sub.offset + min(16, data_len)]
            print(f"    Data Preview: {sub.format_hex_with_ascii(preview)}")

    def handle_ridata_pidata(self, sub, rec_type):
        """Handle RIDATA (74H) / PIDATA (86H). Spec Appendix 3."""
        if rec_type == 0x74:
            # RIDATA: Relocatable Iterated Data - uses Segment Index
            print(f"  [Obsolete] RIDATA (Relocatable) Iterated Data")
            seg_idx = sub.parse_index()
            print(f"    Segment: {self.get_segdef(seg_idx)}")
            offset = sub.parse_numeric(2)
            print(f"    Offset: 0x{offset:04X}")
        else:
            # PIDATA: Physical Iterated Data - uses Frame Number
            print(f"  [Obsolete] PIDATA (Physical) Iterated Data")
            frame = sub.parse_numeric(2)
            print(f"    Frame Number: 0x{frame:04X}")
            offset = sub.parse_numeric(2)
            print(f"    Offset: 0x{offset:04X}")
            print(f"    Physical Address: 0x{(frame << 4) + offset:06X}")

        print("    (Iterated data follows)")
        if sub.bytes_remaining() > 0:
            print(f"    Remaining Data: {sub.bytes_remaining()} bytes")

    def handle_ovldef(self, sub):
        """Handle OVLDEF (76H) - Overlay Definition. Spec Appendix 3."""
        print("  [Obsolete] Overlay Definition")
        name = sub.parse_name()
        print(f"    Overlay Name: '{name}'")

        if sub.bytes_remaining() >= 2:
            attrib = sub.parse_numeric(2)
            print(f"    Overlay Attribute: 0x{attrib:04X}")

        if sub.bytes_remaining() >= 4:
            file_location = sub.parse_numeric(4)
            print(f"    File Location: 0x{file_location:08X}")

        if sub.bytes_remaining() > 0:
            print(f"    Additional Data: {sub.format_hex_with_ascii(sub.data[sub.offset:])}")

    def handle_endrec(self, sub):
        """Handle ENDREC (78H) - End Record. Spec Appendix 3."""
        print("  [Obsolete] End Record")
        print("    Denotes end of a set of records (block or overlay)")

    def handle_blkdef(self, sub):
        """Handle BLKDEF (7AH) - Block Definition. Spec Appendix 3."""
        print("  [Obsolete] Block Definition")
        print("    Debug info for procedure/block scope")

        # Parse the BLKDEF structure
        base_grp = sub.parse_index()
        base_seg = sub.parse_index()

        print(f"    Base Group: {self.get_grpdef(base_grp)}")
        print(f"    Base Segment: {self.get_segdef(base_seg)}")

        # Frame number exists if base_seg == 0
        if base_seg == 0:
            frame = sub.parse_numeric(2)
            print(f"    Frame Number: 0x{frame:04X}")

        name = sub.parse_name()
        print(f"    Block Name: '{name}'")

        offset_size = sub.get_offset_field_size(False)
        offset = sub.parse_numeric(offset_size)
        print(f"    Offset: 0x{offset:0{offset_size*2}X}")

        # Debug info length and data
        if sub.bytes_remaining() > 0:
            debug_len = sub.parse_numeric(2)
            print(f"    Debug Info Length: {debug_len} bytes")
            if debug_len > 0 and sub.bytes_remaining() > 0:
                debug_data = sub.read_bytes(min(debug_len, sub.bytes_remaining()))
                print(f"    Debug Data: {sub.format_hex_with_ascii(debug_data)}")

    def handle_blkend(self, sub):
        """Handle BLKEND (7CH) - Block End. Spec Appendix 3."""
        print("  [Obsolete] Block End")
        print("    Closes a BLKDEF scope")

    def handle_debsym(self, sub):
        """Handle DEBSYM (7EH) - Debug Symbols. Spec Appendix 3."""
        print("  [Obsolete] Debug Symbols")
        print("    Local symbols including stack and based symbols")
        if sub.bytes_remaining() > 0:
            print(f"    Data: {sub.format_hex_with_ascii(sub.data[sub.offset:])}")

    def handle_libhed_obsolete(self, sub):
        """Handle LIBHED (A4H) - Obsolete Intel Library Header. Spec Appendix 3."""
        print("  [Obsolete Intel] Library Header")
        print("    Note: Conflicts with MS EXESTR comment class")
        if sub.bytes_remaining() > 0:
            print(f"    Data: {sub.format_hex_with_ascii(sub.data[sub.offset:])}")

    def handle_libnam_obsolete(self, sub):
        """Handle LIBNAM (A6H) - Obsolete Intel Library Names. Spec Appendix 3."""
        print("  [Obsolete Intel] Library Module Names")
        print("    Lists module names in sequence of appearance")
        while sub.bytes_remaining() > 0:
            name = sub.parse_name()
            if name:
                print(f"    Module: {name}")

    def handle_libloc_obsolete(self, sub):
        """Handle LIBLOC (A8H) - Obsolete Intel Library Locations. Spec Appendix 3."""
        print("  [Obsolete Intel] Library Module Locations")
        count = 0
        while sub.bytes_remaining() >= 4:
            location = sub.parse_numeric(4)
            print(f"    Module {count}: Offset 0x{location:08X}")
            count += 1

    def handle_libdic_obsolete(self, sub):
        """Handle LIBDIC (AAH) - Obsolete Intel Library Dictionary. Spec Appendix 3."""
        print("  [Obsolete Intel] Library Dictionary")
        print("    Public symbols grouped by defining module")
        if sub.bytes_remaining() > 0:
            print(f"    Data: {sub.format_hex_with_ascii(sub.data[sub.offset:])}")
