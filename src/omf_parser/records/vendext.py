"""VENDEXT record handler."""

from . import omf_record
from ..constants import RecordType, KNOWN_VENDORS
from ..models import ParsedVendExt
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.VENDEXT)
def handle_vendext(omf: OMFFileProtocol, record: RecordInfo) -> ParsedVendExt:
    """Handle VENDEXT (CEH)."""
    sub = omf.make_parser(record)
    vendor_num = sub.parse_numeric(2)

    result = ParsedVendExt(vendor_num=vendor_num)
    result.vendor_name = KNOWN_VENDORS.get(vendor_num)

    if result.vendor_name is None:
        result.warnings.append("Unrecognized vendor number")

    if sub.bytes_remaining() > 0:
        result.extension_data = sub.data[sub.offset:]

    return result
