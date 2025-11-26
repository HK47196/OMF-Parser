"""Standard COMENT record handler."""

from ..records import omf_record
from ..constants import RecordType, ComentFlags, CommentClass
from ..models import ParsedComent
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo
from . import get_coment_handler


@omf_record(RecordType.COMENT)
def handle_coment(omf: OMFFileProtocol, record: RecordInfo) -> ParsedComent | None:
    """Handle COMENT (88H)."""
    sub = omf.make_parser(record)

    flags = sub.read_byte()
    cls = sub.read_byte()

    if flags is None or cls is None:
        return None

    np = (flags & ComentFlags.NP) != 0
    nl = (flags & ComentFlags.NL) != 0

    result = ParsedComent(
        comment_class=cls,
        no_purge=np,
        no_list=nl
    )

    text = sub.data[sub.offset:]

    handler = get_coment_handler(cls, omf.features)
    if handler:
        content = handler(omf, sub, flags, text)
        result.content = content
    else:
        try:
            known_class = CommentClass(cls)
            warning = f"No handler for comment class 0x{cls:02X} ({known_class.label})"
        except ValueError:
            warning = f"Unknown comment class 0x{cls:02X}"
        result.warnings.append(warning)
        if text:
            result.raw_data = text

    return result
