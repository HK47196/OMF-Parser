"""LINSYM record handler."""

from . import omf_record
from ..constants import RecordType, ComdatFlags
from ..models import ParsedLinSym, LineEntry


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
