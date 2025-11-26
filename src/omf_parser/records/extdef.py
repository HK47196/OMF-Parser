"""EXTDEF, LEXTDEF, and CEXTDEF record handlers."""

from . import omf_record
from ..constants import RecordType
from ..models import ParsedExtDef, ParsedCExtDef, ExtDefEntry, CExtDefEntry
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.EXTDEF, RecordType.LEXTDEF, RecordType.LEXTDEF2)
def handle_extdef(omf: OMFFileProtocol, record: RecordInfo) -> ParsedExtDef:
    """Handle EXTDEF/LEXTDEF (8CH/B4H/B5H)."""
    sub = omf.make_parser(record)
    is_local = record.type in (RecordType.LEXTDEF, RecordType.LEXTDEF2)

    result = ParsedExtDef(is_local=is_local)

    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        type_idx = sub.parse_index()

        idx = len(omf.extdefs)
        omf.extdefs.append(name)
        result.externals.append(ExtDefEntry(
            index=idx,
            name=name,
            type_index=type_idx
        ))

    return result


@omf_record(RecordType.CEXTDEF)
def handle_cextdef(omf: OMFFileProtocol, record: RecordInfo) -> ParsedCExtDef:
    """Handle CEXTDEF (BCH)."""
    sub = omf.make_parser(record)

    result = ParsedCExtDef()

    while sub.bytes_remaining() > 0:
        name_idx = sub.parse_index()
        type_idx = sub.parse_index()

        name = omf.lnames[name_idx] if name_idx < len(omf.lnames) else f"LName#{name_idx}"
        idx = len(omf.extdefs)
        omf.extdefs.append(name)
        result.externals.append(CExtDefEntry(
            index=idx,
            name=omf.get_lname(name_idx),
            type_index=type_idx
        ))

    return result
