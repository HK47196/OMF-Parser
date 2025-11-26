"""VERNUM record handler."""

from . import omf_record
from ..constants import RecordType, KNOWN_VENDORS
from ..models import ParsedVerNum
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.VERNUM)
def handle_vernum(omf: OMFFileProtocol, record: RecordInfo) -> ParsedVerNum:
    """Handle VERNUM (CCH)."""
    sub = omf.make_parser(record)
    version = sub.parse_name()

    result = ParsedVerNum(version=version)

    parts = version.split('.')
    if len(parts) >= 3:
        result.tis_base = parts[0]
        result.vendor_num = parts[1]
        result.vendor_ver = parts[2]

        try:
            vendor_int = int(parts[1])
            if vendor_int != 0:
                vendor_name = KNOWN_VENDORS.get(vendor_int, "Unknown")
                result.vendor_name = vendor_name
                result.warnings.append(f"Non-TIS vendor extensions present (vendor {vendor_int}: {vendor_name})")
        except ValueError:
            pass

    return result
