"""Library format record handlers."""

import struct


class LibraryHandlersMixin:

    def handle_libheader(self, sub, rec_len):
        """Handle Library Header (F0H). Spec Page 74."""
        # Page size = Record Length + 3 (for type byte and length word)
        page_size = rec_len + 3
        self.lib_page_size = page_size
        self.dictionary_offset = sub.parse_numeric(4)
        self.lib_dict_blocks = sub.parse_numeric(2)
        self.lib_flags = sub.read_byte() or 0

        print(f"  Page Size: {page_size} bytes")
        print(f"  Dictionary Offset: 0x{self.dictionary_offset:08X}")
        print(f"  Dictionary Blocks: {self.lib_dict_blocks}")
        print(f"  Flags: 0x{self.lib_flags:02X}", end="")
        if self.lib_flags & 0x01:
            print(" [Case Sensitive]", end="")
        print()

    def handle_library_dictionary(self):
        """Handle Library Dictionary. Spec Page 75-77."""
        print(f"\n[{self.offset:06X}] === LIBRARY DICTIONARY ===")

        if self.dictionary_offset > 0 and self.offset < self.dictionary_offset:
            padding = self.dictionary_offset - self.offset
            print(f"  Skipping {padding} bytes of padding")
            self.offset = self.dictionary_offset

        entries_found = 0
        for block_num in range(self.lib_dict_blocks):
            block = self.read_bytes(512)
            if not block:
                print(f"  [!] EOF reading dictionary block {block_num}")
                break

            buckets = block[:37]
            free_space = block[37]

            for bucket_idx, bucket_val in enumerate(buckets):
                if bucket_val == 0:
                    continue

                entry_offset = bucket_val * 2
                if entry_offset >= 512:
                    continue

                try:
                    s_len = block[entry_offset]
                    if s_len == 0 or entry_offset + 1 + s_len + 2 > 512:
                        continue

                    s_str = block[entry_offset + 1:entry_offset + 1 + s_len].decode('ascii', errors='replace')
                    page_offset = entry_offset + 1 + s_len
                    page_num = struct.unpack('<H', block[page_offset:page_offset + 2])[0]

                    print(f"  [{block_num}:{bucket_idx:02}] '{s_str}' -> Page {page_num}")
                    entries_found += 1
                except Exception:
                    pass

        print(f"  Total Dictionary Entries: {entries_found}")

        if self.offset < self.file_size:
            peek = self.data[self.offset] if self.offset < len(self.data) else None
            if peek == 0xF2:
                self.handle_extended_dictionary()

    def handle_extended_dictionary(self):
        """Handle Extended Dictionary. Spec Page 77."""
        print(f"\n[{self.offset:06X}] === EXTENDED DICTIONARY ===")

        header = self.read_byte()
        if header != 0xF2:
            print("  [!] Invalid extended dictionary header")
            return

        length = self.parse_numeric(2)
        print(f"  Length: {length} bytes")

        if length < 2:
            return

        num_modules = self.parse_numeric(2)
        print(f"  Number of Modules: {num_modules}")

        for i in range(num_modules + 1):
            if self.bytes_remaining() < 4:
                break
            page_num = self.parse_numeric(2)
            dep_offset = self.parse_numeric(2)
            if page_num != 0 or dep_offset != 0:
                print(f"    Module {i}: Page={page_num}, DepOffset={dep_offset}")
