"""THEADR and LHEADR record handlers."""

from . import omf_record
from ..constants import RecordType
from ..models import ParsedTheadr


@omf_record(RecordType.THEADR, RecordType.LHEADR)
def handle_theadr(omf, record):
    """Handle THEADR (80H) and LHEADR (82H)."""
    omf.lnames = ["<null>"]
    omf.segdefs = ["<null>"]
    omf.grpdefs = ["<null>"]
    omf.extdefs = ["<null>"]
    omf.typdefs = ["<null>"]

    sub = omf.make_parser(record)
    name = sub.parse_name()
    rec_name = "THEADR" if record.type == RecordType.THEADR else "LHEADR"

    return ParsedTheadr(record_name=rec_name, module_name=name)
