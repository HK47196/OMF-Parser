"""Standard OMF record handlers."""

from ..constants import (
    COMMENT_CLASSES, A0_SUBTYPES, RESERVED_SEGMENTS,
    ALIGN_NAMES, COMBINE_NAMES, MODE_PHARLAP, KNOWN_VENDORS
)


class StandardHandlersMixin:

    def handle_theadr_lheadr(self, sub, rec_type):
        """Handle THEADR (80H) and LHEADR (82H). Spec Page 8-9."""
        self.lnames = ["<null>"]
        self.segdefs = ["<null>"]
        self.grpdefs = ["<null>"]
        self.extdefs = ["<null>"]
        self.typdefs = ["<null>"]

        name = sub.parse_name()
        rec_name = "THEADR" if rec_type == 0x80 else "LHEADR"
        print(f"  {rec_name} Module: '{name}'")

    def handle_lnames(self, sub, rec_type):
        """Handle LNAMES (96H) and LLNAMES (CAH). Spec Page 36."""
        rec_name = "LNAMES" if rec_type == 0x96 else "LLNAMES (Local)"
        start_idx = len(self.lnames)

        while sub.bytes_remaining() > 0:
            name = sub.parse_name()
            self.lnames.append(name)

        end_idx = len(self.lnames) - 1
        print(f"  {rec_name}: Added indices {start_idx} to {end_idx}")
        for i in range(start_idx, len(self.lnames)):
            marker = " [RESERVED]" if self.lnames[i] in RESERVED_SEGMENTS else ""
            print(f"    [{i}] '{self.lnames[i]}'{marker}")

    def handle_segdef(self, sub, rec_type):
        """Handle SEGDEF (98H/99H). Spec Page 38."""
        is_32bit = (rec_type == 0x99)

        acbp = sub.read_byte()
        if acbp is None:
            return

        align = (acbp >> 5) & 0x07
        combine = (acbp >> 2) & 0x07
        big = (acbp >> 1) & 0x01
        use32 = acbp & 0x01

        print(f"  ACBP: 0x{acbp:02X}")

        align_name = self.call_extension_hook('get_segdef_alignment_name', align)
        if not align_name:
            align_name = ALIGN_NAMES[align]
        print(f"    Alignment: {align_name}")
        print(f"    Combine: {COMBINE_NAMES[combine]}")
        print(f"    Big: {big} (segment is {'64K/4GB' if big else 'smaller'})")
        print(f"    Use32: {use32} ({'Use32' if use32 else 'Use16'})")

        frame_num = None
        frame_offset = None
        if align == 0:
            frame_num = sub.parse_numeric(2)
            frame_offset = sub.read_byte()
            print(f"    Absolute Frame: 0x{frame_num:04X}, Offset: 0x{frame_offset:02X}")

        size_bytes = sub.get_offset_field_size(is_32bit)
        length = sub.parse_numeric(size_bytes)

        if big and length == 0:
            if is_32bit:
                print(f"    Length: 4GB (0x100000000)")
            else:
                print(f"    Length: 64K (0x10000)")
        else:
            print(f"    Length: {length} (0x{length:X})")

        seg_name_idx = sub.parse_index()
        cls_name_idx = sub.parse_index()
        ovl_name_idx = sub.parse_index()

        seg_name = self.get_lname(seg_name_idx)
        cls_name = self.get_lname(cls_name_idx)
        ovl_name = self.get_lname(ovl_name_idx)

        print(f"    Segment Name: {seg_name}")
        print(f"    Class Name: {cls_name}")
        print(f"    Overlay Name: {ovl_name}")

        # Check for PharLap extension (access type byte after overlay name)
        # Per spec: PharLap adds an extra Access Type byte
        if self.target_mode == MODE_PHARLAP and sub.bytes_remaining() >= 1:
            access_byte = sub.read_byte()
            access_type = access_byte & 0x03
            u_bit = (access_byte >> 2) & 0x01
            access_names = ["Read Only", "Execute Only", "Execute/Read", "Read/Write"]
            print(f"    [PharLap] Access: {access_names[access_type]}, Use32: {u_bit}")
        elif sub.bytes_remaining() >= 1:
            # Unknown extension byte in non-PharLap mode
            extra_byte = sub.read_byte()
            print(f"    [Unknown] Extra byte: 0x{extra_byte:02X}")

        raw_name = self.lnames[seg_name_idx] if seg_name_idx < len(self.lnames) else f"Seg#{len(self.segdefs)}"
        self.segdefs.append(raw_name)

    def handle_grpdef(self, sub):
        """Handle GRPDEF (9AH). Spec Page 42."""
        name_idx = sub.parse_index()
        name = self.get_lname(name_idx)

        print(f"  Group Name: {name}")

        # Check for FLAT pseudo-group
        raw_name = self.lnames[name_idx] if name_idx < len(self.lnames) else ""
        if raw_name == "FLAT":
            print("    [Special] FLAT pseudo-group - Virtual Zero Address")

        components = []
        while sub.bytes_remaining() > 0:
            comp_type = sub.read_byte()
            if comp_type is None:
                break

            if comp_type == 0xFF:
                if sub.bytes_remaining() > 0:
                    seg_idx = sub.parse_index()
                    components.append(f"Seg:{self.get_segdef(seg_idx)}")
                else:
                    components.append("Seg:TRUNCATED")
                    break
            elif comp_type == 0xFE:
                if sub.bytes_remaining() > 0:
                    ext_idx = sub.parse_index()
                    components.append(f"Ext:{self.get_extdef(ext_idx)}")
                else:
                    components.append("Ext:TRUNCATED")
                    break
            elif comp_type == 0xFD:
                if sub.bytes_remaining() >= 3:  # At least 3 bytes for minimal indexes
                    seg_name = sub.parse_index()
                    cls_name = sub.parse_index()
                    ovl_name = sub.parse_index()
                    components.append(f"SegDef({seg_name},{cls_name},{ovl_name})")
                else:
                    components.append("SegDef:TRUNCATED")
                    break
            elif comp_type == 0xFB:
                # LTL data - consume the associated fields to prevent stream desync
                # Format: LTL Data field, Maximum Group Length, Group Length
                if sub.bytes_remaining() >= 5:  # 1 + 2 + 2
                    ltl_data = sub.read_byte()
                    max_len = sub.parse_numeric(2)
                    grp_len = sub.parse_numeric(2)
                    components.append(f"LTL(data=0x{ltl_data:02X},max={max_len},len={grp_len})")
                else:
                    components.append("LTL:TRUNCATED")
                    break
            elif comp_type == 0xFA:
                if sub.bytes_remaining() >= 3:  # 2 + 1
                    frame = sub.parse_numeric(2)
                    offset = sub.read_byte()
                    components.append(f"Abs({frame:04X}:{offset:02X})")
                else:
                    components.append("Abs:TRUNCATED")
                    break
            else:
                # Unknown component type - stop parsing to avoid desync
                components.append(f"Unknown({comp_type:02X})")
                self.add_warning(f"    [!] WARNING: Unknown GRPDEF component type 0x{comp_type:02X}, stopping component parsing")
                break

        for comp in components:
            print(f"    Component: {comp}")

        self.grpdefs.append(raw_name)

    def handle_pubdef(self, sub, rec_type):
        """Handle PUBDEF/LPUBDEF (90H/91H/B6H/B7H). Spec Page 31."""
        is_32bit = rec_type in [0x91, 0xB7]
        is_local = rec_type in [0xB6, 0xB7]

        print(f"  {'Local ' if is_local else ''}Public Definitions ({'32-bit' if is_32bit else '16-bit'}):")

        base_grp = sub.parse_index()
        base_seg = sub.parse_index()

        print(f"    Base Group: {self.get_grpdef(base_grp)}")
        print(f"    Base Segment: {self.get_segdef(base_seg)}")

        # Per Spec Page 29: Base Frame exists whenever Base Segment == 0
        # (regardless of Base Group value)
        if base_seg == 0:
            frame = sub.parse_numeric(2)
            print(f"    Absolute Frame: 0x{frame:04X}")
            if base_grp != 0:
                print(f"    [Note] Frame ignored by linker when Base Group != 0")

        while sub.bytes_remaining() > 0:
            name = sub.parse_name()
            if not name and sub.bytes_remaining() == 0:
                break

            offset_size = sub.get_offset_field_size(is_32bit)
            offset = sub.parse_numeric(offset_size)
            type_idx = sub.parse_index()

            print(f"    Symbol: '{name}' Offset=0x{offset:X} Type={type_idx}")

    def handle_extdef(self, sub, rec_type):
        """Handle EXTDEF/LEXTDEF (8CH/B4H/B5H). Spec Page 29."""
        is_local = rec_type in [0xB4, 0xB5]

        print(f"  {'Local ' if is_local else ''}External Definitions:")

        while sub.bytes_remaining() > 0:
            name = sub.parse_name()
            type_idx = sub.parse_index()

            idx = len(self.extdefs)
            self.extdefs.append(name)
            print(f"    [{idx}] '{name}' Type={type_idx}")

    def handle_cextdef(self, sub):
        """Handle CEXTDEF (BCH). Spec Page 62."""
        print("  COMDAT External Definitions:")

        while sub.bytes_remaining() > 0:
            name_idx = sub.parse_index()
            type_idx = sub.parse_index()

            name = self.lnames[name_idx] if name_idx < len(self.lnames) else f"LName#{name_idx}"
            idx = len(self.extdefs)
            self.extdefs.append(name)
            print(f"    [{idx}] {self.get_lname(name_idx)} Type={type_idx}")

    def handle_modend(self, sub, rec_type):
        """Handle MODEND (8AH/8BH). Spec Page 27."""
        is_32bit = (rec_type == 0x8B)

        mod_type = sub.read_byte()
        if mod_type is None:
            return

        is_main = (mod_type & 0x80) != 0
        has_start = (mod_type & 0x40) != 0
        is_relocatable = (mod_type & 0x01) != 0

        print(f"  Module Type: 0x{mod_type:02X}")
        print(f"    Main Module: {is_main}")
        print(f"    Has Start Address: {has_start}")
        print(f"    Relocatable Start: {is_relocatable}")

        if has_start:
            print("  Start Address:")
            end_data = sub.read_byte()
            if end_data is not None:
                f_bit = (end_data >> 7) & 0x01
                frame_method = (end_data >> 4) & 0x07
                t_bit = (end_data >> 3) & 0x01
                p_bit = (end_data >> 2) & 0x01
                target_method = end_data & 0x03

                # Per Spec Page 27: P-bit must be 0
                if p_bit != 0:
                    self.add_warning(f"    [!] WARNING: MODEND P-bit is {p_bit}, must be 0 per spec")

                if frame_method < 3:
                    frame_datum = sub.parse_index()
                    print(f"    Frame Method: {frame_method}, Datum: {frame_datum}")
                else:
                    print(f"    Frame Method: {frame_method}")

                target_datum = sub.parse_index()
                print(f"    Target Method: {target_method}, Datum: {target_datum}")

                if p_bit == 0:
                    disp_size = sub.get_offset_field_size(is_32bit)
                    disp = sub.parse_numeric(disp_size)
                    print(f"    Target Displacement: 0x{disp:X}")

    def handle_linnum(self, sub, rec_type):
        """Handle LINNUM (94H/95H). Spec Page 34."""
        is_32bit = (rec_type == 0x95)

        base_grp = sub.parse_index()
        base_seg = sub.parse_index()

        print(f"  Base Group: {self.get_grpdef(base_grp)}")
        print(f"  Base Segment: {self.get_segdef(base_seg)}")
        print("  Line Number Entries:")

        while sub.bytes_remaining() > 0:
            line_num = sub.parse_numeric(2)  # Line number always 2 bytes
            offset_size = sub.get_offset_field_size(is_32bit)
            offset = sub.parse_numeric(offset_size)

            if line_num == 0:
                print(f"    Line 0 (end of function): Offset=0x{offset:X}")
            else:
                print(f"    Line {line_num}: Offset=0x{offset:X}")

    def handle_vernum(self, sub):
        """Handle VERNUM (CCH). Spec Page 71."""
        version = sub.parse_name()
        print(f"  OMF Version: {version}")

        parts = version.split('.')
        if len(parts) >= 3:
            tis_base = parts[0]
            vendor_num = parts[1]
            vendor_ver = parts[2]

            print(f"    TIS Base Version: {tis_base}")
            print(f"    Vendor Number: {vendor_num}")
            print(f"    Vendor Version: {vendor_ver}")

            # Warn about vendor extensions
            try:
                vendor_int = int(vendor_num)
                if vendor_int != 0:
                    vendor_name = KNOWN_VENDORS.get(vendor_int, "Unknown")
                    self.add_warning(f"    [!] WARNING: Non-TIS vendor extensions present (vendor {vendor_int}: {vendor_name})")
            except ValueError:
                pass

    def handle_vendext(self, sub):
        """Handle VENDEXT (CEH). Spec Page 72."""
        vendor_num = sub.parse_numeric(2)

        vendor_name = KNOWN_VENDORS.get(vendor_num)
        if vendor_name:
            print(f"  Vendor Number: {vendor_num} ({vendor_name})")
        else:
            print(f"  Vendor Number: {vendor_num}")
            self.add_warning(f"  [!] WARNING: Unrecognized vendor number - parser may not handle extensions correctly")

        if sub.bytes_remaining() > 0:
            print(f"  Extension Data: {sub.format_hex_with_ascii(sub.data[sub.offset:])}")

    def handle_locsym(self, sub):
        """Handle LOCSYM (92H) - Local Symbols. Spec Appendix 3."""
        print("  [Obsolete] Local Symbols (same format as PUBDEF)")
        # Parse like PUBDEF
        base_grp = sub.parse_index()
        base_seg = sub.parse_index()
        print(f"    Base Group: {self.get_grpdef(base_grp)}")
        print(f"    Base Segment: {self.get_segdef(base_seg)}")

        # Per Spec Page 29: Base Frame exists whenever Base Segment == 0
        if base_seg == 0:
            frame = sub.parse_numeric(2)
            print(f"    Absolute Frame: 0x{frame:04X}")
            if base_grp != 0:
                print(f"    [Note] Frame ignored by linker when Base Group != 0")

        while sub.bytes_remaining() > 0:
            name = sub.parse_name()
            offset = sub.parse_numeric(2)
            type_idx = sub.parse_index()
            print(f"    '{name}' Offset=0x{offset:X} Type={type_idx}")

    def handle_typdef(self, sub):
        """Handle TYPDEF (8EH). Spec Page 80 (Obsolete)."""
        from ..constants import VAR_TYPE_NAMES

        name = sub.parse_name()  # Always ignored by linkers
        en_byte = sub.read_byte()

        print(f"  [Obsolete TYPDEF]")
        if name:
            print(f"  Name (ignored): '{name}'")

        print(f"  EN Byte: {en_byte}")

        if en_byte == 0:
            # Microsoft stripped format - single leaf descriptor
            print(f"  Format: Microsoft (stripped)")
            if sub.bytes_remaining() == 0:
                self.typdefs.append(f"TYPDEF#{len(self.typdefs)}")
                return

            leaf_type = sub.read_byte()

            if leaf_type == 0x62:  # NEAR
                var_type = sub.read_byte()
                size_bits = sub.parse_variable_length_int()
                print(f"  NEAR Variable")
                print(f"    Type: {VAR_TYPE_NAMES.get(var_type, f'0x{var_type:02X}')}")
                print(f"    Size: {size_bits} bits ({size_bits // 8} bytes)")

            elif leaf_type == 0x61:  # FAR
                var_type = sub.read_byte()  # Must be 0x77 (array)
                num_elements = sub.parse_variable_length_int()
                element_type_idx = sub.parse_index()
                print(f"  FAR Variable (Array)")
                print(f"    Num Elements: {num_elements}")
                print(f"    Element Type: {self.get_typdef(element_type_idx)}")

            else:
                print(f"  Unknown Leaf Type: 0x{leaf_type:02X}")
                print(f"  Remaining: {sub.format_hex_with_ascii(sub.data[sub.offset:])}")

        else:
            # Intel standard format - Eight-Leaf Descriptor
            print(f"  Format: Intel (Eight-Leaf Descriptor)")
            print(f"  Number of leaf descriptors: {en_byte}")

            for leaf_idx in range(en_byte):
                if sub.bytes_remaining() == 0:
                    break

                print(f"  Leaf {leaf_idx + 1}:")
                leaf_type = sub.read_byte()

                if leaf_type == 0x62:  # NEAR
                    var_type = sub.read_byte()
                    size_bits = sub.parse_variable_length_int()
                    print(f"    NEAR Variable")
                    print(f"      Type: {VAR_TYPE_NAMES.get(var_type, f'0x{var_type:02X}')}")
                    print(f"      Size: {size_bits} bits ({size_bits // 8} bytes)")

                elif leaf_type == 0x61:  # FAR
                    var_type = sub.read_byte()  # Must be 0x77 (array)
                    num_elements = sub.parse_variable_length_int()
                    element_type_idx = sub.parse_index()
                    print(f"    FAR Variable (Array)")
                    print(f"      Num Elements: {num_elements}")
                    print(f"      Element Type: {self.get_typdef(element_type_idx)}")

                else:
                    print(f"    Unknown Leaf Type: 0x{leaf_type:02X}")
                    remaining = sub.data[sub.offset:sub.offset + 16]
                    print(f"    Remaining: {sub.format_hex_with_ascii(remaining)}")

        self.typdefs.append(f"TYPDEF#{len(self.typdefs)}")

    def handle_coment(self, sub):
        """Handle COMENT (88H). Spec Page 10-26."""
        flags = sub.read_byte()
        cls = sub.read_byte()

        if flags is None or cls is None:
            return

        np = (flags & 0x80) >> 7
        nl = (flags & 0x40) >> 6

        if cls in COMMENT_CLASSES:
            cls_name = f"{COMMENT_CLASSES[cls]} (0x{cls:02X})"
        else:
            cls_name = f"0x{cls:02X}"
        print(f"  Comment Class: {cls_name}")
        print(f"  Flags: NoPurge={np}, NoList={nl}")

        # Read remaining text for extensions
        text = sub.data[sub.offset:]

        # Delegate to vendor extensions
        handled = self.call_extension_hook('handle_coment', sub, cls, flags, text)

        if not handled:
            # Unknown comment class
            self.add_warning(f"  [!] WARNING: Unhandled comment class: 0x{cls:02X}")
            if text:
                print(f"  Data: {sub.format_hex_with_ascii(text)}")

    def handle_coment_a0(self, sub):
        """Handle Comment Class A0 - OMF Extensions. Spec Page 12."""
        subtype = sub.read_byte()
        if subtype is None:
            return

        subtype_name = A0_SUBTYPES.get(subtype, f"0x{subtype:02X}")
        print(f"  A0 Subtype: {subtype_name}")

        if subtype == 0x01:  # IMPDEF - Spec Page 16
            ord_flag = sub.read_byte()
            int_name = sub.parse_name()
            mod_name = sub.parse_name()

            print(f"    Internal Name: {int_name}")
            print(f"    Module Name: {mod_name}")

            if ord_flag == 0:
                entry_name = sub.parse_name()
                if entry_name == "":
                    print(f"    Entry: (same as internal)")
                else:
                    print(f"    Entry Name: {entry_name}")
            else:
                ordinal = sub.parse_numeric(2)
                print(f"    Ordinal: {ordinal}")

        elif subtype == 0x02:  # EXPDEF - Spec Page 17
            exp_flag = sub.read_byte()
            exp_name = sub.parse_name()
            int_name = sub.parse_name()

            by_ordinal = (exp_flag & 0x80) != 0
            resident = (exp_flag & 0x40) != 0
            no_data = (exp_flag & 0x20) != 0
            parm_count = exp_flag & 0x1F

            print(f"    Exported Name: {exp_name}")
            if int_name:
                print(f"    Internal Name: {int_name}")
            else:
                print(f"    Internal Name: (same as exported)")
            print(f"    By Ordinal: {by_ordinal}, Resident: {resident}, NoData: {no_data}, Parms: {parm_count}")

            if by_ordinal:
                ordinal = sub.parse_numeric(2)
                print(f"    Export Ordinal: {ordinal}")

        elif subtype == 0x03:  # INCDEF - Spec Page 18
            extdef_delta = sub.parse_numeric(2)
            linnum_delta = sub.parse_numeric(2)
            if extdef_delta >= 0x8000:
                extdef_delta -= 0x10000
            if linnum_delta >= 0x8000:
                linnum_delta -= 0x10000
            print(f"    EXTDEF Delta: {extdef_delta}")
            print(f"    LINNUM Delta: {linnum_delta}")
            if sub.bytes_remaining() > 0:
                print(f"    Padding: {sub.bytes_remaining()} bytes")

        elif subtype == 0x04:  # Protected memory library
            print("    DLL uses protected memory (_loadds)")

        elif subtype == 0x05:  # LNKDIR - Spec Page 19
            bit_flags = sub.read_byte()
            pcode_ver = sub.read_byte()
            cv_ver = sub.read_byte()

            print(f"    Bit Flags: 0x{bit_flags:02X}")
            if bit_flags & 0x01:
                print("      - Output new .EXE format")
            if bit_flags & 0x02:
                print("      - Omit CodeView $PUBLICS")
            if bit_flags & 0x04:
                print("      - Run MPC utility")
            print(f"    Pseudocode Version: {pcode_ver}")
            print(f"    CodeView Version: {cv_ver}")

        elif subtype == 0x06:  # Big-endian
            self.is_big_endian = True
            print("    Target is big-endian architecture")
            print("    [MODE] Switched to big-endian parsing")

        elif subtype == 0x07:  # PRECOMP
            print("    $$TYPES should use sstPreComp instead of sstTypes")

        else:
            self.add_error(f"    [FATAL] Unknown A0 subtype 0x{subtype:02X} - linker will abort on this record")
            if sub.bytes_remaining() > 0:
                print(f"    Data: {sub.format_hex_with_ascii(sub.data[sub.offset:])}")
