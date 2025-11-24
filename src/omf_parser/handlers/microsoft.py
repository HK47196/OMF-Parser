"""Microsoft extension record handlers."""

from ..constants import (
    MODE_IBM,
    COMDAT_SELECTION_NAMES,
    COMDAT_ALLOCATION_NAMES,
    COMDAT_ALIGN_NAMES,
    BAKPAT_LOCATION_NAMES
)


class MicrosoftHandlersMixin:

    def handle_comdef(self, sub, rec_type):
        """Handle COMDEF/LCOMDEF (B0H/B8H). Spec Page 54."""
        is_local = (rec_type == 0xB8)

        print(f"  {'Local ' if is_local else ''}Communal Definitions:")

        while sub.bytes_remaining() > 0:
            name = sub.parse_name()
            type_idx = sub.parse_index()
            data_type = sub.read_byte()

            if data_type is None:
                break

            if data_type == 0x61:
                num_elements = sub.parse_variable_length_int()
                element_size = sub.parse_variable_length_int()
                total = num_elements * element_size
                print(f"    '{name}' FAR: {num_elements} x {element_size} = {total} bytes")
            elif data_type == 0x62:
                size = sub.parse_variable_length_int()
                print(f"    '{name}' NEAR: {size} bytes")
            elif 0x01 <= data_type <= 0x5F:
                length = sub.parse_variable_length_int()
                print(f"    '{name}' Borland SegIdx={data_type}: {length} bytes")
            else:
                length = sub.parse_variable_length_int()
                print(f"    '{name}' DataType=0x{data_type:02X}: {length} bytes")

            # CRITICAL: COMDEF/LCOMDEF symbols are indexed together with EXTDEF/LEXTDEF
            # for FIXUPP external name index references (Spec Page 4)
            self.extdefs.append(name)

    def handle_comdat(self, sub, rec_type):
        """Handle COMDAT (C2H/C3H). Spec Page 63."""
        is_32bit = (rec_type == 0xC3)

        flags = sub.read_byte()
        attrib = sub.read_byte()
        align = sub.read_byte()

        if flags is None or attrib is None or align is None:
            return

        continuation = (flags & 0x01) != 0
        iterated = (flags & 0x02) != 0
        local = (flags & 0x04) != 0
        data_in_code = (flags & 0x08) != 0

        selection = (attrib >> 4) & 0x0F
        allocation = attrib & 0x0F

        print(f"  Flags: 0x{flags:02X}")
        print(f"    Continuation: {continuation}")
        print(f"    Iterated Data: {iterated}")
        print(f"    Local (LCOMDAT): {local}")
        print(f"    Data in Code Seg: {data_in_code}")

        print(f"  Attributes: 0x{attrib:02X}")
        print(f"    Selection: {COMDAT_SELECTION_NAMES.get(selection, f'Reserved({selection})')}")
        print(f"    Allocation: {COMDAT_ALLOCATION_NAMES.get(allocation, f'Reserved({allocation})')}")
        print(f"  Alignment: {COMDAT_ALIGN_NAMES.get(align, f'Unknown({align})')}")

        offset_size = 4 if is_32bit else 2
        enum_offset = sub.parse_numeric(offset_size)
        print(f"  Enum Offset: 0x{enum_offset:X}")

        type_idx = sub.parse_index()
        print(f"  Type Index: {type_idx}")

        if allocation == 0:
            base_grp = sub.parse_index()
            base_seg = sub.parse_index()
            print(f"  Base Group: {self.get_grpdef(base_grp)}")
            print(f"  Base Segment: {self.get_segdef(base_seg)}")
            if base_seg == 0 and base_grp == 0:
                frame = sub.parse_numeric(2)
                print(f"  Absolute Frame: 0x{frame:04X}")

        # NOTE: Microsoft LINK uses logical name index (1-2 bytes)
        # IBM LINK386 uses length-prefixed name string
        if self.target_mode == MODE_IBM:
            name = sub.parse_name()
            print(f"  Symbol: '{name}'")
        else:
            name_idx = sub.parse_index()
            print(f"  Symbol: {self.get_lname(name_idx)}")

        data_len = sub.bytes_remaining()
        print(f"  Data Length: {data_len} bytes")

    def handle_bakpat(self, sub, rec_type):
        """Handle BAKPAT (B2H/B3H). Spec Page 57."""
        is_32bit = (rec_type == 0xB3)

        print("  Backpatch Records:")

        while sub.bytes_remaining() > 0:
            seg_idx = sub.parse_index()
            loc_type = sub.read_byte()

            loc_str = BAKPAT_LOCATION_NAMES.get(loc_type, f"Unknown({loc_type})")

            # Validate location type 2 per spec
            if loc_type == 2 and rec_type == 0xB2:
                print(f"    [!] Warning: Location type 2 (DWord) only valid for B3H records")
                print(f"        Spec states: 'not supported yet' for this type")

            val_size = 4 if is_32bit else 2
            offset = sub.parse_numeric(val_size)
            value = sub.parse_numeric(val_size)

            print(f"    Segment: {self.get_segdef(seg_idx)}")
            print(f"    Location Type: {loc_str}")
            print(f"    Offset: 0x{offset:X}")
            print(f"    Value: 0x{value:X}")

    def handle_nbkpat(self, sub, rec_type):
        """Handle NBKPAT (C8H/C9H). Spec Page 69."""
        # NOTE: NBKPAT has INVERTED bit order per spec page 69:
        # "These fields are 32 bits for record type C8H, 16 bits for C9H."
        # This is OPPOSITE of normal OMF convention where odd = 32-bit
        is_32bit = (rec_type == 0xC8)

        print("  Named Backpatch Records:")

        while sub.bytes_remaining() > 0:
            loc_type = sub.read_byte()

            # NOTE: IBM LINK386 uses length-prefixed name here instead of index
            # Microsoft uses logical name index
            if self.target_mode == MODE_IBM:
                name = sub.parse_name()
                print(f"    Symbol: '{name}'")
            else:
                name_idx = sub.parse_index()
                print(f"    Symbol: {self.get_lname(name_idx)}")

            # IBM LINK386 defines location type 9 as 32-bit offset
            if self.target_mode == MODE_IBM:
                loc_names = {0: "Byte(8)", 1: "Word(16)", 2: "DWord(32)", 9: "DWord(32-IBM)"}
            else:
                loc_names = {0: "Byte(8)", 1: "Word(16)", 2: "DWord(32)"}
            loc_str = loc_names.get(loc_type, f"Unknown({loc_type})")

            val_size = 4 if is_32bit else 2
            offset = sub.parse_numeric(val_size)
            value = sub.parse_numeric(val_size)

            print(f"    Location Type: {loc_str}")
            print(f"    Offset: 0x{offset:X}")
            print(f"    Value: 0x{value:X}")

    def handle_linsym(self, sub, rec_type):
        """Handle LINSYM (C4H/C5H). Spec Page 66."""
        is_32bit = (rec_type == 0xC5)

        flags = sub.read_byte()
        continuation = (flags & 0x01) != 0

        print(f"  Flags: Continuation={continuation}")
        # NOTE: Microsoft LINK uses logical name index (1-2 bytes)
        # IBM LINK386 uses length-prefixed name string
        if self.target_mode == MODE_IBM:
            name = sub.parse_name()
            print(f"  Symbol: '{name}'")
        else:
            name_idx = sub.parse_index()
            print(f"  Symbol: {self.get_lname(name_idx)}")
        print("  Line Number Entries:")

        while sub.bytes_remaining() > 0:
            line_num = sub.parse_numeric(2)
            offset_size = 4 if is_32bit else 2
            offset = sub.parse_numeric(offset_size)

            if line_num == 0:
                print(f"    Line 0 (end of function): Offset=0x{offset:X}")
            else:
                print(f"    Line {line_num}: Offset=0x{offset:X}")

    def handle_alias(self, sub):
        """Handle ALIAS (C6H). Spec Page 68."""
        print("  Alias Definitions:")

        while sub.bytes_remaining() > 0:
            alias_name = sub.parse_name()
            subst_name = sub.parse_name()
            print(f"    '{alias_name}' -> '{subst_name}'")
