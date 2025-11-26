"""COMDEF and LCOMDEF record handlers."""

from . import omf_record
from ..constants import RecordType, ComdefType, COMDEF_BORLAND_MAX
from ..models import (
    ParsedComDef,
    ComDefFarDefinition, ComDefNearDefinition,
    ComDefBorlandDefinition, ComDefUnknownDefinition
)
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.COMDEF, RecordType.LCOMDEF)
def handle_comdef(omf: OMFFileProtocol, record: RecordInfo) -> ParsedComDef:
    """Handle COMDEF/LCOMDEF (B0H/B8H)."""
    sub = omf.make_parser(record)
    is_local = (record.type == RecordType.LCOMDEF)

    result = ParsedComDef(is_local=is_local)

    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        type_idx = sub.parse_index()
        data_type = sub.read_byte()

        if data_type is None:
            # Per TIS OMF 1.1: Record Length declares expected size.
            # Missing data indicates malformed record.
            result.warnings.append("Truncated COMDEF record")
            break

        defn: ComDefFarDefinition | ComDefNearDefinition | ComDefBorlandDefinition | ComDefUnknownDefinition
        if data_type == ComdefType.FAR:
            num_elements = sub.parse_variable_length_int()
            element_size = sub.parse_variable_length_int()
            total = num_elements * element_size
            defn = ComDefFarDefinition(
                name=name,
                type_index=type_idx,
                data_type=data_type,
                kind='FAR',
                num_elements=num_elements,
                element_size=element_size,
                total_size=total
            )
        elif data_type == ComdefType.NEAR:
            size = sub.parse_variable_length_int()
            defn = ComDefNearDefinition(
                name=name,
                type_index=type_idx,
                data_type=data_type,
                kind='NEAR',
                size=size
            )
        elif 0x01 <= data_type <= COMDEF_BORLAND_MAX:
            length = sub.parse_variable_length_int()
            defn = ComDefBorlandDefinition(
                name=name,
                type_index=type_idx,
                data_type=data_type,
                kind='Borland',
                seg_index=data_type,
                length=length
            )
        else:
            length = sub.parse_variable_length_int()
            defn = ComDefUnknownDefinition(
                name=name,
                type_index=type_idx,
                data_type=data_type,
                kind='Unknown',
                length=length
            )

        result.definitions.append(defn)
        omf.extdefs.append(name)

    return result
