"""PUBDEF and LPUBDEF record handlers."""

from . import omf_record
from ..constants import RecordType
from ..models import ParsedPubDef, PubDefSymbol


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
