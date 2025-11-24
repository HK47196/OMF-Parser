"""OMF complete parser."""

import struct

from .constants import (
    MODE_AUTO, MODE_MS, MODE_IBM, MODE_PHARLAP,
    RECORD_NAMES, RESERVED_SEGMENTS, MODE_NAMES
)
from .parsing_utils import ParsingMixin
from .handlers import (
    StandardHandlersMixin,
    DataHandlersMixin,
    MicrosoftHandlersMixin,
    LibraryHandlersMixin,
    ObsoleteHandlersMixin
)


class OMFCompleteParser(
    ParsingMixin,
    StandardHandlersMixin,
    DataHandlersMixin,
    MicrosoftHandlersMixin,
    LibraryHandlersMixin,
    ObsoleteHandlersMixin
):

    def __init__(self, filepath=None, data=None, offset=0):
        if data is not None:
            self.filepath = "MEMORY"
            self.data = data
            self.offset = offset
            self.file_size = len(data)
        else:
            self.filepath = filepath
            self.offset = 0
            self.data = b""
            self.file_size = 0

        self.is_lib = False
        self.lib_page_size = 0
        self.lib_dict_blocks = 0
        self.dictionary_offset = 0
        self.lib_flags = 0

        # Endianness and architectural mode
        self.is_big_endian = False
        self.target_mode = MODE_MS  # Default to Microsoft format

        self.lnames = ["<null>"]
        self.segdefs = ["<null>"]
        self.grpdefs = ["<null>"]
        self.extdefs = ["<null>"]
        self.typdefs = ["<null>"]
        self.last_data_record = None

    def get_lname(self, index):
        if index is None:
            return "?"
        if 0 <= index < len(self.lnames):
            name = self.lnames[index]
            if name in RESERVED_SEGMENTS:
                return f"'{name}' [RESERVED]"
            return f"'{name}'"
        return f"LName#{index}(?)"

    def get_segdef(self, index):
        if index is None:
            return "?"
        if 0 <= index < len(self.segdefs):
            return self.segdefs[index]
        return f"Seg#{index}"

    def get_grpdef(self, index):
        if index is None:
            return "?"
        if 0 <= index < len(self.grpdefs):
            return self.grpdefs[index]
        return f"Grp#{index}"

    def get_extdef(self, index):
        if 0 <= index < len(self.extdefs):
            return f"'{self.extdefs[index]}'"
        return f"Ext#{index}"

    def get_typdef(self, index):
        if 0 <= index < len(self.typdefs):
            return self.typdefs[index]
        return f"Type#{index}"

    def detect_mode(self):
        if self.file_size == 0:
            return MODE_MS

        # Save current offset to restore later
        saved_offset = self.offset
        self.offset = 0

        detected_mode = MODE_MS  # Default fallback
        records_checked = 0
        max_records = 10

        try:
            while self.offset < self.file_size and records_checked < max_records:
                # Skip library padding
                if self.data[self.offset] == 0x00:
                    self.offset += 1
                    continue

                rec_start = self.offset
                rec_type = self.read_byte()
                if rec_type is None:
                    break

                raw_len = self.read_bytes(2)
                if not raw_len:
                    break
                rec_len = struct.unpack('<H', raw_len)[0]

                raw_content = self.read_bytes(rec_len)
                if raw_content is None or len(raw_content) < rec_len:
                    break

                records_checked += 1

                # Check COMENT records (0x88) for vendor strings
                if rec_type == 0x88 and len(raw_content) > 2:
                    try:
                        # Skip checksum and parse comment
                        content = raw_content[:-1] if len(raw_content) > 0 else raw_content
                        if len(content) >= 2:
                            flags = content[0]
                            cls = content[1]

                            # Check comment text
                            if len(content) > 2:
                                text = content[2:].decode('ascii', errors='ignore').lower()

                                if 'pharlap' in text or 'phar lap' in text:
                                    detected_mode = MODE_PHARLAP
                                    break
                                elif 'ibm' in text or 'link386' in text:
                                    detected_mode = MODE_IBM
                                    break

                                # Easy OMF comment class (0xAA) indicates PharLap
                                if cls == 0xAA:
                                    detected_mode = MODE_PHARLAP
                                    break
                    except Exception:
                        pass

                # Check for OVLDEF (0x76) - old Intel/MS format
                elif rec_type == 0x76:
                    detected_mode = MODE_MS

                # Check for VENDEXT (0xCE) - vendor extension
                elif rec_type == 0xCE and len(raw_content) >= 3:
                    try:
                        content = raw_content[:-1] if len(raw_content) > 0 else raw_content
                        if len(content) >= 2:
                            vendor_num = struct.unpack('<H', content[:2])[0]
                            if vendor_num == 0:
                                detected_mode = MODE_MS
                    except Exception:
                        pass

                # Check Library Header (0xF0) - default to MS for libraries
                elif rec_type == 0xF0:
                    # Keep checking other records in case there are vendor COMMENTs
                    if detected_mode == MODE_MS:
                        detected_mode = MODE_MS

        except Exception:
            # On any error, use default
            pass

        finally:
            # Restore offset for actual parsing
            self.offset = saved_offset

        return detected_mode

    def run(self):
        print(f"{'='*60}")
        print(f"OMF Complete Analysis: {self.filepath}")
        print(f"{'='*60}")

        if not self.data:
            try:
                with open(self.filepath, 'rb') as f:
                    self.data = f.read()
                    self.file_size = len(self.data)
            except Exception as e:
                print(f"Error reading file: {e}")
                return

        if self.file_size == 0:
            print("Empty file.")
            return

        print(f"File Size: {self.file_size} bytes")

        # Detect Library
        if self.data[0] == 0xF0:
            self.is_lib = True
            print("File Type: OMF Library (.LIB)")
        else:
            print("File Type: OMF Object Module (.OBJ)")

        print()

        stop_record_parsing = False
        record_count = 0

        while self.offset < self.file_size and not stop_record_parsing:
            if self.is_lib and self.data[self.offset] == 0x00:
                self.offset += 1
                continue

            rec_start = self.offset
            rec_type = self.read_byte()
            if rec_type is None:
                break

            raw_len = self.read_bytes(2)
            if not raw_len:
                print(f"\n[!] Error: Unexpected EOF reading record length at {rec_start:06X}")
                break
            rec_len = struct.unpack('<H', raw_len)[0]

            # Per Spec Page 1: Most records should not exceed 1024 bytes
            # Exceptions: LIDATA (iterated blocks), large comments, library dictionaries
            if rec_len > 1024:
                allowed_large = [0x88, 0xA2, 0xA3, 0xF0, 0xF1]  # COMENT, LIDATA, LIDATA32, LIBHDR, LIBEND
                if rec_type not in allowed_large:
                    print(f"[!] WARNING: Record length {rec_len} exceeds 1024 bytes (type 0x{rec_type:02X})")

            raw_content = self.read_bytes(rec_len)
            if raw_content is None or len(raw_content) < rec_len:
                print(f"\n[!] Error: Unexpected EOF reading record content at {rec_start:06X}")
                break

            record_count += 1

            # Library records F0/F1 do NOT have checksums
            is_lib_rec = rec_type in [0xF0, 0xF1]

            sub = OMFCompleteParser(data=raw_content)
            sub.lnames = self.lnames
            sub.segdefs = self.segdefs
            sub.grpdefs = self.grpdefs
            sub.extdefs = self.extdefs
            sub.typdefs = self.typdefs
            # Inherit mode and endianness settings
            sub.is_big_endian = self.is_big_endian
            sub.target_mode = self.target_mode

            checksum = None
            checksum_status = ""
            if not is_lib_rec and len(raw_content) > 0:
                checksum = raw_content[-1]
                full_record = bytes([rec_type]) + raw_len + raw_content
                valid, checksum_status = self.validate_checksum(full_record, checksum)
                sub.data = raw_content[:-1]
                sub.file_size = len(sub.data)

            rec_name = RECORD_NAMES.get(rec_type, f"UNKNOWN({rec_type:02X})")

            if checksum is not None:
                print(f"[{rec_start:06X}] {rec_name:<14} Len={rec_len:<5} Chk={checksum:02X} ({checksum_status})")
            else:
                print(f"[{rec_start:06X}] {rec_name:<14} Len={rec_len}")

            try:
                self._dispatch_handler(sub, rec_type, rec_len, stop_record_parsing)
                if rec_type == 0xF1:
                    stop_record_parsing = True
            except Exception as e:
                print(f"  [!] Error parsing record: {e}")
                if sub.data:
                    print(f"      Raw: {sub.data[:32].hex().upper()}")

        if self.is_lib and stop_record_parsing:
            self.handle_library_dictionary()

        print()
        print(f"{'='*60}")
        print(f"Total Records: {record_count}")
        print(f"{'='*60}")

    def _dispatch_handler(self, sub, rec_type, rec_len, stop_parsing):
        if rec_type == 0xF0:
            self.handle_libheader(sub, rec_len)
        elif rec_type == 0xF1:
            print("  End of Library Modules.")
        elif rec_type in [0x80, 0x82]:
            self.handle_theadr_lheadr(sub, rec_type)
        elif rec_type == 0x88:
            self.handle_coment(sub)
        elif rec_type in [0x96, 0xCA]:
            self.handle_lnames(sub, rec_type)
        elif rec_type in [0x98, 0x99]:
            self.handle_segdef(sub, rec_type)
        elif rec_type == 0x9A:
            self.handle_grpdef(sub)
        elif rec_type in [0x90, 0x91, 0xB6, 0xB7]:
            self.handle_pubdef(sub, rec_type)
        elif rec_type in [0x8C, 0xB4, 0xB5]:
            self.handle_extdef(sub, rec_type)
        elif rec_type == 0xBC:
            self.handle_cextdef(sub)
        elif rec_type in [0xA0, 0xA1]:
            self.handle_ledata(sub, rec_type)
        elif rec_type in [0xA2, 0xA3]:
            self.handle_lidata(sub, rec_type)
        elif rec_type in [0x9C, 0x9D]:
            self.handle_fixupp(sub, rec_type)
        elif rec_type in [0xB2, 0xB3]:
            self.handle_bakpat(sub, rec_type)
        elif rec_type in [0xC8, 0xC9]:
            self.handle_nbkpat(sub, rec_type)
        elif rec_type in [0xB0, 0xB8]:
            self.handle_comdef(sub, rec_type)
        elif rec_type in [0xC2, 0xC3]:
            self.handle_comdat(sub, rec_type)
        elif rec_type in [0xC4, 0xC5]:
            self.handle_linsym(sub, rec_type)
        elif rec_type == 0xC6:
            self.handle_alias(sub)
        elif rec_type == 0x8E:
            self.handle_typdef(sub)
        elif rec_type in [0x8A, 0x8B]:
            self.handle_modend(sub, rec_type)
        elif rec_type == 0xCC:
            self.handle_vernum(sub)
        elif rec_type in [0x94, 0x95]:
            self.handle_linnum(sub, rec_type)
        elif rec_type == 0xCE:
            self.handle_vendext(sub)
        elif rec_type == 0x92:
            self.handle_locsym(sub)
        # Obsolete records
        elif rec_type == 0x6E:
            self.handle_rheadr(sub)
        elif rec_type == 0x70:
            self.handle_regint(sub)
        elif rec_type in [0x72, 0x84]:
            self.handle_redata_pedata(sub, rec_type)
        elif rec_type in [0x74, 0x86]:
            self.handle_ridata_pidata(sub, rec_type)
        elif rec_type == 0x76:
            self.handle_ovldef(sub)
        elif rec_type == 0x78:
            self.handle_endrec(sub)
        elif rec_type == 0x7A:
            self.handle_blkdef(sub)
        elif rec_type == 0x7C:
            self.handle_blkend(sub)
        elif rec_type == 0x7E:
            self.handle_debsym(sub)
        elif rec_type == 0x9E:
            print("  [!] Unnamed record (never defined in any spec)")
        elif rec_type == 0xA4:
            self.handle_libhed_obsolete(sub)
        elif rec_type == 0xA6:
            self.handle_libnam_obsolete(sub)
        elif rec_type == 0xA8:
            self.handle_libloc_obsolete(sub)
        elif rec_type == 0xAA:
            self.handle_libdic_obsolete(sub)
        else:
            print(f"  [?] Unhandled record type: {rec_type:02X}")
            if sub.data:
                print(f"      Raw: {sub.data[:32].hex().upper()}{'...' if len(sub.data) > 32 else ''}")
