"""OMF format detection for standalone and embedded files."""

import re
import struct
from dataclasses import dataclass
from typing import Iterator

from .constants import RecordType


@dataclass
class OMFCandidate:
    """A potential OMF structure found in data."""
    offset: int
    header_type: int
    confidence: float
    description: str
    estimated_size: int | None = None


# Common filename extensions in THEADR (case-insensitive)
_THEADR_EXTENSIONS = re.compile(
    rb'\.(asm|obj|c|cpp|cxx|pas|for|cob|bas|inc|h|hpp)[\x00-\x20]?$',
    re.IGNORECASE
)

# Compiler/assembler signatures in COMENT class 0x00
_TRANSLATOR_SIGNATURES = [
    b'Microsoft', b'MASM', b'ML ', b'LINK',
    b'Borland', b'TASM', b'Turbo',
    b'WATCOM', b'WASM', b'WLINK',
    b'OPTASM', b'LZASM', b'NASM', b'FASM',
    b'Phar Lap', b'PharLap',
    b'Intel', b'iC86', b'ASM86',
    b'Digital Mars', b'DJGPP',
    b'JWasm', b'UASM', b'POASM',
]

# Segment names commonly found in LNAMES
_COMMON_SEGMENTS = [
    b'_TEXT', b'_DATA', b'_BSS', b'CODE', b'DATA', b'STACK',
    b'DGROUP', b'_RDATA', b'CONST', b'.text', b'.data', b'.bss',
    b'FAR_DATA', b'FAR_BSS', b'$$SYMBOLS', b'$$TYPES',
]

# Valid OMF record types
_VALID_RECORD_TYPES = (
    set(range(0x6E, 0x7F, 2)) |  # Obsolete Intel (even only)
    set(range(0x80, 0xCF)) |      # Standard + Microsoft
    {0xF0, 0xF1, 0xF2}            # Library records
)

# Regex patterns for grep-style searching
GREP_PATTERNS = {
    # THEADR with common extensions
    'theadr_asm': rb'\x80..\x00?.{0,64}\.[Aa][Ss][Mm]\x00?',
    'theadr_c': rb'\x80..\x00?.{0,64}\.[Cc]\x00?',
    'theadr_obj': rb'\x80..\x00?.{0,64}\.[Oo][Bb][Jj]\x00?',

    # Easy OMF-386 marker (flags byte can be 0x00 or 0x80)
    'easy_omf': rb'\x88..[\x00\x80]\xAA80386',

    # COMENT with known translators
    'ms_translator': rb'\x88..[\x00\x80]\x00Microsoft',
    'borland_translator': rb'\x88..[\x00\x80]\x00(?:Borland|TASM|Turbo)',
    'watcom_translator': rb'\x88..[\x00\x80]\x00WATCOM',

    # LNAMES with common segments
    'lnames_text': rb'\x96..\x05_TEXT',
    'lnames_data': rb'\x96..\x05_DATA',
    'lnames_code': rb'\x96..\x04CODE',
}


def is_omf(data: bytes) -> bool:
    """
    Quick check if data appears to be an OMF file.

    Args:
        data: File content bytes

    Returns:
        True if data appears to be OMF format
    """
    result = detect_omf(data)
    return result[0]


def detect_omf(data: bytes, check_depth: int = 3) -> tuple[bool, float, str]:
    """
    Detect if data is likely an OMF file.

    Args:
        data: File content bytes
        check_depth: Number of records to validate

    Returns:
        Tuple of (is_omf, confidence, description)
    """
    if len(data) < 4:
        return False, 0.0, "File too small"

    first_byte = data[0]

    valid_headers: dict[int, str] = {
        RecordType.THEADR: "THEADR",
        RecordType.LHEADR: "LHEADR",
        RecordType.LIBHDR: "LIBHDR"
    }
    if first_byte not in valid_headers:
        return False, 0.0, f"Invalid header byte: 0x{first_byte:02X}"

    header_type = valid_headers[first_byte]
    confidence = 0.3

    rec_len = struct.unpack('<H', data[1:3])[0]
    if rec_len == 0 or 3 + rec_len > len(data):
        return False, 0.1, "Invalid record length"

    confidence += 0.1

    if first_byte in (RecordType.THEADR, RecordType.LHEADR):
        content = data[3:3 + rec_len]
        if len(content) >= 2:
            str_len = content[0]
            if str_len == rec_len - 2:
                confidence += 0.15
                name_bytes = content[1:1 + str_len]
                if all(32 <= b < 127 for b in name_bytes):
                    confidence += 0.15

    full_record = data[:3 + rec_len]
    checksum = full_record[-1]
    if checksum == 0 or (sum(full_record) & 0xFF) == 0:
        confidence += 0.1

    valid, _ = _validate_record_chain(data, 0, check_depth, is_library=(first_byte == RecordType.LIBHDR))
    if valid:
        confidence += 0.1

    confidence = min(1.0, confidence)

    if confidence >= 0.5:
        return True, confidence, f"OMF {header_type} detected"
    return False, confidence, f"Unlikely OMF (confidence: {confidence:.0%})"


def scan_for_omf(data: bytes, min_confidence: float = 0.5) -> Iterator[OMFCandidate]:
    """
    Scan binary data for embedded OMF structures.

    Args:
        data: Binary data to scan
        min_confidence: Minimum confidence threshold (0.0-1.0)

    Yields:
        OMFCandidate objects for each potential OMF found
    """
    length = len(data)
    offset = 0

    while offset < length - 4:
        candidate = None

        if data[offset] in (RecordType.THEADR, RecordType.LHEADR):
            candidate = _check_theadr(data, offset)

        elif data[offset] == RecordType.LIBHDR:
            candidate = _check_libhdr(data, offset)

        elif (offset + 8 <= length and
              data[offset] == RecordType.COMENT and
              len(data) > offset + 4 and
              data[offset + 4] == 0xAA):  # Easy OMF class
            candidate = _check_easy_omf_marker(data, offset)

        if candidate and candidate.confidence >= min_confidence:
            yield candidate
            if candidate.estimated_size:
                offset += max(1, candidate.estimated_size)
                continue

        offset += 1


def scan_for_patterns(data: bytes, patterns: list[str] | None = None) -> Iterator[tuple[str, int, bytes]]:
    """
    Scan data using regex patterns for quick OMF signature matching.

    Args:
        data: Binary data to scan
        patterns: List of pattern names from GREP_PATTERNS, or None for all

    Yields:
        Tuples of (pattern_name, offset, matched_bytes)
    """
    if patterns is None:
        patterns = list(GREP_PATTERNS.keys())

    for name in patterns:
        if name not in GREP_PATTERNS:
            continue
        pattern = GREP_PATTERNS[name]
        for match in re.finditer(pattern, data):
            yield (name, match.start(), match.group())


def _validate_record_chain(data: bytes, offset: int, count: int, is_library: bool = False) -> tuple[bool, int]:
    """Validate a chain of OMF records starting at offset."""
    pos = offset

    for i in range(count):
        if is_library:
            while pos < len(data) and data[pos] == 0x00:
                pos += 1

        if pos + 3 > len(data):
            return (i > 0, pos)

        rec_type = data[pos]
        if rec_type not in _VALID_RECORD_TYPES:
            return (i > 0, pos)

        rec_len = struct.unpack('<H', data[pos + 1:pos + 3])[0]
        if rec_len == 0 or pos + 3 + rec_len > len(data):
            return (i > 0, pos)

        if rec_type not in (RecordType.LIBHDR, RecordType.LIBEND):
            record = data[pos:pos + 3 + rec_len]
            checksum = record[-1]
            if checksum != 0 and (sum(record) & 0xFF) != 0:
                return (i > 0, pos)

        if rec_type in (RecordType.MODEND, RecordType.MODEND32, RecordType.LIBEND):
            return (True, pos + 3 + rec_len)

        pos += 3 + rec_len

    return (True, pos)


def _check_theadr(data: bytes, offset: int) -> OMFCandidate | None:
    """Check for THEADR/LHEADR at offset."""
    if offset + 4 > len(data):
        return None

    rec_type = data[offset]
    rec_len = struct.unpack('<H', data[offset + 1:offset + 3])[0]

    if rec_len < 2 or offset + 3 + rec_len > len(data):
        return None

    content = data[offset + 3:offset + 3 + rec_len]
    str_len = content[0]

    if str_len != rec_len - 2:
        return None

    confidence = 0.25
    name_bytes = content[1:1 + str_len]

    if not all(32 <= b < 127 for b in name_bytes):
        return None

    confidence += 0.15
    module_name = name_bytes.decode('ascii', errors='replace')

    if _THEADR_EXTENSIONS.search(name_bytes):
        confidence += 0.20

    record = data[offset:offset + 3 + rec_len]
    checksum = record[-1]
    if checksum == 0 or (sum(record) & 0xFF) == 0:
        confidence += 0.15
    else:
        return None

    is_library = False
    valid, end_offset = _validate_record_chain(data, offset, count=3, is_library=is_library)
    if valid:
        confidence += 0.15

        next_offset = offset + 3 + rec_len
        if next_offset < len(data) and data[next_offset] == RecordType.COMENT:
            confidence += 0.10
            if _has_translator_signature(data, next_offset):
                confidence += 0.15

    header_name = "THEADR" if rec_type == RecordType.THEADR else "LHEADR"
    return OMFCandidate(
        offset=offset,
        header_type=rec_type,
        confidence=min(1.0, confidence),
        description=f"{header_name}: {module_name}",
        estimated_size=end_offset - offset if valid else None
    )


def _check_libhdr(data: bytes, offset: int) -> OMFCandidate | None:
    """Check for LIBHDR at offset."""
    if offset + 10 > len(data):
        return None

    rec_len = struct.unpack('<H', data[offset + 1:offset + 3])[0]
    if rec_len < 7 or offset + 3 + rec_len > len(data):
        return None

    content = data[offset + 3:offset + 3 + rec_len]

    page_size = struct.unpack('<H', content[0:2])[0] + 3

    confidence = 0.25

    if page_size in (16, 32, 64, 128, 256, 512, 1024, 2048, 4096):
        confidence += 0.20
    elif page_size & (page_size - 1) == 0 and 16 <= page_size <= 65536:
        confidence += 0.10
    else:
        return None

    if len(content) >= 6:
        dict_offset = struct.unpack('<I', content[2:6])[0]
        if 0 < dict_offset < len(data) - offset:
            confidence += 0.15

    first_module_offset = offset + page_size
    if first_module_offset < len(data) and data[first_module_offset] == RecordType.THEADR:
        confidence += 0.25
        valid, _ = _validate_record_chain(data, first_module_offset, count=2)
        if valid:
            confidence += 0.15

    return OMFCandidate(
        offset=offset,
        header_type=RecordType.LIBHDR,
        confidence=min(1.0, confidence),
        description=f"LIBHDR: page_size={page_size}",
        estimated_size=None
    )


def _check_easy_omf_marker(data: bytes, offset: int) -> OMFCandidate | None:
    """Check for Easy OMF-386 COMENT marker."""
    if offset + 3 > len(data):
        return None

    rec_len = struct.unpack('<H', data[offset + 1:offset + 3])[0]
    if offset + 3 + rec_len > len(data):
        return None

    content = data[offset + 3:offset + 3 + rec_len - 1]

    if len(content) >= 7 and b'80386' in content:
        return OMFCandidate(
            offset=offset,
            header_type=RecordType.COMENT,
            confidence=0.70,
            description="Easy OMF-386 marker (fragment)",
            estimated_size=3 + rec_len
        )
    return None


def _has_translator_signature(data: bytes, offset: int) -> bool:
    """Check if COMENT at offset contains a known translator signature."""
    if offset + 5 > len(data):
        return False

    rec_len = struct.unpack('<H', data[offset + 1:offset + 3])[0]
    if rec_len < 3 or offset + 3 + rec_len > len(data):
        return False

    content = data[offset + 3:offset + 3 + rec_len]
    comment_class = content[1] if len(content) > 1 else 0xFF

    if comment_class != 0x00:
        return False

    text = content[2:] if len(content) > 2 else b''
    return any(sig in text for sig in _TRANSLATOR_SIGNATURES)
