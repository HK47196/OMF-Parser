"""Library record handlers (LIBHDR, LIBEND)."""

import struct
from . import omf_record
from ..constants import RecordType, LibraryConsts
from ..models import ParsedLibHdr, ParsedLibEnd, ParsedLibDict, ParsedExtDict, DictEntry, ExtDictModule
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(RecordType.LIBHDR)
def handle_libhdr(omf: OMFFileProtocol, record: RecordInfo) -> ParsedLibHdr | None:
    """Handle Library Header (F0H)."""
    sub = omf.make_parser(record)

    page_size = record.length + 3
    omf.lib_page_size = page_size
    omf.lib_dict_offset = sub.parse_numeric(4)
    omf.lib_dict_blocks = sub.parse_numeric(2)
    lib_flags = sub.read_byte()
    if lib_flags is None:
        # Per TIS OMF 1.1: Record Length declares expected size.
        # Missing data indicates malformed record.
        return None

    return ParsedLibHdr(
        page_size=page_size,
        dict_offset=omf.lib_dict_offset,
        dict_blocks=omf.lib_dict_blocks,
        flags=lib_flags,
        case_sensitive=(lib_flags & LibraryConsts.FLAG_CASE_SENSITIVE) != 0
    )


@omf_record(RecordType.LIBEND)
def handle_libend(omf: OMFFileProtocol, record: RecordInfo) -> ParsedLibEnd:
    """Handle Library End (F1H)."""
    return ParsedLibEnd()


def parse_library_dictionary(omf: OMFFileProtocol) -> tuple[ParsedLibDict | None, ParsedExtDict | None]:
    """Parse Library Dictionary after LIBEND.

    This is called separately after all records are processed,
    not as a record handler.

    Returns:
        Tuple of (ParsedLibDict, Optional[ParsedExtDict])
    """
    if omf.lib_dict_offset == 0 or omf.lib_dict_blocks == 0:
        return None, None

    if omf.data is None:
        return None, None

    dict_start = omf.lib_dict_offset

    result = ParsedLibDict()

    for block_num in range(omf.lib_dict_blocks):
        block_offset = dict_start + (block_num * LibraryConsts.DICT_BLOCK_SIZE)
        if block_offset + LibraryConsts.DICT_BLOCK_SIZE > len(omf.data):
            break

        block = omf.data[block_offset:block_offset + LibraryConsts.DICT_BLOCK_SIZE]
        buckets = block[:LibraryConsts.DICT_BUCKET_COUNT]

        for bucket_idx, bucket_val in enumerate(buckets):
            if bucket_val == 0:
                continue

            entry_offset = bucket_val * 2
            if entry_offset >= LibraryConsts.DICT_BLOCK_SIZE:
                continue

            try:
                s_len = block[entry_offset]
                if s_len == 0 or entry_offset + 1 + s_len + 2 > LibraryConsts.DICT_BLOCK_SIZE:
                    continue

                s_str = block[entry_offset + 1:entry_offset + 1 + s_len].decode('ascii', errors='replace')
                page_offset = entry_offset + 1 + s_len
                page_num = struct.unpack('<H', block[page_offset:page_offset + 2])[0]

                result.entries.append(DictEntry(
                    block=block_num,
                    bucket=bucket_idx,
                    symbol=s_str,
                    page=page_num
                ))
                result.total_entries += 1
            except Exception:
                pass

    ext_dict_offset = dict_start + (omf.lib_dict_blocks * LibraryConsts.DICT_BLOCK_SIZE)
    ext_dict = None
    if ext_dict_offset < len(omf.data) and omf.data[ext_dict_offset] == RecordType.EXTDICT:
        ext_dict = parse_extended_dictionary(omf, ext_dict_offset)

    return result, ext_dict


def parse_extended_dictionary(omf: OMFFileProtocol, offset: int) -> ParsedExtDict | None:
    """Parse Extended Dictionary.

    Returns:
        ParsedExtDict or None
    """
    if omf.data is None or offset >= len(omf.data):
        return None

    header = omf.data[offset]
    if header != RecordType.EXTDICT:
        return None

    length = struct.unpack('<H', omf.data[offset + 1:offset + 3])[0]

    if length < 2:
        return ParsedExtDict(length=length, num_modules=0)

    pos = offset + 3
    num_modules = struct.unpack('<H', omf.data[pos:pos + 2])[0]
    pos += 2

    result = ParsedExtDict(length=length, num_modules=num_modules)

    for i in range(num_modules + 1):
        if pos + 4 > len(omf.data):
            break
        page_num = struct.unpack('<H', omf.data[pos:pos + 2])[0]
        dep_offset = struct.unpack('<H', omf.data[pos + 2:pos + 4])[0]
        pos += 4
        if page_num != 0 or dep_offset != 0:
            result.modules.append(ExtDictModule(
                index=i,
                page=page_num,
                dep_offset=dep_offset
            ))

    return result
