"""BAKPAT and NBKPAT record handlers."""

from . import omf_record
from ..constants import RecordType, BackpatchLocation
from ..models import (
    ParsedBackpatch, ParsedNamedBackpatch, BackpatchRecord, NamedBackpatchRecord
)


@omf_record(RecordType.BAKPAT, RecordType.BAKPAT32)
def handle_bakpat(omf, record):
    """Handle BAKPAT (B2H/B3H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.BAKPAT32)

    result = ParsedBackpatch(is_32bit=is_32bit)

    while sub.bytes_remaining() > 0:
        seg_idx = sub.parse_index()
        loc_type_val = sub.read_byte()

        location = BackpatchLocation(loc_type_val)

        if loc_type_val == 2 and record.type == RecordType.BAKPAT:
            result.warnings.append("Location type 2 (DWord) only valid for B3H records")

        val_size = sub.get_offset_field_size(is_32bit)
        offset = sub.parse_numeric(val_size)
        value = sub.parse_numeric(val_size)

        result.records.append(BackpatchRecord(
            segment=omf.get_segdef(seg_idx),
            segment_index=seg_idx,
            location=location,
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

    result = ParsedNamedBackpatch(is_32bit=is_32bit)

    while sub.bytes_remaining() > 0:
        loc_type_val = sub.read_byte()

        if omf.variant.nbkpat_uses_inline_name():
            symbol = sub.parse_name()
        else:
            name_idx = sub.parse_index()
            symbol = omf.get_lname(name_idx)

        location = BackpatchLocation(loc_type_val)

        val_size = sub.get_offset_field_size(is_32bit)
        offset = sub.parse_numeric(val_size)
        value = sub.parse_numeric(val_size)

        result.records.append(NamedBackpatchRecord(
            location=location,
            symbol=symbol,
            offset=offset,
            value=value
        ))

    return result
