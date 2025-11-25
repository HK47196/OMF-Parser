"""Microsoft extension record handlers."""

from . import omf_record
from ..constants import (
    RecordType, ComdefType, ComdatFlags,
    COMDAT_SELECTION_NAMES,
    COMDAT_ALLOCATION_NAMES,
    COMDAT_ALIGN_NAMES,
    BAKPAT_LOCATION_NAMES,
    COMDEF_BORLAND_MAX
)
from ..models import (
    ParsedComDef, ParsedComDat, ParsedBakPat, ParsedNBkPat,
    ParsedLinSym, ParsedAlias, ParsedLIDataBlock,
    ComDefFarDefinition, ComDefNearDefinition, ComDefBorlandDefinition, ComDefUnknownDefinition,
    BackpatchRecord, NamedBackpatchRecord, LineEntry, AliasEntry
)


def parse_lidata_blocks(sub, is_32bit):
    """Parse LIDATA-style iterated data blocks from a parser.

    Used by both LIDATA records and COMDAT records with iterated data flag.
    Returns tuple of (blocks list, warnings list).
    """
    blocks = []
    warnings = []
    truncated = False

    def parse_data_block(depth=0):
        nonlocal truncated
        repeat_size = sub.get_lidata_repeat_count_size(is_32bit)
        min_bytes = repeat_size + 2

        if sub.bytes_remaining() < min_bytes:
            if sub.bytes_remaining() > 0 and not truncated:
                warnings.append(
                    f"Truncated data block at depth {depth}: "
                    f"need {min_bytes} bytes, have {sub.bytes_remaining()}"
                )
                truncated = True
            return None

        repeat_count = sub.parse_numeric(repeat_size)
        block_count = sub.parse_numeric(2)

        block = ParsedLIDataBlock(
            repeat_count=repeat_count,
            block_count=block_count
        )

        if block_count == 0:
            content_len = sub.read_byte()
            if content_len is None:
                warnings.append(f"Missing content length byte at depth {depth}")
                return block
            if sub.bytes_remaining() < content_len:
                warnings.append(
                    f"Truncated content at depth {depth}: "
                    f"declared {content_len} bytes, have {sub.bytes_remaining()}"
                )
                content = sub.read_bytes(sub.bytes_remaining())
            else:
                content = sub.read_bytes(content_len)
            block.content = content if content else b''
        else:
            for i in range(block_count):
                nested = parse_data_block(depth + 1)
                if nested:
                    block.nested_blocks.append(nested)
                elif not truncated:
                    warnings.append(
                        f"Missing nested block {i+1}/{block_count} at depth {depth}"
                    )

        return block

    while sub.bytes_remaining() > 0:
        block = parse_data_block(depth=0)
        if block:
            block.calculate_expanded_size()
            blocks.append(block)
        else:
            break

    return blocks, warnings


@omf_record(RecordType.COMDEF, RecordType.LCOMDEF)
def handle_comdef(omf, record):
    """Handle COMDEF/LCOMDEF (B0H/B8H)."""
    sub = omf.make_parser(record)
    is_local = (record.type == RecordType.LCOMDEF)

    result = ParsedComDef(is_local=is_local)

    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        type_idx = sub.parse_index()
        data_type = sub.read_byte()

        if data_type is None:
            break

        if data_type == ComdefType.FAR:
            num_elements = sub.parse_variable_length_int()
            element_size = sub.parse_variable_length_int()
            total = num_elements * element_size
            defn = ComDefFarDefinition(
                name=name,
                type_index=type_idx,
                data_type=data_type,
                kind='FAR',
                num_elements=num_elements,
                element_size=element_size,
                total_size=total
            )
        elif data_type == ComdefType.NEAR:
            size = sub.parse_variable_length_int()
            defn = ComDefNearDefinition(
                name=name,
                type_index=type_idx,
                data_type=data_type,
                kind='NEAR',
                size=size
            )
        elif 0x01 <= data_type <= COMDEF_BORLAND_MAX:
            length = sub.parse_variable_length_int()
            defn = ComDefBorlandDefinition(
                name=name,
                type_index=type_idx,
                data_type=data_type,
                kind='Borland',
                seg_index=data_type,
                length=length
            )
        else:
            length = sub.parse_variable_length_int()
            defn = ComDefUnknownDefinition(
                name=name,
                type_index=type_idx,
                data_type=data_type,
                kind='Unknown',
                length=length
            )

        result.definitions.append(defn)
        omf.extdefs.append(name)

    return result


@omf_record(RecordType.COMDAT, RecordType.COMDAT32)
def handle_comdat(omf, record):
    """Handle COMDAT (C2H/C3H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.COMDAT32)

    flags = sub.read_byte()
    attrib = sub.read_byte()
    align = sub.read_byte()

    if flags is None or attrib is None or align is None:
        return None

    continuation = (flags & ComdatFlags.CONTINUATION) != 0
    iterated = (flags & ComdatFlags.ITERATED) != 0
    local = (flags & ComdatFlags.LOCAL) != 0
    data_in_code = (flags & ComdatFlags.DATA_IN_CODE) != 0

    selection = (attrib >> ComdatFlags.SELECTION_SHIFT) & ComdatFlags.SELECTION_MASK
    allocation = attrib & ComdatFlags.ALLOCATION_MASK

    result = ParsedComDat(
        is_32bit=is_32bit,
        flags=flags,
        continuation=continuation,
        iterated=iterated,
        local=local,
        data_in_code=data_in_code,
        attributes=attrib,
        selection=COMDAT_SELECTION_NAMES.get(selection, f'Reserved({selection})'),
        allocation=COMDAT_ALLOCATION_NAMES.get(allocation, f'Reserved({allocation})'),
        alignment=COMDAT_ALIGN_NAMES.get(align, f'Unknown({align})')
    )

    offset_size = sub.get_offset_field_size(is_32bit)
    result.enum_offset = sub.parse_numeric(offset_size)
    result.type_index = sub.parse_index()

    if allocation == 0:
        base_grp = sub.parse_index()
        base_seg = sub.parse_index()
        result.base_group = omf.get_grpdef(base_grp)
        result.base_segment = omf.get_segdef(base_seg)
        if base_seg == 0 and base_grp == 0:
            result.absolute_frame = sub.parse_numeric(2)

    if omf.variant.comdat_uses_inline_name():
        result.symbol = sub.parse_name()
    else:
        name_idx = sub.parse_index()
        result.symbol = omf.get_lname(name_idx)

    result.data_length = sub.bytes_remaining()

    if iterated and result.data_length > 0:
        blocks, _ = parse_lidata_blocks(sub, is_32bit)
        result.iterated_blocks = blocks
        result.iterated_expanded_size = sum(b.expanded_size for b in blocks)

    return result


@omf_record(RecordType.BAKPAT, RecordType.BAKPAT32)
def handle_bakpat(omf, record):
    """Handle BAKPAT (B2H/B3H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.BAKPAT32)

    result = ParsedBakPat(is_32bit=is_32bit)

    while sub.bytes_remaining() > 0:
        seg_idx = sub.parse_index()
        loc_type = sub.read_byte()

        loc_str = BAKPAT_LOCATION_NAMES.get(loc_type, f"Unknown({loc_type})")

        if loc_type == 2 and record.type == RecordType.BAKPAT:
            result.warnings.append("Location type 2 (DWord) only valid for B3H records")

        val_size = sub.get_offset_field_size(is_32bit)
        offset = sub.parse_numeric(val_size)
        value = sub.parse_numeric(val_size)

        result.records.append(BackpatchRecord(
            segment=omf.get_segdef(seg_idx),
            segment_index=seg_idx,
            location_type=loc_type,
            location_name=loc_str,
            offset=offset,
            value=value
        ))

    return result


@omf_record(RecordType.NBKPAT, RecordType.NBKPAT32)
def handle_nbkpat(omf, record):
    """Handle NBKPAT (C8H/C9H)."""
    sub = omf.make_parser(record)
    # NBKPAT has INVERTED bit order: C8H = 32-bit, C9H = 16-bit
    is_32bit = (record.type == RecordType.NBKPAT)

    result = ParsedNBkPat(is_32bit=is_32bit)

    loc_names = omf.variant.nbkpat_loc_names()

    while sub.bytes_remaining() > 0:
        loc_type = sub.read_byte()

        if omf.variant.nbkpat_uses_inline_name():
            symbol = sub.parse_name()
        else:
            name_idx = sub.parse_index()
            symbol = omf.get_lname(name_idx)

        loc_name = loc_names.get(loc_type, f"Unknown({loc_type})")

        val_size = sub.get_offset_field_size(is_32bit)
        offset = sub.parse_numeric(val_size)
        value = sub.parse_numeric(val_size)

        result.records.append(NamedBackpatchRecord(
            location_type=loc_type,
            location_name=loc_name,
            symbol=symbol,
            offset=offset,
            value=value
        ))

    return result


@omf_record(RecordType.LINSYM, RecordType.LINSYM32)
def handle_linsym(omf, record):
    """Handle LINSYM (C4H/C5H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.LINSYM32)

    flags = sub.read_byte()
    continuation = (flags & ComdatFlags.CONTINUATION) != 0

    if omf.variant.linsym_uses_inline_name():
        symbol = sub.parse_name()
    else:
        name_idx = sub.parse_index()
        symbol = omf.get_lname(name_idx)

    result = ParsedLinSym(
        is_32bit=is_32bit,
        continuation=continuation,
        symbol=symbol
    )

    while sub.bytes_remaining() > 0:
        line_num = sub.parse_numeric(2)
        offset_size = sub.get_offset_field_size(is_32bit)
        offset = sub.parse_numeric(offset_size)

        result.entries.append(LineEntry(
            line=line_num,
            offset=offset,
            is_end_of_function=(line_num == 0)
        ))

    return result


@omf_record(RecordType.ALIAS)
def handle_alias(omf, record):
    """Handle ALIAS (C6H)."""
    sub = omf.make_parser(record)

    result = ParsedAlias()

    while sub.bytes_remaining() > 0:
        alias_name = sub.parse_name()
        subst_name = sub.parse_name()
        result.aliases.append(AliasEntry(
            alias=alias_name,
            substitute=subst_name
        ))

    return result
