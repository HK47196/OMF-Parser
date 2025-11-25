"""Standard OMF record handlers."""

from . import omf_record
from ..parsing import format_hex_with_ascii
from ..constants import (
    RESERVED_SEGMENTS, ALIGN_NAMES, COMBINE_NAMES,
    KNOWN_VENDORS, VAR_TYPE_NAMES
)


@omf_record(0x80, 0x82)
def handle_theadr(omf, record):
    """Handle THEADR (80H) and LHEADR (82H)."""
    omf.lnames = ["<null>"]
    omf.segdefs = ["<null>"]
    omf.grpdefs = ["<null>"]
    omf.extdefs = ["<null>"]
    omf.typdefs = ["<null>"]

    sub = omf.make_parser(record)
    name = sub.parse_name()
    rec_name = "THEADR" if record.type == 0x80 else "LHEADR"
    print(f"  {rec_name} Module: '{name}'")


@omf_record(0x96, 0xCA)
def handle_lnames(omf, record):
    """Handle LNAMES (96H) and LLNAMES (CAH)."""
    sub = omf.make_parser(record)
    rec_name = "LNAMES" if record.type == 0x96 else "LLNAMES (Local)"
    start_idx = len(omf.lnames)

    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        omf.lnames.append(name)

    end_idx = len(omf.lnames) - 1
    print(f"  {rec_name}: Added indices {start_idx} to {end_idx}")
    for i in range(start_idx, len(omf.lnames)):
        marker = " [RESERVED]" if omf.lnames[i] in RESERVED_SEGMENTS else ""
        print(f"    [{i}] '{omf.lnames[i]}'{marker}")


@omf_record(0x98, 0x99)
def handle_segdef(omf, record):
    """Handle SEGDEF (98H/99H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == 0x99)

    acbp = sub.read_byte()
    if acbp is None:
        return

    align = (acbp >> 5) & 0x07
    combine = (acbp >> 2) & 0x07
    big = (acbp >> 1) & 0x01
    use32 = acbp & 0x01

    # Get alignment name, checking variant-specific names first
    extra_align_names = omf.variant.segdef_extra_align_names()
    if align in extra_align_names:
        align_name = extra_align_names[align]
    elif align < len(ALIGN_NAMES):
        align_name = ALIGN_NAMES[align]
    else:
        align_name = f"Unknown({align})"

    print(f"  ACBP: 0x{acbp:02X}")
    print(f"    Alignment: {align_name}")
    print(f"    Combine: {COMBINE_NAMES[combine]}")
    print(f"    Big: {big} (segment is {'64K/4GB' if big else 'smaller'})")
    print(f"    Use32: {use32} ({'Use32' if use32 else 'Use16'})")

    if align == 0:
        frame_num = sub.parse_numeric(2)
        frame_offset = sub.read_byte()
        print(f"    Absolute Frame: 0x{frame_num:04X}, Offset: 0x{frame_offset:02X}")

    size_bytes = sub.get_offset_field_size(is_32bit)
    length = sub.parse_numeric(size_bytes)

    if big and length == 0:
        if is_32bit:
            print(f"    Length: 4GB (0x100000000)")
        else:
            print(f"    Length: 64K (0x10000)")
    else:
        print(f"    Length: {length} (0x{length:X})")

    seg_name_idx = sub.parse_index()
    cls_name_idx = sub.parse_index()
    ovl_name_idx = sub.parse_index()

    seg_name = omf.get_lname(seg_name_idx)
    cls_name = omf.get_lname(cls_name_idx)
    ovl_name = omf.get_lname(ovl_name_idx)

    print(f"    Segment Name: {seg_name}")
    print(f"    Class Name: {cls_name}")
    print(f"    Overlay Name: {ovl_name}")

    # Check for PharLap access byte
    if sub.bytes_remaining() >= 1:
        if omf.variant.segdef_has_access_byte():
            access_byte = sub.read_byte()
            access_type = access_byte & 0x03
            access_names = omf.variant.segdef_access_byte_names()
            access_name = access_names.get(access_type, f"Unknown({access_type})")
            print(f"    Access: 0x{access_byte:02X} ({access_name})")
        else:
            extra_byte = sub.read_byte()
            print(f"    [Unknown] Extra byte: 0x{extra_byte:02X}")

    raw_name = omf.lnames[seg_name_idx] if seg_name_idx < len(omf.lnames) else f"Seg#{len(omf.segdefs)}"
    omf.segdefs.append(raw_name)


@omf_record(0x9A)
def handle_grpdef(omf, record):
    """Handle GRPDEF (9AH)."""
    sub = omf.make_parser(record)
    name_idx = sub.parse_index()
    name = omf.get_lname(name_idx)

    print(f"  Group Name: {name}")

    raw_name = omf.lnames[name_idx] if name_idx < len(omf.lnames) else ""
    if raw_name == "FLAT":
        print("    [Special] FLAT pseudo-group - Virtual Zero Address")

    components = []
    while sub.bytes_remaining() > 0:
        comp_type = sub.read_byte()
        if comp_type is None:
            break

        if comp_type == 0xFF:
            if sub.bytes_remaining() > 0:
                seg_idx = sub.parse_index()
                components.append(f"Seg:{omf.get_segdef(seg_idx)}")
            else:
                components.append("Seg:TRUNCATED")
                break
        elif comp_type == 0xFE:
            if sub.bytes_remaining() > 0:
                ext_idx = sub.parse_index()
                components.append(f"Ext:{omf.get_extdef(ext_idx)}")
            else:
                components.append("Ext:TRUNCATED")
                break
        elif comp_type == 0xFD:
            if sub.bytes_remaining() >= 3:
                seg_name = sub.parse_index()
                cls_name = sub.parse_index()
                ovl_name = sub.parse_index()
                components.append(f"SegDef({seg_name},{cls_name},{ovl_name})")
            else:
                components.append("SegDef:TRUNCATED")
                break
        elif comp_type == 0xFB:
            if sub.bytes_remaining() >= 5:
                ltl_data = sub.read_byte()
                max_len = sub.parse_numeric(2)
                grp_len = sub.parse_numeric(2)
                components.append(f"LTL(data=0x{ltl_data:02X},max={max_len},len={grp_len})")
            else:
                components.append("LTL:TRUNCATED")
                break
        elif comp_type == 0xFA:
            if sub.bytes_remaining() >= 3:
                frame = sub.parse_numeric(2)
                offset = sub.read_byte()
                components.append(f"Abs({frame:04X}:{offset:02X})")
            else:
                components.append("Abs:TRUNCATED")
                break
        else:
            components.append(f"Unknown({comp_type:02X})")
            omf.add_warning(f"    [!] WARNING: Unknown GRPDEF component type 0x{comp_type:02X}")
            break

    for comp in components:
        print(f"    Component: {comp}")

    omf.grpdefs.append(raw_name)


@omf_record(0x90, 0x91, 0xB6, 0xB7)
def handle_pubdef(omf, record):
    """Handle PUBDEF/LPUBDEF (90H/91H/B6H/B7H)."""
    sub = omf.make_parser(record)
    is_32bit = record.type in [0x91, 0xB7]
    is_local = record.type in [0xB6, 0xB7]

    print(f"  {'Local ' if is_local else ''}Public Definitions ({'32-bit' if is_32bit else '16-bit'}):")

    base_grp = sub.parse_index()
    base_seg = sub.parse_index()

    print(f"    Base Group: {omf.get_grpdef(base_grp)}")
    print(f"    Base Segment: {omf.get_segdef(base_seg)}")

    if base_seg == 0:
        frame = sub.parse_numeric(2)
        print(f"    Absolute Frame: 0x{frame:04X}")
        if base_grp != 0:
            print(f"    [Note] Frame ignored by linker when Base Group != 0")

    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        if not name and sub.bytes_remaining() == 0:
            break

        offset_size = sub.get_offset_field_size(is_32bit)
        offset = sub.parse_numeric(offset_size)
        type_idx = sub.parse_index()

        print(f"    Symbol: '{name}' Offset=0x{offset:X} Type={type_idx}")


@omf_record(0x8C, 0xB4, 0xB5)
def handle_extdef(omf, record):
    """Handle EXTDEF/LEXTDEF (8CH/B4H/B5H)."""
    sub = omf.make_parser(record)
    is_local = record.type in [0xB4, 0xB5]

    print(f"  {'Local ' if is_local else ''}External Definitions:")

    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        type_idx = sub.parse_index()

        idx = len(omf.extdefs)
        omf.extdefs.append(name)
        print(f"    [{idx}] '{name}' Type={type_idx}")


@omf_record(0xBC)
def handle_cextdef(omf, record):
    """Handle CEXTDEF (BCH)."""
    sub = omf.make_parser(record)
    print("  COMDAT External Definitions:")

    while sub.bytes_remaining() > 0:
        name_idx = sub.parse_index()
        type_idx = sub.parse_index()

        name = omf.lnames[name_idx] if name_idx < len(omf.lnames) else f"LName#{name_idx}"
        idx = len(omf.extdefs)
        omf.extdefs.append(name)
        print(f"    [{idx}] {omf.get_lname(name_idx)} Type={type_idx}")


@omf_record(0x8A, 0x8B)
def handle_modend(omf, record):
    """Handle MODEND (8AH/8BH)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == 0x8B)

    mod_type = sub.read_byte()
    if mod_type is None:
        return

    is_main = (mod_type & 0x80) != 0
    has_start = (mod_type & 0x40) != 0
    is_relocatable = (mod_type & 0x01) != 0

    print(f"  Module Type: 0x{mod_type:02X}")
    print(f"    Main Module: {is_main}")
    print(f"    Has Start Address: {has_start}")
    print(f"    Relocatable Start: {is_relocatable}")

    if has_start:
        print("  Start Address:")
        end_data = sub.read_byte()
        if end_data is not None:
            frame_method = (end_data >> 4) & 0x07
            p_bit = (end_data >> 2) & 0x01
            target_method = end_data & 0x03

            if p_bit != 0:
                omf.add_warning(f"    [!] WARNING: MODEND P-bit is {p_bit}, must be 0 per spec")

            if frame_method < 3:
                frame_datum = sub.parse_index()
                print(f"    Frame Method: {frame_method}, Datum: {frame_datum}")
            else:
                print(f"    Frame Method: {frame_method}")

            target_datum = sub.parse_index()
            print(f"    Target Method: {target_method}, Datum: {target_datum}")

            if p_bit == 0:
                disp_size = sub.get_offset_field_size(is_32bit)
                disp = sub.parse_numeric(disp_size)
                print(f"    Target Displacement: 0x{disp:X}")


@omf_record(0x94, 0x95)
def handle_linnum(omf, record):
    """Handle LINNUM (94H/95H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == 0x95)

    base_grp = sub.parse_index()
    base_seg = sub.parse_index()

    print(f"  Base Group: {omf.get_grpdef(base_grp)}")
    print(f"  Base Segment: {omf.get_segdef(base_seg)}")
    print("  Line Number Entries:")

    while sub.bytes_remaining() > 0:
        line_num = sub.parse_numeric(2)
        offset_size = sub.get_offset_field_size(is_32bit)
        offset = sub.parse_numeric(offset_size)

        if line_num == 0:
            print(f"    Line 0 (end of function): Offset=0x{offset:X}")
        else:
            print(f"    Line {line_num}: Offset=0x{offset:X}")


@omf_record(0xCC)
def handle_vernum(omf, record):
    """Handle VERNUM (CCH)."""
    sub = omf.make_parser(record)
    version = sub.parse_name()
    print(f"  OMF Version: {version}")

    parts = version.split('.')
    if len(parts) >= 3:
        tis_base = parts[0]
        vendor_num = parts[1]
        vendor_ver = parts[2]

        print(f"    TIS Base Version: {tis_base}")
        print(f"    Vendor Number: {vendor_num}")
        print(f"    Vendor Version: {vendor_ver}")

        try:
            vendor_int = int(vendor_num)
            if vendor_int != 0:
                vendor_name = KNOWN_VENDORS.get(vendor_int, "Unknown")
                omf.add_warning(f"    [!] WARNING: Non-TIS vendor extensions present (vendor {vendor_int}: {vendor_name})")
        except ValueError:
            pass


@omf_record(0xCE)
def handle_vendext(omf, record):
    """Handle VENDEXT (CEH)."""
    sub = omf.make_parser(record)
    vendor_num = sub.parse_numeric(2)

    vendor_name = KNOWN_VENDORS.get(vendor_num)
    if vendor_name:
        print(f"  Vendor Number: {vendor_num} ({vendor_name})")
    else:
        print(f"  Vendor Number: {vendor_num}")
        omf.add_warning(f"  [!] WARNING: Unrecognized vendor number")

    if sub.bytes_remaining() > 0:
        print(f"  Extension Data: {format_hex_with_ascii(sub.data[sub.offset:])}")


@omf_record(0x92)
def handle_locsym(omf, record):
    """Handle LOCSYM (92H) - Local Symbols."""
    sub = omf.make_parser(record)
    print("  [Obsolete] Local Symbols (same format as PUBDEF)")

    base_grp = sub.parse_index()
    base_seg = sub.parse_index()
    print(f"    Base Group: {omf.get_grpdef(base_grp)}")
    print(f"    Base Segment: {omf.get_segdef(base_seg)}")

    if base_seg == 0:
        frame = sub.parse_numeric(2)
        print(f"    Absolute Frame: 0x{frame:04X}")
        if base_grp != 0:
            print(f"    [Note] Frame ignored by linker when Base Group != 0")

    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        offset = sub.parse_numeric(2)
        type_idx = sub.parse_index()
        print(f"    '{name}' Offset=0x{offset:X} Type={type_idx}")


@omf_record(0x8E)
def handle_typdef(omf, record):
    """Handle TYPDEF (8EH)."""
    sub = omf.make_parser(record)

    name = sub.parse_name()
    en_byte = sub.read_byte()

    print(f"  [Obsolete TYPDEF]")
    if name:
        print(f"  Name (ignored): '{name}'")

    print(f"  EN Byte: {en_byte}")

    if en_byte == 0:
        print(f"  Format: Microsoft (stripped)")
        if sub.bytes_remaining() == 0:
            omf.typdefs.append(f"TYPDEF#{len(omf.typdefs)}")
            return

        leaf_type = sub.read_byte()

        if leaf_type == 0x62:
            var_type = sub.read_byte()
            size_bits = sub.parse_variable_length_int()
            print(f"  NEAR Variable")
            print(f"    Type: {VAR_TYPE_NAMES.get(var_type, f'0x{var_type:02X}')}")
            print(f"    Size: {size_bits} bits ({size_bits // 8} bytes)")

        elif leaf_type == 0x61:
            var_type = sub.read_byte()
            num_elements = sub.parse_variable_length_int()
            element_type_idx = sub.parse_index()
            print(f"  FAR Variable (Array)")
            print(f"    Num Elements: {num_elements}")
            print(f"    Element Type: {omf.get_typdef(element_type_idx)}")

        else:
            print(f"  Unknown Leaf Type: 0x{leaf_type:02X}")
            print(f"  Remaining: {format_hex_with_ascii(sub.data[sub.offset:])}")

    else:
        print(f"  Format: Intel (Eight-Leaf Descriptor)")
        print(f"  Number of leaf descriptors: {en_byte}")

        for leaf_idx in range(en_byte):
            if sub.bytes_remaining() == 0:
                break

            print(f"  Leaf {leaf_idx + 1}:")
            leaf_type = sub.read_byte()

            if leaf_type == 0x62:
                var_type = sub.read_byte()
                size_bits = sub.parse_variable_length_int()
                print(f"    NEAR Variable")
                print(f"      Type: {VAR_TYPE_NAMES.get(var_type, f'0x{var_type:02X}')}")
                print(f"      Size: {size_bits} bits ({size_bits // 8} bytes)")

            elif leaf_type == 0x61:
                var_type = sub.read_byte()
                num_elements = sub.parse_variable_length_int()
                element_type_idx = sub.parse_index()
                print(f"    FAR Variable (Array)")
                print(f"      Num Elements: {num_elements}")
                print(f"      Element Type: {omf.get_typdef(element_type_idx)}")

            else:
                print(f"    Unknown Leaf Type: 0x{leaf_type:02X}")
                remaining = sub.data[sub.offset:sub.offset + 16]
                print(f"    Remaining: {format_hex_with_ascii(remaining)}")

    omf.typdefs.append(f"TYPDEF#{len(omf.typdefs)}")
