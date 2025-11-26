"""TYPDEF record handler."""

from . import omf_record
from ..constants import RecordType, TypdefLeaf, TypDefVarType
from ..models import (
    ParsedTypDef, TypDefLeafNear, TypDefLeafFar, TypDefLeafUnknown
)
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.TYPDEF)
def handle_typdef(omf: OMFFileProtocol, record: RecordInfo) -> ParsedTypDef | None:
    """Handle TYPDEF (8EH)."""
    sub = omf.make_parser(record)

    name = sub.parse_name()
    en_byte = sub.read_byte()
    if en_byte is None:
        # Per TIS OMF 1.1: Record Length declares expected size.
        # Missing data indicates malformed record.
        omf.typdefs.append(f"TYPDEF#{len(omf.typdefs)}")
        return None

    result = ParsedTypDef(name=name if name else None, en_byte=en_byte)

    if en_byte == 0:
        result.format = "Microsoft"
        if sub.bytes_remaining() == 0:
            omf.typdefs.append(f"TYPDEF#{len(omf.typdefs)}")
            return result

        leaf_type = sub.read_byte()
        if leaf_type is None:
            omf.typdefs.append(f"TYPDEF#{len(omf.typdefs)}")
            return result

        if leaf_type == TypdefLeaf.NEAR:
            var_type = sub.read_byte()
            if var_type is None:
                # Per TIS OMF 1.1: Record Length declares expected size.
                # Missing data indicates malformed record.
                omf.typdefs.append(f"TYPDEF#{len(omf.typdefs)}")
                return result
            size_bits = sub.parse_variable_length_int()
            result.leaves.append(TypDefLeafNear(
                type='NEAR',
                leaf_type=leaf_type,
                var_type=TypDefVarType.from_raw(var_type, omf.variant.omf_variant),
                size_bits=size_bits,
                size_bytes=size_bits // 8
            ))

        elif leaf_type == TypdefLeaf.FAR:
            var_type = sub.read_byte()
            if var_type is None:
                # Per TIS OMF 1.1: Record Length declares expected size.
                # Missing data indicates malformed record.
                omf.typdefs.append(f"TYPDEF#{len(omf.typdefs)}")
                return result
            num_elements = sub.parse_variable_length_int()
            element_type_idx = sub.parse_index()
            result.leaves.append(TypDefLeafFar(
                type='FAR',
                leaf_type=leaf_type,
                num_elements=num_elements,
                element_type=omf.get_typdef(element_type_idx),
                element_type_index=element_type_idx
            ))

        else:
            result.leaves.append(TypDefLeafUnknown(
                type='Unknown',
                leaf_type=leaf_type,
                remaining=sub.data[sub.offset:]
            ))

    else:
        result.format = "Intel"

        for leaf_idx in range(en_byte):
            if sub.bytes_remaining() == 0:
                break

            leaf_type = sub.read_byte()
            if leaf_type is None:
                break

            if leaf_type == TypdefLeaf.NEAR:
                var_type = sub.read_byte()
                if var_type is None:
                    # Per TIS OMF 1.1: Record Length declares expected size.
                    # Missing data indicates malformed record.
                    break
                size_bits = sub.parse_variable_length_int()
                result.leaves.append(TypDefLeafNear(
                    type='NEAR',
                    leaf_index=leaf_idx + 1,
                    leaf_type=leaf_type,
                    var_type=TypDefVarType.from_raw(var_type, omf.variant.omf_variant),
                    size_bits=size_bits,
                    size_bytes=size_bits // 8
                ))

            elif leaf_type == TypdefLeaf.FAR:
                var_type = sub.read_byte()
                if var_type is None:
                    # Per TIS OMF 1.1: Record Length declares expected size.
                    # Missing data indicates malformed record.
                    break
                num_elements = sub.parse_variable_length_int()
                element_type_idx = sub.parse_index()
                result.leaves.append(TypDefLeafFar(
                    type='FAR',
                    leaf_index=leaf_idx + 1,
                    leaf_type=leaf_type,
                    num_elements=num_elements,
                    element_type=omf.get_typdef(element_type_idx),
                    element_type_index=element_type_idx
                ))

            else:
                remaining = sub.data[sub.offset:sub.offset + 16]
                result.leaves.append(TypDefLeafUnknown(
                    type='Unknown',
                    leaf_index=leaf_idx + 1,
                    leaf_type=leaf_type,
                    remaining=remaining
                ))

    omf.typdefs.append(f"TYPDEF#{len(omf.typdefs)}")

    return result
