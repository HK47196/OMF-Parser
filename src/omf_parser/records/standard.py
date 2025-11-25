"""Standard OMF record handlers."""

from . import omf_record
from ..constants import (
    RESERVED_SEGMENTS, ALIGN_NAMES, COMBINE_NAMES,
    KNOWN_VENDORS, VAR_TYPE_NAMES
)
from ..models import (
    ParsedTheadr, ParsedLNames, ParsedSegDef, ParsedGrpDef,
    ParsedPubDef, ParsedExtDef, ParsedCExtDef, ParsedModEnd,
    ParsedLinNum, ParsedVerNum, ParsedVendExt, ParsedLocSym, ParsedTypDef
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

    return ParsedTheadr(record_name=rec_name, module_name=name)


@omf_record(0x96, 0xCA)
def handle_lnames(omf, record):
    """Handle LNAMES (96H) and LLNAMES (CAH)."""
    sub = omf.make_parser(record)
    rec_name = "LNAMES" if record.type == 0x96 else "LLNAMES (Local)"
    start_idx = len(omf.lnames)

    names = []
    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        omf.lnames.append(name)
        idx = len(omf.lnames) - 1
        is_reserved = name in RESERVED_SEGMENTS
        names.append((idx, name, is_reserved))

    end_idx = len(omf.lnames) - 1

    return ParsedLNames(
        record_name=rec_name,
        start_index=start_idx,
        end_index=end_idx,
        names=names
    )


@omf_record(0x98, 0x99)
def handle_segdef(omf, record):
    """Handle SEGDEF (98H/99H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == 0x99)

    acbp = sub.read_byte()
    if acbp is None:
        return None

    align = (acbp >> 5) & 0x07
    combine = (acbp >> 2) & 0x07
    big = (acbp >> 1) & 0x01
    use32 = acbp & 0x01

    extra_align_names = omf.variant.segdef_extra_align_names()
    if align in extra_align_names:
        align_name = extra_align_names[align]
    elif align < len(ALIGN_NAMES):
        align_name = ALIGN_NAMES[align]
    else:
        align_name = f"Unknown({align})"

    result = ParsedSegDef(
        acbp=acbp,
        alignment=align_name,
        align_value=align,
        combine=COMBINE_NAMES[combine],
        big=big,
        use32=use32
    )

    if align == 0:
        result.absolute_frame = sub.parse_numeric(2)
        result.absolute_offset = sub.read_byte()

    size_bytes = sub.get_offset_field_size(is_32bit)
    length = sub.parse_numeric(size_bytes)

    if big and length == 0:
        if is_32bit:
            result.length = 0x100000000
            result.length_display = "4GB (0x100000000)"
        else:
            result.length = 0x10000
            result.length_display = "64K (0x10000)"
    else:
        result.length = length
        result.length_display = f"{length} (0x{length:X})"

    seg_name_idx = sub.parse_index()
    cls_name_idx = sub.parse_index()
    ovl_name_idx = sub.parse_index()

    result.segment_name = omf.get_lname(seg_name_idx)
    result.class_name = omf.get_lname(cls_name_idx)
    result.overlay_name = omf.get_lname(ovl_name_idx)

    if sub.bytes_remaining() >= 1:
        if omf.variant.segdef_has_access_byte():
            access_byte = sub.read_byte()
            access_type = access_byte & 0x03
            access_names = omf.variant.segdef_access_byte_names()
            result.access_byte = access_byte
            result.access_name = access_names.get(access_type, f"Unknown({access_type})")
        else:
            result.extra_byte = sub.read_byte()

    raw_name = omf.lnames[seg_name_idx] if seg_name_idx < len(omf.lnames) else f"Seg#{len(omf.segdefs)}"
    omf.segdefs.append(raw_name)

    return result


@omf_record(0x9A)
def handle_grpdef(omf, record):
    """Handle GRPDEF (9AH)."""
    sub = omf.make_parser(record)
    name_idx = sub.parse_index()
    name = omf.get_lname(name_idx)

    raw_name = omf.lnames[name_idx] if name_idx < len(omf.lnames) else ""

    result = ParsedGrpDef(
        name=name,
        name_index=name_idx,
        is_flat=(raw_name == "FLAT")
    )

    while sub.bytes_remaining() > 0:
        comp_type = sub.read_byte()
        if comp_type is None:
            break

        if comp_type == 0xFF:
            if sub.bytes_remaining() > 0:
                seg_idx = sub.parse_index()
                result.components.append(f"Seg:{omf.get_segdef(seg_idx)}")
            else:
                result.components.append("Seg:TRUNCATED")
                break
        elif comp_type == 0xFE:
            if sub.bytes_remaining() > 0:
                ext_idx = sub.parse_index()
                result.components.append(f"Ext:{omf.get_extdef(ext_idx)}")
            else:
                result.components.append("Ext:TRUNCATED")
                break
        elif comp_type == 0xFD:
            if sub.bytes_remaining() >= 3:
                seg_name = sub.parse_index()
                cls_name = sub.parse_index()
                ovl_name = sub.parse_index()
                result.components.append(f"SegDef({seg_name},{cls_name},{ovl_name})")
            else:
                result.components.append("SegDef:TRUNCATED")
                break
        elif comp_type == 0xFB:
            if sub.bytes_remaining() >= 5:
                ltl_data = sub.read_byte()
                max_len = sub.parse_numeric(2)
                grp_len = sub.parse_numeric(2)
                result.components.append(f"LTL(data=0x{ltl_data:02X},max={max_len},len={grp_len})")
            else:
                result.components.append("LTL:TRUNCATED")
                break
        elif comp_type == 0xFA:
            if sub.bytes_remaining() >= 3:
                frame = sub.parse_numeric(2)
                offset = sub.read_byte()
                result.components.append(f"Abs({frame:04X}:{offset:02X})")
            else:
                result.components.append("Abs:TRUNCATED")
                break
        else:
            result.components.append(f"Unknown({comp_type:02X})")
            result.warnings.append(f"Unknown GRPDEF component type 0x{comp_type:02X}")
            break

    omf.grpdefs.append(raw_name)

    return result


@omf_record(0x90, 0x91, 0xB6, 0xB7)
def handle_pubdef(omf, record):
    """Handle PUBDEF/LPUBDEF (90H/91H/B6H/B7H)."""
    sub = omf.make_parser(record)
    is_32bit = record.type in [0x91, 0xB7]
    is_local = record.type in [0xB6, 0xB7]

    base_grp = sub.parse_index()
    base_seg = sub.parse_index()

    result = ParsedPubDef(
        is_32bit=is_32bit,
        is_local=is_local,
        base_group=omf.get_grpdef(base_grp),
        base_segment=omf.get_segdef(base_seg)
    )

    if base_seg == 0:
        result.absolute_frame = sub.parse_numeric(2)
        if base_grp != 0:
            result.frame_note = "Frame ignored by linker when Base Group != 0"

    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        if not name and sub.bytes_remaining() == 0:
            break

        offset_size = sub.get_offset_field_size(is_32bit)
        offset = sub.parse_numeric(offset_size)
        type_idx = sub.parse_index()

        result.symbols.append({
            'name': name,
            'offset': offset,
            'type_index': type_idx
        })

    return result


@omf_record(0x8C, 0xB4, 0xB5)
def handle_extdef(omf, record):
    """Handle EXTDEF/LEXTDEF (8CH/B4H/B5H)."""
    sub = omf.make_parser(record)
    is_local = record.type in [0xB4, 0xB5]

    result = ParsedExtDef(is_local=is_local)

    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        type_idx = sub.parse_index()

        idx = len(omf.extdefs)
        omf.extdefs.append(name)
        result.externals.append({
            'index': idx,
            'name': name,
            'type_index': type_idx
        })

    return result


@omf_record(0xBC)
def handle_cextdef(omf, record):
    """Handle CEXTDEF (BCH)."""
    sub = omf.make_parser(record)

    result = ParsedCExtDef()

    while sub.bytes_remaining() > 0:
        name_idx = sub.parse_index()
        type_idx = sub.parse_index()

        name = omf.lnames[name_idx] if name_idx < len(omf.lnames) else f"LName#{name_idx}"
        idx = len(omf.extdefs)
        omf.extdefs.append(name)
        result.externals.append({
            'index': idx,
            'name': omf.get_lname(name_idx),
            'type_index': type_idx
        })

    return result


@omf_record(0x8A, 0x8B)
def handle_modend(omf, record):
    """Handle MODEND (8AH/8BH)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == 0x8B)

    mod_type = sub.read_byte()
    if mod_type is None:
        return None

    is_main = (mod_type & 0x80) != 0
    has_start = (mod_type & 0x40) != 0
    is_relocatable = (mod_type & 0x01) != 0

    result = ParsedModEnd(
        mod_type=mod_type,
        is_main=is_main,
        has_start=has_start,
        is_relocatable=is_relocatable
    )

    if has_start:
        end_data = sub.read_byte()
        if end_data is not None:
            frame_method = (end_data >> 4) & 0x07
            p_bit = (end_data >> 2) & 0x01
            target_method = end_data & 0x03

            start_addr = {
                'frame_method': frame_method,
                'p_bit': p_bit,
                'target_method': target_method
            }

            if p_bit != 0:
                result.warnings.append(f"MODEND P-bit is {p_bit}, must be 0 per spec")

            if frame_method < 3:
                start_addr['frame_datum'] = sub.parse_index()

            start_addr['target_datum'] = sub.parse_index()

            if p_bit == 0:
                disp_size = sub.get_offset_field_size(is_32bit)
                start_addr['target_displacement'] = sub.parse_numeric(disp_size)

            result.start_address = start_addr

    return result


@omf_record(0x94, 0x95)
def handle_linnum(omf, record):
    """Handle LINNUM (94H/95H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == 0x95)

    base_grp = sub.parse_index()
    base_seg = sub.parse_index()

    result = ParsedLinNum(
        is_32bit=is_32bit,
        base_group=omf.get_grpdef(base_grp),
        base_segment=omf.get_segdef(base_seg)
    )

    while sub.bytes_remaining() > 0:
        line_num = sub.parse_numeric(2)
        offset_size = sub.get_offset_field_size(is_32bit)
        offset = sub.parse_numeric(offset_size)

        result.entries.append({
            'line': line_num,
            'offset': offset,
            'is_end_of_function': (line_num == 0)
        })

    return result


@omf_record(0xCC)
def handle_vernum(omf, record):
    """Handle VERNUM (CCH)."""
    sub = omf.make_parser(record)
    version = sub.parse_name()

    result = ParsedVerNum(version=version)

    parts = version.split('.')
    if len(parts) >= 3:
        result.tis_base = parts[0]
        result.vendor_num = parts[1]
        result.vendor_ver = parts[2]

        try:
            vendor_int = int(parts[1])
            if vendor_int != 0:
                vendor_name = KNOWN_VENDORS.get(vendor_int, "Unknown")
                result.vendor_name = vendor_name
                result.warnings.append(f"Non-TIS vendor extensions present (vendor {vendor_int}: {vendor_name})")
        except ValueError:
            pass

    return result


@omf_record(0xCE)
def handle_vendext(omf, record):
    """Handle VENDEXT (CEH)."""
    sub = omf.make_parser(record)
    vendor_num = sub.parse_numeric(2)

    result = ParsedVendExt(vendor_num=vendor_num)
    result.vendor_name = KNOWN_VENDORS.get(vendor_num)

    if result.vendor_name is None:
        result.warnings.append("Unrecognized vendor number")

    if sub.bytes_remaining() > 0:
        result.extension_data = sub.data[sub.offset:]

    return result


@omf_record(0x92)
def handle_locsym(omf, record):
    """Handle LOCSYM (92H) - Local Symbols."""
    sub = omf.make_parser(record)

    base_grp = sub.parse_index()
    base_seg = sub.parse_index()

    result = ParsedLocSym(
        base_group=omf.get_grpdef(base_grp),
        base_segment=omf.get_segdef(base_seg)
    )

    if base_seg == 0:
        result.absolute_frame = sub.parse_numeric(2)
        if base_grp != 0:
            result.frame_note = "Frame ignored by linker when Base Group != 0"

    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        offset = sub.parse_numeric(2)
        type_idx = sub.parse_index()
        result.symbols.append({
            'name': name,
            'offset': offset,
            'type_index': type_idx
        })

    return result


@omf_record(0x8E)
def handle_typdef(omf, record):
    """Handle TYPDEF (8EH)."""
    sub = omf.make_parser(record)

    name = sub.parse_name()
    en_byte = sub.read_byte()

    result = ParsedTypDef(name=name if name else None, en_byte=en_byte)

    if en_byte == 0:
        result.format = "Microsoft"
        if sub.bytes_remaining() == 0:
            omf.typdefs.append(f"TYPDEF#{len(omf.typdefs)}")
            return result

        leaf_type = sub.read_byte()

        if leaf_type == 0x62:
            var_type = sub.read_byte()
            size_bits = sub.parse_variable_length_int()
            result.leaves.append({
                'type': 'NEAR',
                'leaf_type': leaf_type,
                'var_type': VAR_TYPE_NAMES.get(var_type, f'0x{var_type:02X}'),
                'var_type_raw': var_type,
                'size_bits': size_bits,
                'size_bytes': size_bits // 8
            })

        elif leaf_type == 0x61:
            var_type = sub.read_byte()
            num_elements = sub.parse_variable_length_int()
            element_type_idx = sub.parse_index()
            result.leaves.append({
                'type': 'FAR',
                'leaf_type': leaf_type,
                'num_elements': num_elements,
                'element_type': omf.get_typdef(element_type_idx),
                'element_type_index': element_type_idx
            })

        else:
            result.leaves.append({
                'type': 'Unknown',
                'leaf_type': leaf_type,
                'remaining': sub.data[sub.offset:]
            })

    else:
        result.format = "Intel"

        for leaf_idx in range(en_byte):
            if sub.bytes_remaining() == 0:
                break

            leaf_type = sub.read_byte()

            if leaf_type == 0x62:
                var_type = sub.read_byte()
                size_bits = sub.parse_variable_length_int()
                result.leaves.append({
                    'type': 'NEAR',
                    'leaf_index': leaf_idx + 1,
                    'leaf_type': leaf_type,
                    'var_type': VAR_TYPE_NAMES.get(var_type, f'0x{var_type:02X}'),
                    'var_type_raw': var_type,
                    'size_bits': size_bits,
                    'size_bytes': size_bits // 8
                })

            elif leaf_type == 0x61:
                var_type = sub.read_byte()
                num_elements = sub.parse_variable_length_int()
                element_type_idx = sub.parse_index()
                result.leaves.append({
                    'type': 'FAR',
                    'leaf_index': leaf_idx + 1,
                    'leaf_type': leaf_type,
                    'num_elements': num_elements,
                    'element_type': omf.get_typdef(element_type_idx),
                    'element_type_index': element_type_idx
                })

            else:
                remaining = sub.data[sub.offset:sub.offset + 16]
                result.leaves.append({
                    'type': 'Unknown',
                    'leaf_index': leaf_idx + 1,
                    'leaf_type': leaf_type,
                    'remaining': remaining
                })

    omf.typdefs.append(f"TYPDEF#{len(omf.typdefs)}")

    return result
