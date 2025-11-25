"""Phase 1: Record enumeration and feature detection."""

import struct
from dataclasses import dataclass
from typing import Optional

from .variant import Variant, TIS_STANDARD, PHARLAP, IBM_LINK386


@dataclass
class RecordInfo:
    """Metadata about a single OMF record."""
    type: int
    offset: int
    length: int
    content: bytes
    checksum: Optional[int]
    checksum_valid: Optional[bool]


class Scanner:
    """Scans an OMF file to enumerate records and detect features.

    Phase 1 of the two-phase parser:
    - Reads all record boundaries (type, offset, length)
    - Extracts record content (excluding checksum)
    - Validates checksums
    - Detects variant from markers (COMENT classes, vendor strings)
    - Detects extension features
    """

    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0
        self.features = set()
        self.variant: Variant = TIS_STANDARD
        self.is_library = False
        self.mixed_variants = False
        self._module_variant: Variant = TIS_STANDARD
        self._seen_variants: set = set()

    def scan(self) -> list[RecordInfo]:
        """Scan the file and return list of records.

        Also populates self.features and self.is_library.

        Returns:
            List of RecordInfo objects for all records in the file
        """
        records = []

        if not self.data:
            return records

        if self.data[0] == 0xF0:
            self.is_library = True

        while self.offset < len(self.data):
            if self.is_library and self.data[self.offset] == 0x00:
                self.offset += 1
                continue

            record = self._read_record()
            if record is None:
                break

            records.append(record)
            self._detect_features(record)
            self._track_module_boundaries(record)

            if record.type == 0xF1:
                break

        if self._module_variant != TIS_STANDARD:
            self._seen_variants.add(self._module_variant.name)

        if self.is_library and len(self._seen_variants) > 1:
            self.mixed_variants = True

        return records

    def _track_module_boundaries(self, record: RecordInfo):
        """Track module boundaries to detect mixed variants in libraries."""
        if record.type in (0x80, 0x82):
            if self._module_variant != TIS_STANDARD:
                self._seen_variants.add(self._module_variant.name)
            self._module_variant = TIS_STANDARD
        elif record.type in (0x8A, 0x8B):
            if self._module_variant != TIS_STANDARD:
                self._seen_variants.add(self._module_variant.name)

    def _read_record(self) -> Optional[RecordInfo]:
        """Read a single record from current offset."""
        if self.offset + 3 > len(self.data):
            return None

        rec_offset = self.offset
        rec_type = self.data[self.offset]
        self.offset += 1

        rec_len = struct.unpack('<H', self.data[self.offset:self.offset + 2])[0]
        self.offset += 2

        if self.offset + rec_len > len(self.data):
            return None

        raw_content = self.data[self.offset:self.offset + rec_len]
        self.offset += rec_len

        is_lib_record = rec_type in (0xF0, 0xF1)
        if is_lib_record:
            return RecordInfo(
                type=rec_type,
                offset=rec_offset,
                length=rec_len,
                content=raw_content,
                checksum=None,
                checksum_valid=None,
            )

        checksum = raw_content[-1] if raw_content else 0
        content = raw_content[:-1] if raw_content else b''

        full_record = bytes([rec_type]) + struct.pack('<H', rec_len) + raw_content
        checksum_valid = self._validate_checksum(full_record, checksum)

        return RecordInfo(
            type=rec_type,
            offset=rec_offset,
            length=rec_len,
            content=content,
            checksum=checksum,
            checksum_valid=checksum_valid,
        )

    def _validate_checksum(self, record_data: bytes, checksum: int) -> bool:
        """Validate record checksum."""
        if checksum == 0:
            return True
        return (sum(record_data) & 0xFF) == 0

    def _detect_features(self, record: RecordInfo):
        """Detect features from record content."""
        if record.type == 0x88:
            self._detect_coment_features(record)
        elif record.type == 0xCE:
            self._detect_vendext_features(record)

    def _detect_coment_features(self, record: RecordInfo):
        """Detect variant and features from COMENT record."""
        if len(record.content) < 2:
            return

        comment_class = record.content[1]

        if comment_class == 0xAA:  # Easy OMF-386 (PharLap)
            self.variant = PHARLAP
            self._module_variant = PHARLAP
            self.features.add('easy_omf')
            self.features.add('pharlap')

        if len(record.content) > 2:
            try:
                text = record.content[2:].decode('ascii', errors='ignore').lower()
                if 'pharlap' in text or 'phar lap' in text:
                    if self.variant == TIS_STANDARD:
                        self.variant = PHARLAP
                    self._module_variant = PHARLAP
                elif 'ibm' in text or 'link386' in text:
                    self.variant = IBM_LINK386
                    self._module_variant = IBM_LINK386
                elif 'borland' in text:  # extension, not a variant
                    self.features.add('borland')
            except Exception:
                pass

    def _detect_vendext_features(self, record: RecordInfo):
        """Detect features from VENDEXT record."""
        if len(record.content) >= 2:
            vendor_num = struct.unpack('<H', record.content[:2])[0]
            self.features.add(f'vendext_{vendor_num}')
