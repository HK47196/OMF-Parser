"""COMDAT record handler."""

from . import omf_record
from .lidata import parse_lidata_blocks
from ..constants import (
    RecordType, ComdatFlags, ComdatSelection, ComdatAllocation, ComdatAlign
)
from ..models import ParsedComDat
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.COMDAT, RecordType.COMDAT32)
def handle_comdat(omf: OMFFileProtocol, record: RecordInfo) -> ParsedComDat | None:
    """Handle COMDAT (C2H/C3H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.COMDAT32)

    flags = sub.read_byte()
    attrib = sub.read_byte()
    align_val = sub.read_byte()

    if flags is None or attrib is None or align_val is None:
        return None

    continuation = (flags & ComdatFlags.CONTINUATION) != 0
    iterated = (flags & ComdatFlags.ITERATED) != 0
    local = (flags & ComdatFlags.LOCAL) != 0
    data_in_code = (flags & ComdatFlags.DATA_IN_CODE) != 0

    selection_val = (attrib >> ComdatFlags.SELECTION_SHIFT) & ComdatFlags.SELECTION_MASK
    allocation_val = attrib & ComdatFlags.ALLOCATION_MASK

    result = ParsedComDat(
        is_32bit=is_32bit,
        flags=flags,
        continuation=continuation,
        iterated=iterated,
        local=local,
        data_in_code=data_in_code,
        selection=ComdatSelection(selection_val),
        allocation=ComdatAllocation(allocation_val),
        alignment=ComdatAlign(align_val)
    )

    offset_size = sub.get_offset_field_size(is_32bit)
    result.enum_offset = sub.parse_numeric(offset_size)
    result.type_index = sub.parse_index()

    if allocation_val == 0:
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
