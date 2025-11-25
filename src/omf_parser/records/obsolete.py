"""Obsolete Intel 8086 record handlers."""

from . import omf_record
from ..parsing import format_hex_with_ascii
from ..constants import REGISTER_NAMES


@omf_record(0x6E)
def handle_rheadr(omf, record):
    """Handle RHEADR (6EH) - R-Module Header."""
    sub = omf.make_parser(record)
    print("  [Obsolete] R-Module Header")
    print("    Identifies a module processed by LINK-86/LOCATE-86")
    name = sub.parse_name()
    if name:
        print(f"    Name: {name}")
    if sub.bytes_remaining() > 0:
        print(f"    Attributes: {format_hex_with_ascii(sub.data[sub.offset:])}")


@omf_record(0x70)
def handle_regint(omf, record):
    """Handle REGINT (70H) - Register Initialization."""
    sub = omf.make_parser(record)
    print("  [Obsolete] Register Initialization")
    print("    Provides initial values for 8086 registers")
    while sub.bytes_remaining() >= 3:
        reg_type = sub.read_byte()
        value = sub.parse_numeric(2)
        print(f"    {REGISTER_NAMES.get(reg_type, f'Reg{reg_type}')}: 0x{value:04X}")


@omf_record(0x72, 0x84)
def handle_redata_pedata(omf, record):
    """Handle REDATA (72H) / PEDATA (84H)."""
    sub = omf.make_parser(record)

    if record.type == 0x72:
        print(f"  [Obsolete] REDATA (Relocatable) Enumerated Data")
        seg_idx = sub.parse_index()
        print(f"    Segment: {omf.get_segdef(seg_idx)}")
        offset = sub.parse_numeric(2)
        print(f"    Offset: 0x{offset:04X}")
    else:
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
        print(f"    Data Preview: {format_hex_with_ascii(preview)}")


@omf_record(0x74, 0x86)
def handle_ridata_pidata(omf, record):
    """Handle RIDATA (74H) / PIDATA (86H)."""
    sub = omf.make_parser(record)

    if record.type == 0x74:
        print(f"  [Obsolete] RIDATA (Relocatable) Iterated Data")
        seg_idx = sub.parse_index()
        print(f"    Segment: {omf.get_segdef(seg_idx)}")
        offset = sub.parse_numeric(2)
        print(f"    Offset: 0x{offset:04X}")
    else:
        print(f"  [Obsolete] PIDATA (Physical) Iterated Data")
        frame = sub.parse_numeric(2)
        print(f"    Frame Number: 0x{frame:04X}")
        offset = sub.parse_numeric(2)
        print(f"    Offset: 0x{offset:04X}")
        print(f"    Physical Address: 0x{(frame << 4) + offset:06X}")

    print("    (Iterated data follows)")
    if sub.bytes_remaining() > 0:
        print(f"    Remaining Data: {sub.bytes_remaining()} bytes")


@omf_record(0x76)
def handle_ovldef(omf, record):
    """Handle OVLDEF (76H) - Overlay Definition."""
    sub = omf.make_parser(record)
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
        print(f"    Additional Data: {format_hex_with_ascii(sub.data[sub.offset:])}")


@omf_record(0x78)
def handle_endrec(omf, record):
    """Handle ENDREC (78H) - End Record."""
    print("  [Obsolete] End Record")
    print("    Denotes end of a set of records (block or overlay)")


@omf_record(0x7A)
def handle_blkdef(omf, record):
    """Handle BLKDEF (7AH) - Block Definition."""
    sub = omf.make_parser(record)
    print("  [Obsolete] Block Definition")
    print("    Debug info for procedure/block scope")

    base_grp = sub.parse_index()
    base_seg = sub.parse_index()

    print(f"    Base Group: {omf.get_grpdef(base_grp)}")
    print(f"    Base Segment: {omf.get_segdef(base_seg)}")

    if base_seg == 0:
        frame = sub.parse_numeric(2)
        print(f"    Frame Number: 0x{frame:04X}")

    name = sub.parse_name()
    print(f"    Block Name: '{name}'")

    offset = sub.parse_numeric(2)
    print(f"    Offset: 0x{offset:04X}")

    if sub.bytes_remaining() > 0:
        debug_len = sub.parse_numeric(2)
        print(f"    Debug Info Length: {debug_len} bytes")
        if debug_len > 0 and sub.bytes_remaining() > 0:
            debug_data = sub.read_bytes(min(debug_len, sub.bytes_remaining()))
            print(f"    Debug Data: {format_hex_with_ascii(debug_data)}")


@omf_record(0x7C)
def handle_blkend(omf, record):
    """Handle BLKEND (7CH) - Block End."""
    print("  [Obsolete] Block End")
    print("    Closes a BLKDEF scope")


@omf_record(0x7E)
def handle_debsym(omf, record):
    """Handle DEBSYM (7EH) - Debug Symbols."""
    sub = omf.make_parser(record)
    print("  [Obsolete] Debug Symbols")
    print("    Local symbols including stack and based symbols")
    if sub.bytes_remaining() > 0:
        print(f"    Data: {format_hex_with_ascii(sub.data[sub.offset:])}")


@omf_record(0xA4)
def handle_libhed_obsolete(omf, record):
    """Handle LIBHED (A4H) - Obsolete Intel Library Header."""
    sub = omf.make_parser(record)
    print("  [Obsolete Intel] Library Header")
    print("    Note: Conflicts with MS EXESTR comment class")
    if sub.bytes_remaining() > 0:
        print(f"    Data: {format_hex_with_ascii(sub.data[sub.offset:])}")


@omf_record(0xA6)
def handle_libnam_obsolete(omf, record):
    """Handle LIBNAM (A6H) - Obsolete Intel Library Names."""
    sub = omf.make_parser(record)
    print("  [Obsolete Intel] Library Module Names")
    print("    Lists module names in sequence of appearance")
    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        if name:
            print(f"    Module: {name}")


@omf_record(0xA8)
def handle_libloc_obsolete(omf, record):
    """Handle LIBLOC (A8H) - Obsolete Intel Library Locations."""
    sub = omf.make_parser(record)
    print("  [Obsolete Intel] Library Module Locations")
    count = 0
    while sub.bytes_remaining() >= 4:
        location = sub.parse_numeric(4)
        print(f"    Module {count}: Offset 0x{location:08X}")
        count += 1


@omf_record(0xAA)
def handle_libdic_obsolete(omf, record):
    """Handle LIBDIC (AAH) - Obsolete Intel Library Dictionary."""
    sub = omf.make_parser(record)
    print("  [Obsolete Intel] Library Dictionary")
    print("    Public symbols grouped by defining module")
    if sub.bytes_remaining() > 0:
        print(f"    Data: {format_hex_with_ascii(sub.data[sub.offset:])}")
