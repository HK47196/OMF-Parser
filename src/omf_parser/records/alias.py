"""ALIAS record handler."""

from . import omf_record
from ..constants import RecordType
from ..models import ParsedAlias, AliasEntry
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.ALIAS)
def handle_alias(omf: OMFFileProtocol, record: RecordInfo) -> ParsedAlias:
    """Handle ALIAS (C6H)."""
    sub = omf.make_parser(record)

    result = ParsedAlias()

    while sub.bytes_remaining() > 0:
        alias_name = sub.parse_name()
        subst_name = sub.parse_name()
        result.aliases.append(AliasEntry(
            alias=alias_name,
            substitute=subst_name
        ))

    return result
