"""LNAMES and LLNAMES record handlers."""

from typing import Literal

from . import omf_record
from ..constants import RecordType, RESERVED_SEGMENTS
from ..models import ParsedLNames, LNameEntry
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.LNAMES, RecordType.LLNAMES)
def handle_lnames(omf: OMFFileProtocol, record: RecordInfo) -> ParsedLNames:
    """Handle LNAMES (96H) and LLNAMES (CAH)."""
    sub = omf.make_parser(record)
    rec_name: Literal["LNAMES", "LLNAMES (Local)"] = "LNAMES" if record.type == RecordType.LNAMES else "LLNAMES (Local)"
    start_idx = len(omf.lnames)

    names: list[LNameEntry] = []
    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        omf.lnames.append(name)
        idx = len(omf.lnames) - 1
        is_reserved = name in RESERVED_SEGMENTS
        names.append((idx, name, is_reserved))

    end_idx = len(omf.lnames) - 1

    return ParsedLNames(
        record_name=rec_name,
        start_index=start_idx,
        end_index=end_idx,
        names=names
    )
