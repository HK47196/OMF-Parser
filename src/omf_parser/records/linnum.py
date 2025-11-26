"""LINNUM record handler."""

from . import omf_record
from ..constants import RecordType
from ..models import ParsedLinNum, LineEntry
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.LINNUM, RecordType.LINNUM32)
def handle_linnum(omf: OMFFileProtocol, record: RecordInfo) -> ParsedLinNum:
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
