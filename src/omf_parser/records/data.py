"""Data record handlers (LEDATA, LIDATA, FIXUPP)."""

from . import omf_record
from ..constants import RecordType, FixuppFlags
from ..models import (
    ParsedLEData, ParsedLIData, ParsedLIDataBlock,
    ParsedFixupp, ParsedThread, ParsedFixup,
    ThreadKind, FixupMode
)


@omf_record(RecordType.LEDATA, RecordType.LEDATA32)
def handle_ledata(omf, record):
    """Handle LEDATA (A0H/A1H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.LEDATA32)

    seg_idx = sub.parse_index()
    offset_size = sub.get_offset_field_size(is_32bit)
    offset = sub.parse_numeric(offset_size)
    data_len = sub.bytes_remaining()

    result = ParsedLEData(
        is_32bit=is_32bit,
        segment=omf.get_segdef(seg_idx),
        segment_index=seg_idx,
        offset=offset,
        data_length=data_len
    )

    if data_len > 0:
        result.data_preview = sub.data[sub.offset:sub.offset + min(16, data_len)]

    omf.last_data_record = ('LEDATA', seg_idx, offset)

    return result


@omf_record(RecordType.LIDATA, RecordType.LIDATA32)
def handle_lidata(omf, record):
    """Handle LIDATA (A2H/A3H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.LIDATA32)

    seg_idx = sub.parse_index()
    offset_size = sub.get_offset_field_size(is_32bit)
    offset = sub.parse_numeric(offset_size)

    result = ParsedLIData(
        is_32bit=is_32bit,
        segment=omf.get_segdef(seg_idx),
        segment_index=seg_idx,
        offset=offset
    )

    def parse_data_block():
        repeat_size = sub.get_lidata_repeat_count_size(is_32bit)
        if sub.bytes_remaining() < repeat_size + 2:
            return None

        repeat_count = sub.parse_numeric(repeat_size)
        block_count = sub.parse_numeric(2)

        block = ParsedLIDataBlock(
            repeat_count=repeat_count,
            block_count=block_count
        )

        if block_count == 0:
            content_len = sub.read_byte()
            if content_len is None:
                return block
            content = sub.read_bytes(content_len)
            block.content = content
        else:
            for _ in range(block_count):
                nested = parse_data_block()
                if nested:
                    block.nested_blocks.append(nested)

        return block

    while sub.bytes_remaining() > 0:
        block = parse_data_block()
        if block:
            result.blocks.append(block)

    omf.last_data_record = ('LIDATA', seg_idx, offset)

    return result


@omf_record(RecordType.FIXUPP, RecordType.FIXUPP32)
def handle_fixupp(omf, record):
    """Handle FIXUPP (9CH/9DH)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.FIXUPP32)

    frame_threads = [None] * 4
    target_threads = [None] * 4

    result = ParsedFixupp(is_32bit=is_32bit)

    method_names_frame = ["F0:SEGDEF", "F1:GRPDEF", "F2:EXTDEF", "F3:FrameNum",
                          "F4:Location", "F5:Target", "F6:Invalid", "F7:?"]
    method_names_target = ["T0:SEGDEF", "T1:GRPDEF", "T2:EXTDEF", "T3:FrameNum",
                           "T4:SEGDEF(0)", "T5:GRPDEF(0)", "T6:EXTDEF(0)", "T7:?"]

    while sub.bytes_remaining() > 0:
        peek = sub.peek_byte()
        if peek is None:
            break

        if (peek & FixuppFlags.IS_FIXUP) == 0:
            b = sub.read_byte()
            is_frame = (b & FixuppFlags.THREAD_IS_FRAME) != 0
            method = (b >> FixuppFlags.THREAD_METHOD_SHIFT) & FixuppFlags.THREAD_METHOD_MASK
            thred = b & FixuppFlags.THREAD_NUM_MASK

            idx = None
            if method == 3:
                idx = sub.parse_numeric(2)
            elif method < 3:
                idx = sub.parse_index()

            kind = ThreadKind.FRAME if is_frame else ThreadKind.TARGET

            if is_frame:
                method_name = method_names_frame[method]
                frame_threads[thred] = (method, idx)
            else:
                method_name = method_names_target[method]
                target_threads[thred] = (method, idx)

            thread = ParsedThread(
                kind=kind,
                thread_num=thred,
                method=method,
                method_name=method_name,
                index=idx
            )

            if is_frame:
                if method == 3:
                    thread.warnings.append("FRAME method F3 is Invalid per spec")
                elif method == 6:
                    thread.warnings.append("FRAME method F6 is Invalid per spec")
                elif method == 7:
                    thread.warnings.append("FRAME method F7 is undefined")
            else:
                if method == 7:
                    thread.warnings.append("TARGET method T7 is undefined")

            result.subrecords.append(thread)

        else:
            b1 = sub.read_byte()
            b2 = sub.read_byte()

            if b1 is None or b2 is None:
                break

            mode = (b1 >> FixuppFlags.MODE_SHIFT) & 0x01
            loc_type = (b1 >> FixuppFlags.LOC_TYPE_SHIFT) & FixuppFlags.LOC_TYPE_MASK
            data_offset = ((b1 & FixuppFlags.OFFSET_HIGH_MASK) << 8) | b2

            mode_enum = FixupMode.SEGMENT_RELATIVE if mode else FixupMode.SELF_RELATIVE

            loc_names = omf.variant.fixupp_loc_names()
            loc_str = loc_names.get(loc_type, f"Unknown({loc_type})")

            fix_dat = sub.read_byte()
            if fix_dat is None:
                break

            f_bit = (fix_dat & FixuppFlags.F_BIT) != 0
            frame_field = (fix_dat >> FixuppFlags.FRAME_SHIFT) & FixuppFlags.FRAME_MASK
            t_bit = (fix_dat & FixuppFlags.T_BIT) != 0
            p_bit = (fix_dat & FixuppFlags.P_BIT) != 0
            targt_field = fix_dat & FixuppFlags.TARGET_MASK

            if f_bit:
                thread_num = frame_field & FixuppFlags.THREAD_NUM_MASK
                frame_method, frame_datum = frame_threads[thread_num] or (0, None)
                frame_src = f"Thread#{thread_num}"
            else:
                frame_method = frame_field
                frame_datum = None
                if frame_method < 3:
                    frame_datum = sub.parse_index()
                frame_src = "Explicit"

            if t_bit:
                thread_num = targt_field
                target_method, target_datum = target_threads[thread_num] or (0, None)
                target_method = (target_method & FixuppFlags.TARGET_MASK) | (p_bit << FixuppFlags.P_BIT_SHIFT)
                target_src = f"Thread#{thread_num}"
            else:
                target_method = targt_field | (p_bit << FixuppFlags.P_BIT_SHIFT)
                target_datum = sub.parse_index()
                target_src = "Explicit"

            disp = None
            if target_method < 4:
                disp_size = sub.get_offset_field_size(is_32bit)
                disp = sub.parse_numeric(disp_size)

            fixup = ParsedFixup(
                data_offset=data_offset,
                location=loc_str,
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
