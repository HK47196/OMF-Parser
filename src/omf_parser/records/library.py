"""Library record handlers (LIBHDR, LIBEND)."""

import struct
from . import omf_record


@omf_record(0xF0)
def handle_libhdr(omf, record):
    """Handle Library Header (F0H)."""
    sub = omf.make_parser(record)

    page_size = record.length + 3
    omf.lib_page_size = page_size
    omf.lib_dict_offset = sub.parse_numeric(4)
    omf.lib_dict_blocks = sub.parse_numeric(2)
    lib_flags = sub.read_byte() or 0

    print(f"  Page Size: {page_size} bytes")
    print(f"  Dictionary Offset: 0x{omf.lib_dict_offset:08X}")
    print(f"  Dictionary Blocks: {omf.lib_dict_blocks}")
    print(f"  Flags: 0x{lib_flags:02X}", end="")
    if lib_flags & 0x01:
        print(" [Case Sensitive]", end="")
    print()


@omf_record(0xF1)
def handle_libend(omf, record):
    """Handle Library End (F1H)."""
    print("  End of Library Modules.")


def handle_library_dictionary(omf):
    """Handle Library Dictionary after LIBEND.

    This is called separately after all records are processed,
    not as a record handler.
    """
    from ..parsing import RecordParser

    print(f"\n[{omf.lib_dict_offset:06X}] === LIBRARY DICTIONARY ===")

    if omf.lib_dict_offset == 0 or omf.lib_dict_blocks == 0:
        print("  No dictionary present")
        return

    dict_start = omf.lib_dict_offset
    entries_found = 0

    for block_num in range(omf.lib_dict_blocks):
        block_offset = dict_start + (block_num * 512)
        if block_offset + 512 > len(omf.data):
            print(f"  [!] EOF reading dictionary block {block_num}")
            break

        block = omf.data[block_offset:block_offset + 512]
        buckets = block[:37]

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

    ext_dict_offset = dict_start + (omf.lib_dict_blocks * 512)
    if ext_dict_offset < len(omf.data) and omf.data[ext_dict_offset] == 0xF2:
        handle_extended_dictionary(omf, ext_dict_offset)


def handle_extended_dictionary(omf, offset):
    """Handle Extended Dictionary."""
    from ..parsing import RecordParser

    print(f"\n[{offset:06X}] === EXTENDED DICTIONARY ===")

    if offset >= len(omf.data):
        return

    header = omf.data[offset]
    if header != 0xF2:
        print("  [!] Invalid extended dictionary header")
        return

    length = struct.unpack('<H', omf.data[offset + 1:offset + 3])[0]
    print(f"  Length: {length} bytes")

    if length < 2:
        return

    pos = offset + 3
    num_modules = struct.unpack('<H', omf.data[pos:pos + 2])[0]
    pos += 2
    print(f"  Number of Modules: {num_modules}")

    for i in range(num_modules + 1):
        if pos + 4 > len(omf.data):
            break
        page_num = struct.unpack('<H', omf.data[pos:pos + 2])[0]
        dep_offset = struct.unpack('<H', omf.data[pos + 2:pos + 4])[0]
        pos += 4
        if page_num != 0 or dep_offset != 0:
            print(f"    Module {i}: Page={page_num}, DepOffset={dep_offset}")
