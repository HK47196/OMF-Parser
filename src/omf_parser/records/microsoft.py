"""Microsoft extension record handlers."""

from . import omf_record
from ..constants import (
    COMDAT_SELECTION_NAMES,
    COMDAT_ALLOCATION_NAMES,
    COMDAT_ALIGN_NAMES,
    BAKPAT_LOCATION_NAMES
)


@omf_record(0xB0, 0xB8)
def handle_comdef(omf, record):
    """Handle COMDEF/LCOMDEF (B0H/B8H)."""
    sub = omf.make_parser(record)
    is_local = (record.type == 0xB8)

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

        omf.extdefs.append(name)


@omf_record(0xC2, 0xC3)
def handle_comdat(omf, record):
    """Handle COMDAT (C2H/C3H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == 0xC3)

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

    offset_size = sub.get_offset_field_size(is_32bit)
    enum_offset = sub.parse_numeric(offset_size)
    print(f"  Enum Offset: 0x{enum_offset:X}")

    type_idx = sub.parse_index()
    print(f"  Type Index: {type_idx}")

    if allocation == 0:
        base_grp = sub.parse_index()
        base_seg = sub.parse_index()
        print(f"  Base Group: {omf.get_grpdef(base_grp)}")
        print(f"  Base Segment: {omf.get_segdef(base_seg)}")
        if base_seg == 0 and base_grp == 0:
            frame = sub.parse_numeric(2)
            print(f"  Absolute Frame: 0x{frame:04X}")

    if omf.variant.comdat_uses_inline_name():
        name = sub.parse_name()
        print(f"  Symbol: '{name}'")
    else:
        name_idx = sub.parse_index()
        print(f"  Symbol: {omf.get_lname(name_idx)}")

    data_len = sub.bytes_remaining()
    print(f"  Data Length: {data_len} bytes")


@omf_record(0xB2, 0xB3)
def handle_bakpat(omf, record):
    """Handle BAKPAT (B2H/B3H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == 0xB3)

    print("  Backpatch Records:")

    while sub.bytes_remaining() > 0:
        seg_idx = sub.parse_index()
        loc_type = sub.read_byte()

        loc_str = BAKPAT_LOCATION_NAMES.get(loc_type, f"Unknown({loc_type})")

        if loc_type == 2 and record.type == 0xB2:
            omf.add_warning(f"    [!] Warning: Location type 2 (DWord) only valid for B3H records")

        val_size = sub.get_offset_field_size(is_32bit)
        offset = sub.parse_numeric(val_size)
        value = sub.parse_numeric(val_size)

        print(f"    Segment: {omf.get_segdef(seg_idx)}")
        print(f"    Location Type: {loc_str}")
        print(f"    Offset: 0x{offset:X}")
        print(f"    Value: 0x{value:X}")


@omf_record(0xC8, 0xC9)
def handle_nbkpat(omf, record):
    """Handle NBKPAT (C8H/C9H)."""
    sub = omf.make_parser(record)
    # NBKPAT has INVERTED bit order: C8H = 32-bit, C9H = 16-bit
    is_32bit = (record.type == 0xC8)

    print("  Named Backpatch Records:")

    loc_names = omf.variant.nbkpat_loc_names()

    while sub.bytes_remaining() > 0:
        loc_type = sub.read_byte()

        if omf.variant.nbkpat_uses_inline_name():
            name = sub.parse_name()
            print(f"    Symbol: '{name}'")
        else:
            name_idx = sub.parse_index()
            print(f"    Symbol: {omf.get_lname(name_idx)}")

        loc_str = loc_names.get(loc_type, f"Unknown({loc_type})")

        val_size = sub.get_offset_field_size(is_32bit)
        offset = sub.parse_numeric(val_size)
        value = sub.parse_numeric(val_size)

        print(f"    Location Type: {loc_str}")
        print(f"    Offset: 0x{offset:X}")
        print(f"    Value: 0x{value:X}")


@omf_record(0xC4, 0xC5)
def handle_linsym(omf, record):
    """Handle LINSYM (C4H/C5H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == 0xC5)

    flags = sub.read_byte()
    continuation = (flags & 0x01) != 0

    print(f"  Flags: Continuation={continuation}")

    if omf.variant.linsym_uses_inline_name():
        name = sub.parse_name()
        print(f"  Symbol: '{name}'")
    else:
        name_idx = sub.parse_index()
        print(f"  Symbol: {omf.get_lname(name_idx)}")

    print("  Line Number Entries:")

    while sub.bytes_remaining() > 0:
        line_num = sub.parse_numeric(2)
        offset_size = sub.get_offset_field_size(is_32bit)
        offset = sub.parse_numeric(offset_size)

        if line_num == 0:
            print(f"    Line 0 (end of function): Offset=0x{offset:X}")
        else:
            print(f"    Line {line_num}: Offset=0x{offset:X}")


@omf_record(0xC6)
def handle_alias(omf, record):
    """Handle ALIAS (C6H)."""
    sub = omf.make_parser(record)
    print("  Alias Definitions:")

    while sub.bytes_remaining() > 0:
        alias_name = sub.parse_name()
        subst_name = sub.parse_name()
        print(f"    '{alias_name}' -> '{subst_name}'")
