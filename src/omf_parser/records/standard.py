"""Standard OMF record handlers."""

from . import omf_record
from ..constants import (
    RecordType, GrpdefComponent, TypdefLeaf,
    SegdefFlags, ModendFlags, SegmentSize,
    RESERVED_SEGMENTS, ALIGN_NAMES, COMBINE_NAMES,
    KNOWN_VENDORS, VAR_TYPE_NAMES
)
from ..models import (
    ParsedTheadr, ParsedLNames, ParsedSegDef, ParsedGrpDef,
    ParsedPubDef, ParsedExtDef, ParsedCExtDef, ParsedModEnd,
    ParsedLinNum, ParsedVerNum, ParsedVendExt, ParsedLocSym, ParsedTypDef,
    PubDefSymbol, ExtDefEntry, CExtDefEntry, StartAddress, LineEntry,
    TypDefLeafNear, TypDefLeafFar, TypDefLeafUnknown
)


@omf_record(RecordType.THEADR, RecordType.LHEADR)
def handle_theadr(omf, record):
    """Handle THEADR (80H) and LHEADR (82H)."""
    omf.lnames = ["<null>"]
    omf.segdefs = ["<null>"]
    omf.grpdefs = ["<null>"]
    omf.extdefs = ["<null>"]
    omf.typdefs = ["<null>"]

    sub = omf.make_parser(record)
    name = sub.parse_name()
    rec_name = "THEADR" if record.type == RecordType.THEADR else "LHEADR"

    return ParsedTheadr(record_name=rec_name, module_name=name)


@omf_record(RecordType.LNAMES, RecordType.LLNAMES)
def handle_lnames(omf, record):
    """Handle LNAMES (96H) and LLNAMES (CAH)."""
    sub = omf.make_parser(record)
    rec_name = "LNAMES" if record.type == RecordType.LNAMES else "LLNAMES (Local)"
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


@omf_record(RecordType.SEGDEF, RecordType.SEGDEF32)
def handle_segdef(omf, record):
    """Handle SEGDEF (98H/99H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.SEGDEF32)

    acbp = sub.read_byte()
    if acbp is None:
        return None

    align = (acbp >> SegdefFlags.ALIGN_SHIFT) & SegdefFlags.ALIGN_MASK
    combine = (acbp >> SegdefFlags.COMBINE_SHIFT) & SegdefFlags.COMBINE_MASK
    big = (acbp >> 1) & SegdefFlags.BIG_MASK
    use32 = acbp & SegdefFlags.USE32_MASK

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
        big=bool(big),
        use32=bool(use32)
    )

    if align == 0:
        result.absolute_frame = sub.parse_numeric(2)
        result.absolute_offset = sub.read_byte()

    size_bytes = sub.get_offset_field_size(is_32bit)
    length = sub.parse_numeric(size_bytes)

    if big and length == 0:
        if is_32bit:
            result.length = SegmentSize.SIZE_4GB
            result.length_display = "4GB (0x100000000)"
        else:
            result.length = SegmentSize.SIZE_64K
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
            access_type = access_byte & SegdefFlags.ACCESS_TYPE_MASK
            access_names = omf.variant.segdef_access_byte_names()
            result.access_byte = access_byte
            result.access_name = access_names.get(access_type, f"Unknown({access_type})")
        else:
            result.extra_byte = sub.read_byte()

    raw_name = omf.lnames[seg_name_idx] if seg_name_idx < len(omf.lnames) else f"Seg#{len(omf.segdefs)}"
    omf.segdefs.append(raw_name)

    return result


@omf_record(RecordType.GRPDEF)
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

        if comp_type == GrpdefComponent.SEGMENT_INDEX:
            if sub.bytes_remaining() > 0:
                seg_idx = sub.parse_index()
                result.components.append(f"Seg:{omf.get_segdef(seg_idx)}")
            else:
                result.components.append("Seg:TRUNCATED")
                break
        elif comp_type == GrpdefComponent.EXTERNAL_INDEX:
            if sub.bytes_remaining() > 0:
                ext_idx = sub.parse_index()
                result.components.append(f"Ext:{omf.get_extdef(ext_idx)}")
            else:
                result.components.append("Ext:TRUNCATED")
                break
        elif comp_type == GrpdefComponent.SEGDEF_INDICES:
            if sub.bytes_remaining() >= 3:
                seg_name = sub.parse_index()
                cls_name = sub.parse_index()
                ovl_name = sub.parse_index()
                result.components.append(f"SegDef({seg_name},{cls_name},{ovl_name})")
            else:
                result.components.append("SegDef:TRUNCATED")
                break
        elif comp_type == GrpdefComponent.LTL:
            if sub.bytes_remaining() >= 5:
                ltl_data = sub.read_byte()
                max_len = sub.parse_numeric(2)
                grp_len = sub.parse_numeric(2)
                result.components.append(f"LTL(data=0x{ltl_data:02X},max={max_len},len={grp_len})")
            else:
                result.components.append("LTL:TRUNCATED")
                break
        elif comp_type == GrpdefComponent.ABSOLUTE:
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


@omf_record(RecordType.PUBDEF, RecordType.PUBDEF32, RecordType.LPUBDEF, RecordType.LPUBDEF32)
def handle_pubdef(omf, record):
    """Handle PUBDEF/LPUBDEF (90H/91H/B6H/B7H)."""
    sub = omf.make_parser(record)
    is_32bit = record.type in (RecordType.PUBDEF32, RecordType.LPUBDEF32)
    is_local = record.type in (RecordType.LPUBDEF, RecordType.LPUBDEF32)

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

        result.symbols.append(PubDefSymbol(
            name=name,
            offset=offset,
            type_index=type_idx
        ))

    return result


@omf_record(RecordType.EXTDEF, RecordType.LEXTDEF, RecordType.LEXTDEF2)
def handle_extdef(omf, record):
    """Handle EXTDEF/LEXTDEF (8CH/B4H/B5H)."""
    sub = omf.make_parser(record)
    is_local = record.type in (RecordType.LEXTDEF, RecordType.LEXTDEF2)

    result = ParsedExtDef(is_local=is_local)

    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        type_idx = sub.parse_index()

        idx = len(omf.extdefs)
        omf.extdefs.append(name)
        result.externals.append(ExtDefEntry(
            index=idx,
            name=name,
            type_index=type_idx
        ))

    return result


@omf_record(RecordType.CEXTDEF)
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
        result.externals.append(CExtDefEntry(
            index=idx,
            name=omf.get_lname(name_idx),
            type_index=type_idx
        ))

    return result


@omf_record(RecordType.MODEND, RecordType.MODEND32)
def handle_modend(omf, record):
    """Handle MODEND (8AH/8BH)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.MODEND32)

    mod_type = sub.read_byte()
    if mod_type is None:
        return None

    is_main = (mod_type & ModendFlags.MAIN) != 0
    has_start = (mod_type & ModendFlags.START) != 0
    is_relocatable = (mod_type & ModendFlags.RELOCATABLE) != 0

    result = ParsedModEnd(
        mod_type=mod_type,
        is_main=is_main,
        has_start=has_start,
        is_relocatable=is_relocatable
    )

    if has_start:
        end_data = sub.read_byte()
        if end_data is not None:
            frame_method = (end_data >> ModendFlags.FRAME_SHIFT) & ModendFlags.FRAME_MASK
            p_bit = (end_data >> ModendFlags.P_BIT_SHIFT) & 0x01
            target_method = end_data & ModendFlags.TARGET_MASK

            if p_bit != 0:
                result.warnings.append(f"MODEND P-bit is {p_bit}, must be 0 per spec")

            frame_datum = None
            if frame_method < 3:
                frame_datum = sub.parse_index()

            target_datum = sub.parse_index()

            target_displacement = None
            if p_bit == 0:
                disp_size = sub.get_offset_field_size(is_32bit)
                target_displacement = sub.parse_numeric(disp_size)

            result.start_address = StartAddress(
                frame_method=frame_method,
                p_bit=p_bit,
                target_method=target_method,
                frame_datum=frame_datum,
                target_datum=target_datum,
                target_displacement=target_displacement
            )

    return result


@omf_record(RecordType.LINNUM, RecordType.LINNUM32)
def handle_linnum(omf, record):
    """Handle LINNUM (94H/95H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.LINNUM32)

    base_grp = sub.parse_index()
    base_seg = sub.parse_index()

    result = ParsedLinNum(
        is_32bit=is_32bit,
        base_group=omf.get_grpdef(base_grp),
        base_segment=omf.get_segdef(base_seg)
    )

    offset_size = sub.get_offset_field_size(is_32bit)
    entry_size = 2 + offset_size

    while sub.bytes_remaining() >= entry_size:
        line_num = sub.parse_numeric(2)
        offset = sub.parse_numeric(offset_size)

        result.entries.append(LineEntry(
            line=line_num,
            offset=offset,
            is_end_of_function=(line_num == 0)
        ))

    if sub.bytes_remaining() > 0:
        result.warnings.append(f"Trailing {sub.bytes_remaining()} byte(s) in LINNUM record")

    return result


@omf_record(RecordType.VERNUM)
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


@omf_record(RecordType.VENDEXT)
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


@omf_record(RecordType.LOCSYM)
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
        result.symbols.append(PubDefSymbol(
            name=name,
            offset=offset,
            type_index=type_idx
        ))

    return result


@omf_record(RecordType.TYPDEF)
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

        if leaf_type == TypdefLeaf.NEAR:
            var_type = sub.read_byte()
            size_bits = sub.parse_variable_length_int()
            result.leaves.append(TypDefLeafNear(
                type='NEAR',
                leaf_type=leaf_type,
                var_type=VAR_TYPE_NAMES.get(var_type, f'0x{var_type:02X}'),
                var_type_raw=var_type,
                size_bits=size_bits,
                size_bytes=size_bits // 8
            ))

        elif leaf_type == TypdefLeaf.FAR:
            var_type = sub.read_byte()
            num_elements = sub.parse_variable_length_int()
            element_type_idx = sub.parse_index()
            result.leaves.append(TypDefLeafFar(
                type='FAR',
                leaf_type=leaf_type,
                num_elements=num_elements,
                element_type=omf.get_typdef(element_type_idx),
                element_type_index=element_type_idx
            ))

        else:
            result.leaves.append(TypDefLeafUnknown(
                type='Unknown',
                leaf_type=leaf_type,
                remaining=sub.data[sub.offset:]
            ))

    else:
        result.format = "Intel"

        for leaf_idx in range(en_byte):
            if sub.bytes_remaining() == 0:
                break

            leaf_type = sub.read_byte()

            if leaf_type == TypdefLeaf.NEAR:
                var_type = sub.read_byte()
                size_bits = sub.parse_variable_length_int()
                result.leaves.append(TypDefLeafNear(
                    type='NEAR',
                    leaf_index=leaf_idx + 1,
                    leaf_type=leaf_type,
                    var_type=VAR_TYPE_NAMES.get(var_type, f'0x{var_type:02X}'),
                    var_type_raw=var_type,
                    size_bits=size_bits,
                    size_bytes=size_bits // 8
                ))

            elif leaf_type == TypdefLeaf.FAR:
                var_type = sub.read_byte()
                num_elements = sub.parse_variable_length_int()
                element_type_idx = sub.parse_index()
                result.leaves.append(TypDefLeafFar(
                    type='FAR',
                    leaf_index=leaf_idx + 1,
                    leaf_type=leaf_type,
                    num_elements=num_elements,
                    element_type=omf.get_typdef(element_type_idx),
                    element_type_index=element_type_idx
                ))

            else:
                remaining = sub.data[sub.offset:sub.offset + 16]
                result.leaves.append(TypDefLeafUnknown(
                    type='Unknown',
                    leaf_index=leaf_idx + 1,
                    leaf_type=leaf_type,
                    remaining=remaining
                ))

    omf.typdefs.append(f"TYPDEF#{len(omf.typdefs)}")

    return result
