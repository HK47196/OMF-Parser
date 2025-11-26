"""FIXUPP record handler."""

from . import omf_record
from ..constants import (
    RecordType, FixuppFlags, FrameMethod, TargetMethod, FixupLocation, OMFVariant
)
from ..models import (
    ParsedFixupp, ParsedThread, ParsedFixup, ThreadKind, FixupMode
)
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.FIXUPP, RecordType.FIXUPP32)
def handle_fixupp(omf: OMFFileProtocol, record: RecordInfo) -> ParsedFixupp:
    """Handle FIXUPP (9CH/9DH)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.FIXUPP32)

    frame_threads: list[tuple[FrameMethod, int | None] | None] = [None] * 4
    target_threads: list[tuple[TargetMethod, int | None] | None] = [None] * 4

    result = ParsedFixupp(is_32bit=is_32bit)

    while sub.bytes_remaining() > 0:
        peek = sub.peek_byte()
        if peek is None:
            # Per TIS OMF 1.1: Record Length declares expected size.
            # Missing data indicates malformed record.
            result.warnings.append("Truncated FIXUPP record")
            break

        if (peek & FixuppFlags.IS_FIXUP) == 0:
            b = sub.read_byte()
            if b is None:
                # Per TIS OMF 1.1: Record Length declares expected size.
                # Missing data indicates malformed record.
                result.warnings.append("Truncated FIXUPP thread subrecord")
                break
            is_frame = (b & FixuppFlags.THREAD_IS_FRAME) != 0
            method_val = (b >> FixuppFlags.THREAD_METHOD_SHIFT) & FixuppFlags.THREAD_METHOD_MASK
            thred = b & FixuppFlags.THREAD_NUM_MASK

            idx: int | None = None
            if method_val == 3:
                idx = sub.parse_numeric(2)
            elif method_val < 3:
                idx = sub.parse_index()

            kind = ThreadKind.FRAME if is_frame else ThreadKind.TARGET

            method: FrameMethod | TargetMethod
            if is_frame:
                method = FrameMethod(method_val)
                frame_threads[thred] = (method, idx)
            else:
                method = TargetMethod(method_val)
                target_threads[thred] = (method, idx)

            thread = ParsedThread(
                kind=kind,
                thread_num=thred,
                method=method,
                index=idx
            )

            if is_frame:
                if method_val == 3:
                    thread.warnings.append("FRAME method F3 is Invalid per spec")
                elif method_val == 6:
                    thread.warnings.append("FRAME method F6 is Invalid per spec")
                elif method_val == 7:
                    thread.warnings.append("FRAME method F7 is undefined")
            else:
                if method_val == 7:
                    thread.warnings.append("TARGET method T7 is undefined")

            result.subrecords.append(thread)

        else:
            b1 = sub.read_byte()
            b2 = sub.read_byte()

            if b1 is None or b2 is None:
                # Per TIS OMF 1.1: Record Length declares expected size.
                # Missing data indicates malformed record.
                result.warnings.append("Truncated FIXUPP fixup subrecord")
                break

            mode = (b1 >> FixuppFlags.MODE_SHIFT) & 0x01
            loc_type_val = (b1 >> FixuppFlags.LOC_TYPE_SHIFT) & FixuppFlags.LOC_TYPE_MASK
            data_offset = ((b1 & FixuppFlags.OFFSET_HIGH_MASK) << 8) | b2

            mode_enum = FixupMode.SEGMENT_RELATIVE if mode else FixupMode.SELF_RELATIVE
            # PharLap loc 5 is 32-bit offset, not loader-resolved 16-bit
            if loc_type_val == 5 and omf.variant.omf_variant == OMFVariant.PHARLAP:
                location = FixupLocation.PHARLAP_OFFSET_32
            else:
                location = FixupLocation(loc_type_val)

            fix_dat = sub.read_byte()
            if fix_dat is None:
                # Per TIS OMF 1.1: Record Length declares expected size.
                # Missing data indicates malformed record.
                result.warnings.append("Truncated FIXUPP fixup data")
                break

            f_bit = (fix_dat & FixuppFlags.F_BIT) != 0
            frame_field = (fix_dat >> FixuppFlags.FRAME_SHIFT) & FixuppFlags.FRAME_MASK
            t_bit = (fix_dat & FixuppFlags.T_BIT) != 0
            p_bit = (fix_dat & FixuppFlags.P_BIT) != 0
            targt_field = fix_dat & FixuppFlags.TARGET_MASK

            if f_bit:
                thread_num = frame_field & FixuppFlags.THREAD_NUM_MASK
                thread_data = frame_threads[thread_num]
                frame_method, frame_datum = thread_data if thread_data else (FrameMethod.SEGDEF, None)
                frame_src = f"Thread#{thread_num}"
            else:
                frame_method = FrameMethod(frame_field)
                frame_datum = None
                if frame_field < 3:
                    frame_datum = sub.parse_index()
                frame_src = "Explicit"

            if t_bit:
                thread_num = targt_field
                target_thread_data = target_threads[thread_num]
                if target_thread_data:
                    base_method, target_datum = target_thread_data
                    target_method_val = (base_method.int_val & FixuppFlags.TARGET_MASK) | (p_bit << FixuppFlags.P_BIT_SHIFT)
                else:
                    target_method_val = p_bit << FixuppFlags.P_BIT_SHIFT
                    target_datum = None
                target_method = TargetMethod(target_method_val)
                target_src = f"Thread#{thread_num}"
            else:
                target_method_val = targt_field | (p_bit << FixuppFlags.P_BIT_SHIFT)
                target_method = TargetMethod(target_method_val)
                target_datum = sub.parse_index()
                target_src = "Explicit"

            disp = None
            if target_method.int_val < 4:
                disp_size = sub.get_offset_field_size(is_32bit)
                disp = sub.parse_numeric(disp_size)

            fixup = ParsedFixup(
                data_offset=data_offset,
                location=location,
                mode=mode_enum,
                frame_method=frame_method,
                frame_source=frame_src,
                frame_datum=frame_datum,
                target_method=target_method,
                target_source=target_src,
                target_datum=target_datum,
                displacement=disp
            )

            result.subrecords.append(fixup)

    return result
