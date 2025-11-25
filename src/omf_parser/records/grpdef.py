"""GRPDEF record handler."""

from . import omf_record
from ..constants import RecordType, GrpdefComponent
from ..models import ParsedGrpDef


@omf_record(RecordType.GRPDEF)
def handle_grpdef(omf, record):
    """Handle GRPDEF (9AH)."""
    sub = omf.make_parser(record)
    name_idx = sub.parse_index()
    name = omf.get_lname(name_idx)

    raw_name = omf.lnames[name_idx] if name_idx < len(omf.lnames) else ""

    result = ParsedGrpDef(
        name=name,
        name_index=name_idx,
        is_flat=(raw_name == "FLAT")
    )

    while sub.bytes_remaining() > 0:
        comp_type = sub.read_byte()
        if comp_type is None:
            break

        if comp_type == GrpdefComponent.SEGMENT_INDEX:
            if sub.bytes_remaining() > 0:
                seg_idx = sub.parse_index()
                result.components.append(f"Seg:{omf.get_segdef(seg_idx)}")
            else:
                result.components.append("Seg:TRUNCATED")
                break
        elif comp_type == GrpdefComponent.EXTERNAL_INDEX:
            if sub.bytes_remaining() > 0:
                ext_idx = sub.parse_index()
                result.components.append(f"Ext:{omf.get_extdef(ext_idx)}")
            else:
                result.components.append("Ext:TRUNCATED")
                break
        elif comp_type == GrpdefComponent.SEGDEF_INDICES:
            if sub.bytes_remaining() >= 3:
                seg_name = sub.parse_index()
                cls_name = sub.parse_index()
                ovl_name = sub.parse_index()
                result.components.append(f"SegDef({seg_name},{cls_name},{ovl_name})")
            else:
                result.components.append("SegDef:TRUNCATED")
                break
        elif comp_type == GrpdefComponent.LTL:
            if sub.bytes_remaining() >= 5:
                ltl_data = sub.read_byte()
                max_len = sub.parse_numeric(2)
                grp_len = sub.parse_numeric(2)
                result.components.append(f"LTL(data=0x{ltl_data:02X},max={max_len},len={grp_len})")
            else:
                result.components.append("LTL:TRUNCATED")
                break
        elif comp_type == GrpdefComponent.ABSOLUTE:
            if sub.bytes_remaining() >= 3:
                frame = sub.parse_numeric(2)
                offset = sub.read_byte()
                result.components.append(f"Abs({frame:04X}:{offset:02X})")
            else:
                result.components.append("Abs:TRUNCATED")
                break
        else:
            result.components.append(f"Unknown({comp_type:02X})")
            result.warnings.append(f"Unknown GRPDEF component type 0x{comp_type:02X}")
            break

    omf.grpdefs.append(raw_name)

    return result
