"""SEGDEF record handler."""

from . import omf_record
from ..constants import (
    RecordType, SegdefFlags, SegmentSize, SegAlignment, SegCombine, SegAccess
)
from ..models import ParsedSegDef
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.SEGDEF, RecordType.SEGDEF32)
def handle_segdef(omf: OMFFileProtocol, record: RecordInfo) -> ParsedSegDef | None:
    """Handle SEGDEF (98H/99H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.SEGDEF32)

    acbp = sub.read_byte()
    if acbp is None:
        return None

    align_val = (acbp >> SegdefFlags.ALIGN_SHIFT) & SegdefFlags.ALIGN_MASK
    combine_val = (acbp >> SegdefFlags.COMBINE_SHIFT) & SegdefFlags.COMBINE_MASK
    big = (acbp >> 1) & SegdefFlags.BIG_MASK
    use32 = acbp & SegdefFlags.USE32_MASK

    variant = omf.variant.omf_variant
    alignment = SegAlignment.from_raw(align_val, variant)

    result = ParsedSegDef(
        acbp=acbp,
        alignment=alignment,
        alignment_bytes=SegAlignment.alignment_bytes(alignment, variant),
        combine=SegCombine.from_raw(combine_val, variant),
        big=bool(big),
        use32=bool(use32)
    )

    if align_val == 0:
        result.absolute_frame = sub.parse_numeric(2)
        abs_offset = sub.read_byte()
        if abs_offset is None:
            # Per TIS OMF 1.1: Record Length declares expected size.
            # Missing data indicates malformed record.
            result.warnings.append("Truncated SEGDEF absolute offset")
            raw_name = f"Seg#{len(omf.segdefs)}"
            omf.segdefs.append(raw_name)
            return result
        result.absolute_offset = abs_offset

    size_bytes = sub.get_offset_field_size(is_32bit)
    length = sub.parse_numeric(size_bytes)

    if big and length == 0:
        if is_32bit:
            result.length = SegmentSize.SIZE_4GB
        else:
            result.length = SegmentSize.SIZE_64K
    else:
        result.length = length

    seg_name_idx = sub.parse_index()
    cls_name_idx = sub.parse_index()
    ovl_name_idx = sub.parse_index()

    result.segment_name = omf.get_lname(seg_name_idx)
    result.class_name = omf.get_lname(cls_name_idx)
    result.overlay_name = omf.get_lname(ovl_name_idx)

    if sub.bytes_remaining() >= 1:
        if omf.variant.segdef_has_access_byte():
            access_byte = sub.read_byte()
            if access_byte is None:
                # Per TIS OMF 1.1: Record Length declares expected size.
                # Missing data indicates malformed record.
                result.warnings.append("Truncated SEGDEF access byte")
            else:
                access_type = access_byte & SegdefFlags.ACCESS_TYPE_MASK
                result.access_byte = access_byte
                result.access = SegAccess.from_raw(access_type, variant)
                # PharLap U bit (bit 2) is authoritative for Use16/Use32
                result.use32 = bool(access_byte & SegdefFlags.ACCESS_U_BIT_MASK)

    raw_name = omf.lnames[seg_name_idx] if seg_name_idx < len(omf.lnames) else f"Seg#{len(omf.segdefs)}"
    omf.segdefs.append(raw_name)

    return result
