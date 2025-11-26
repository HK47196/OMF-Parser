"""Standard COMENT record handler."""

from ..records import omf_record
from ..constants import RecordType, ComentFlags, CommentClass
from ..models import ParsedComent, ParsedUnknownComent
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo
from . import get_coment_handler


@omf_record(RecordType.COMENT)
def handle_coment(omf: OMFFileProtocol, record: RecordInfo) -> ParsedComent | ParsedUnknownComent | None:
    """Handle COMENT (88H)."""
    sub = omf.make_parser(record)

    flags = sub.read_byte()
    cls = sub.read_byte()

    if flags is None or cls is None:
        return None

    np = (flags & ComentFlags.NP) != 0
    nl = (flags & ComentFlags.NL) != 0
    text = sub.data[sub.offset:]

    # Try to parse as known comment class
    try:
        comment_class = CommentClass.from_raw(cls, omf.variant.omf_variant)
    except ValueError:
        # Unknown comment class
        return ParsedUnknownComent(
            comment_class=cls,
            no_purge=np,
            no_list=nl,
            raw_data=text if text else None
        )

    result = ParsedComent(
        comment_class=comment_class,
        no_purge=np,
        no_list=nl
    )

    handler = get_coment_handler(cls, omf.features)
    if handler:
        content = handler(omf, sub, flags, text)
        result.content = content
    else:
        result.warnings.append(f"No handler for comment class {comment_class}")

    return result
