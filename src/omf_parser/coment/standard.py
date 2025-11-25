"""Standard COMENT record handler."""

from ..records import omf_record
from ..parsing import format_hex_with_ascii
from ..constants import COMMENT_CLASSES
from . import get_coment_handler


@omf_record(0x88)
def handle_coment(omf, record):
    """Handle COMENT (88H)."""
    sub = omf.make_parser(record)

    flags = sub.read_byte()
    cls = sub.read_byte()

    if flags is None or cls is None:
        return

    np = (flags & 0x80) >> 7
    nl = (flags & 0x40) >> 6

    cls_name = COMMENT_CLASSES.get(cls, f"Unknown")
    print(f"  Comment Class: {cls_name} (0x{cls:02X})")
    print(f"  Flags: NoPurge={np}, NoList={nl}")

    text = sub.data[sub.offset:]

    handler = get_coment_handler(cls, omf.features)
    if handler:
        handler(omf, sub, flags, text)
    else:
        if cls not in COMMENT_CLASSES:
            omf.add_warning(f"  [!] WARNING: Unknown comment class 0x{cls:02X}")
        else:
            omf.add_warning(f"  [?] No handler for comment class 0x{cls:02X} ({cls_name})")
        if text:
            print(f"  Data: {format_hex_with_ascii(text)}")
