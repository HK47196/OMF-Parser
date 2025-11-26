"""LOCSYM record handler."""

from . import omf_record
from ..constants import RecordType
from ..models import ParsedLocSym, PubDefSymbol
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.LOCSYM)
def handle_locsym(omf: OMFFileProtocol, record: RecordInfo) -> ParsedLocSym:
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
