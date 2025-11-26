"""BAKPAT and NBKPAT record handlers."""

from . import omf_record
from ..constants import RecordType, BackpatchLocation
from ..models import (
    ParsedBackpatch, ParsedNamedBackpatch, BackpatchRecord, NamedBackpatchRecord
)
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.BAKPAT, RecordType.BAKPAT32)
def handle_bakpat(omf: OMFFileProtocol, record: RecordInfo) -> ParsedBackpatch:
    """Handle BAKPAT (B2H/B3H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.BAKPAT32)

    result = ParsedBackpatch(is_32bit=is_32bit)

    while sub.bytes_remaining() > 0:
        seg_idx = sub.parse_index()
        loc_type_val = sub.read_byte()
        if loc_type_val is None:
            # Per TIS OMF 1.1: Record Length declares expected size.
            # Missing data indicates malformed record.
            result.warnings.append("Truncated BAKPAT record")
            break

        location = BackpatchLocation.from_raw(loc_type_val, omf.variant.omf_variant)

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
def handle_nbkpat(omf: OMFFileProtocol, record: RecordInfo) -> ParsedNamedBackpatch:
    """Handle NBKPAT (C8H/C9H)."""
    sub = omf.make_parser(record)
    # NBKPAT has INVERTED bit order: C8H = 32-bit, C9H = 16-bit
    is_32bit = (record.type == RecordType.NBKPAT)

    result = ParsedNamedBackpatch(is_32bit=is_32bit)

    while sub.bytes_remaining() > 0:
        loc_type_val = sub.read_byte()
        if loc_type_val is None:
            # Per TIS OMF 1.1: Record Length declares expected size.
            # Missing data indicates malformed record.
            result.warnings.append("Truncated NBKPAT record")
            break

        if omf.variant.nbkpat_uses_inline_name():
            symbol = sub.parse_name()
        else:
            name_idx = sub.parse_index()
            symbol = omf.get_lname(name_idx)

        location = BackpatchLocation.from_raw(loc_type_val, omf.variant.omf_variant)

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
