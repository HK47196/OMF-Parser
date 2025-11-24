"""Data and fixup record handlers."""

from ..constants import MODE_PHARLAP


class DataHandlersMixin:

    def handle_ledata(self, sub, rec_type):
        """Handle LEDATA (A0H/A1H). Spec Page 49."""
        is_32bit = (rec_type == 0xA1)

        seg_idx = sub.parse_index()
        offset_size = 4 if is_32bit else 2
        offset = sub.parse_numeric(offset_size)
        data_len = sub.bytes_remaining()

        print(f"  Segment: {self.get_segdef(seg_idx)}")
        print(f"  Offset: 0x{offset:X}")
        print(f"  Data Length: {data_len} bytes")

        if data_len > 0:
            preview = sub.data[sub.offset:sub.offset + min(16, data_len)]
            print(f"  Data Preview: {preview.hex().upper()}")

        self.last_data_record = ('LEDATA', seg_idx, offset)

    def handle_lidata(self, sub, rec_type):
        """Handle LIDATA (A2H/A3H). Spec Page 51."""
        is_32bit = (rec_type == 0xA3)

        seg_idx = sub.parse_index()
        offset_size = 4 if is_32bit else 2
        offset = sub.parse_numeric(offset_size)

        print(f"  Segment: {self.get_segdef(seg_idx)}")
        print(f"  Offset: 0x{offset:X}")
        print("  Iterated Data Blocks:")

        def parse_data_block(indent=4):
            if sub.bytes_remaining() < 4:
                return

            # COMPATIBILITY NOTE: PharLap uses 16-bit repeat count even in 32-bit records
            # Standard TIS/Microsoft/IBM uses 32-bit repeat count for A3H records
            # Per Spec Page 81
            if is_32bit and self.target_mode != MODE_PHARLAP:
                repeat_count = sub.parse_numeric(4)  # Standard 32-bit
            else:
                repeat_count = sub.parse_numeric(2)  # 16-bit OR PharLap 32-bit

            block_count = sub.parse_numeric(2)

            prefix = " " * indent

            if block_count == 0:
                # Content is data bytes
                content_len = sub.read_byte()
                if content_len is None:
                    return
                content = sub.read_bytes(content_len)
                if content:
                    print(f"{prefix}Repeat {repeat_count}x: {content.hex().upper()}")
            else:
                # Content is nested blocks
                print(f"{prefix}Repeat {repeat_count}x ({block_count} nested blocks):")
                for _ in range(block_count):
                    parse_data_block(indent + 2)

        while sub.bytes_remaining() > 0:
            parse_data_block()

        self.last_data_record = ('LIDATA', seg_idx, offset)

    def handle_fixupp(self, sub, rec_type):
        """Handle FIXUPP (9CH/9DH). Spec Page 44."""
        is_32bit = (rec_type == 0x9D)

        frame_threads = [None] * 4
        target_threads = [None] * 4

        print("  Fixup Subrecords:")

        while sub.bytes_remaining() > 0:
            peek = sub.peek_byte()
            if peek is None:
                break

            if (peek & 0x80) == 0:
                # THREAD subrecord
                b = sub.read_byte()
                is_frame = (b & 0x40) != 0
                method = (b >> 2) & 0x07
                thred = b & 0x03

                idx = None
                # Per Spec Page 44: T3/F3 use explicit 16-bit numbers, not OMF indexes
                if method == 3:
                    idx = sub.parse_numeric(2)  # Explicit 16-bit frame number
                elif method < 3:
                    idx = sub.parse_index()     # Variable-length OMF index

                kind = "FRAME" if is_frame else "TARGET"

                method_names_frame = ["F0:SEGDEF", "F1:GRPDEF", "F2:EXTDEF", "F3:FrameNum",
                                      "F4:Location", "F5:Target", "F6:Invalid", "F7:?"]
                method_names_target = ["T0:SEGDEF", "T1:GRPDEF", "T2:EXTDEF", "T3:FrameNum",
                                       "T4:SEGDEF(0)", "T5:GRPDEF(0)", "T6:EXTDEF(0)", "T7:?"]

                if is_frame:
                    method_name = method_names_frame[method]
                    # Validate F6 as invalid per spec
                    if method == 6:
                        print(f"    [!] WARNING: Invalid FRAME method F6 encountered")
                    frame_threads[thred] = (method, idx)
                else:
                    method_name = method_names_target[method]
                    target_threads[thred] = (method, idx)

                out = f"    THREAD {kind}#{thred} Method={method_name}"
                if idx is not None:
                    label = "FrameNum" if method == 3 else "Index"
                    out += f" {label}={idx}"
                print(out)

            else:
                # FIXUP subrecord
                # Locat word - unusual byte order (Spec Page 46)
                b1 = sub.read_byte()  # Contains: 1, M, Loc(4), HighOff(2)
                b2 = sub.read_byte()  # Contains: LowOff(8)

                if b1 is None or b2 is None:
                    break

                mode = (b1 >> 6) & 0x01
                loc_type = (b1 >> 2) & 0x0F
                data_offset = ((b1 & 0x03) << 8) | b2

                mode_str = "Segment-relative" if mode else "Self-relative"

                # Per Spec: PharLap and IBM/MS have conflicting location type definitions
                if self.target_mode == MODE_PHARLAP:
                    loc_names = {
                        0: "Low Byte(8)",
                        1: "Offset(16)",
                        2: "Segment(16)",
                        3: "Ptr(16:16)",
                        4: "High Byte(8)",
                        5: "Offset(32)",           # PharLap
                        6: "Ptr(16:32)",           # PharLap
                        7: "Reserved(7)",
                        8: "Reserved(8)",
                        9: "Reserved(9)",
                        10: "Reserved(10)",
                        11: "Reserved(11)",
                        12: "Reserved(12)",
                        13: "Reserved(13)",
                    }
                else:
                    # IBM/Microsoft format
                    loc_names = {
                        0: "Low Byte(8)",
                        1: "Offset(16)",
                        2: "Segment(16)",
                        3: "Ptr(16:16)",
                        4: "High Byte(8)",
                        5: "Ldr-Offset(16)",
                        6: "Reserved(6)",
                        7: "Reserved(7)",
                        8: "Reserved(8)",
                        9: "Offset(32)",
                        10: "Reserved(10)",
                        11: "Ptr(16:32)",
                        12: "Reserved(12)",
                        13: "Ldr-Offset(32)",
                    }
                loc_str = loc_names.get(loc_type, f"Unknown({loc_type})")

                fix_dat = sub.read_byte()
                if fix_dat is None:
                    break

                f_bit = (fix_dat >> 7) & 0x01
                frame_field = (fix_dat >> 4) & 0x07
                t_bit = (fix_dat >> 3) & 0x01
                p_bit = (fix_dat >> 2) & 0x01
                targt_field = fix_dat & 0x03

                if f_bit:
                    thread_num = frame_field & 0x03
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
                    # P bit provides high bit of method
                    target_method = (target_method & 0x03) | (p_bit << 2)
                    target_src = f"Thread#{thread_num}"
                else:
                    target_method = targt_field | (p_bit << 2)
                    target_datum = sub.parse_index()
                    target_src = "Explicit"

                disp = None
                if target_method < 4:
                    disp_size = 4 if is_32bit else 2
                    disp = sub.parse_numeric(disp_size)

                print(f"    FIXUP @{data_offset:03X}")
                print(f"      Location: {loc_str}, Mode: {mode_str}")
                print(f"      Frame: Method={frame_method} ({frame_src})", end="")
                if frame_datum is not None:
                    print(f" Datum={frame_datum}", end="")
                print()
                print(f"      Target: Method={target_method} ({target_src})", end="")
                if target_datum is not None:
                    print(f" Datum={target_datum}", end="")
                print()
                if disp is not None:
                    print(f"      Displacement: 0x{disp:X}")
