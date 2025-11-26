"""MODEND record handler."""

from . import omf_record
from ..constants import RecordType, ModendFlags, FrameMethod, TargetMethod
from ..models import ParsedModEnd, StartAddress
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.MODEND, RecordType.MODEND32)
def handle_modend(omf: OMFFileProtocol, record: RecordInfo) -> ParsedModEnd | None:
    """Handle MODEND (8AH/8BH)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.MODEND32)

    mod_type = sub.read_byte()
    if mod_type is None:
        return None

    is_main = (mod_type & ModendFlags.MAIN) != 0
    has_start = (mod_type & ModendFlags.START) != 0
    is_relocatable = (mod_type & ModendFlags.RELOCATABLE) != 0

    result = ParsedModEnd(
        mod_type=mod_type,
        is_main=is_main,
        has_start=has_start,
        is_relocatable=is_relocatable
    )

    if has_start:
        end_data = sub.read_byte()
        if end_data is not None:
            frame_method = (end_data >> ModendFlags.FRAME_SHIFT) & ModendFlags.FRAME_MASK
            p_bit = (end_data >> ModendFlags.P_BIT_SHIFT) & 0x01
            # P bit is high bit of target method (like FIXUPP): methods 0-3 have displacement, 4-6 don't
            target_method = (p_bit << ModendFlags.P_BIT_SHIFT) | (end_data & ModendFlags.TARGET_MASK)

            if p_bit != 0:
                result.warnings.append("MODEND uses secondary target (P=1): valid per Intel OMF, not TIS OMF 1.1")

            frame_datum = None
            if frame_method < 3:
                frame_datum = sub.parse_index()

            target_datum = sub.parse_index()

            target_displacement = None
            if target_method < 4:  # Primary methods (T0-T3) have displacement
                disp_size = sub.get_offset_field_size(is_32bit)
                target_displacement = sub.parse_numeric(disp_size)

            result.start_address = StartAddress(
                frame_method=FrameMethod(frame_method),
                target_method=TargetMethod(target_method),
                frame_datum=frame_datum,
                target_datum=target_datum,
                target_displacement=target_displacement
            )

    return result
