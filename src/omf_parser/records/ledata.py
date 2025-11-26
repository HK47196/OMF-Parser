"""LEDATA record handler."""

from . import omf_record
from ..constants import RecordType
from ..models import ParsedLEData
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.LEDATA, RecordType.LEDATA32)
def handle_ledata(omf: OMFFileProtocol, record: RecordInfo) -> ParsedLEData:
    """Handle LEDATA (A0H/A1H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.LEDATA32)

    seg_idx = sub.parse_index()
    offset_size = sub.get_offset_field_size(is_32bit)
    offset = sub.parse_numeric(offset_size)
    data_len = sub.bytes_remaining()

    result = ParsedLEData(
        is_32bit=is_32bit,
        segment=omf.get_segdef(seg_idx),
        segment_index=seg_idx,
        offset=offset,
        data_length=data_len
    )

    if data_len > 0:
        result.data_preview = sub.data[sub.offset:sub.offset + min(16, data_len)]

    omf.last_data_record = ('LEDATA', seg_idx, offset)

    return result
