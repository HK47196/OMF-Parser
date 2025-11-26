"""Phase 1: Record enumeration and feature detection."""

import struct
from dataclasses import dataclass

from .variant import Variant, TIS_STANDARD, PHARLAP, IBM_LINK386
from .constants import RecordType, CommentClass, OMFVariant


@dataclass
class RecordInfo:
    """Metadata about a single OMF record."""
    type: int
    offset: int
    length: int
    content: bytes
    checksum: int | None
    checksum_valid: bool | None
    module_variant: Variant | None = None


class Scanner:
    """Scans an OMF file to enumerate records and detect features.

    Phase 1 of the two-phase parser:
    - Reads all record boundaries (type, offset, length)
    - Extracts record content (excluding checksum)
    - Validates checksums
    - Detects variant from markers (COMENT classes, vendor strings)
    - Detects extension features
    """

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.offset = 0
        self.features: set[str] = set()
        self.variant: Variant = TIS_STANDARD
        self.is_library = False
        self.has_32bit_records = False
        self.mixed_variants = False
        self.warnings: list[str] = []
        self._module_variant: Variant = TIS_STANDARD
        self._seen_variants: set[OMFVariant] = set()
        self._module_start_idx: int = 0

    def scan(self) -> list[RecordInfo]:
        """Scan the file and return list of records.

        Also populates self.features and self.is_library.

        Returns:
            List of RecordInfo objects for all records in the file
        """
        records: list[RecordInfo] = []

        if not self.data:
            return records

        if self.data[0] == RecordType.LIBHDR:
            self.is_library = True

        while self.offset < len(self.data):
            if self.is_library and self.data[self.offset] == 0x00:
                self.offset += 1
                continue

            record = self._read_record()
            if record is None:
                break

            current_idx = len(records)
            self._detect_features(record, current_idx)
            records.append(record)
            self._track_module_boundaries(record, records)

            if record.type == RecordType.LIBEND:
                break

        self._finalize_module(records)
        self._seen_variants.add(self._module_variant.omf_variant)

        if self.is_library and len(self._seen_variants) > 1:
            self.mixed_variants = True

        return records

    def _track_module_boundaries(self, record: RecordInfo, records: list[RecordInfo]) -> None:
        """Track module boundaries and assign variants to completed modules."""
        if record.type in (RecordType.THEADR, RecordType.LHEADR):
            self._finalize_module(records, exclude_last=True)
            self._module_start_idx = len(records) - 1
            self._module_variant = TIS_STANDARD
        elif record.type in (RecordType.MODEND, RecordType.MODEND32):
            self._finalize_module(records)

    def _finalize_module(self, records: list[RecordInfo], exclude_last: bool = False) -> None:
        """Assign the detected variant to all records in the current module."""
        end_idx = len(records) - 1 if exclude_last else len(records)
        for i in range(self._module_start_idx, end_idx):
            records[i].module_variant = self._module_variant
        self._seen_variants.add(self._module_variant.omf_variant)

    def _read_record(self) -> RecordInfo | None:
        """Read a single record from current offset."""
        if self.offset + 3 > len(self.data):
            return None

        rec_offset = self.offset
        rec_type = self.data[self.offset]
        self.offset += 1

        # Detect 32-bit records (odd record types like SEGDEF32=0x99, LEDATA32=0xA1)
        try:
            rt = RecordType(rec_type)
            if rt.is_32bit:
                self.has_32bit_records = True
        except ValueError:
            pass  # Unknown record type, ignore for 32-bit detection

        rec_len = struct.unpack('<H', self.data[self.offset:self.offset + 2])[0]
        self.offset += 2

        if self.offset + rec_len > len(self.data):
            return None

        raw_content = self.data[self.offset:self.offset + rec_len]
        self.offset += rec_len

        is_lib_record = rec_type in (RecordType.LIBHDR, RecordType.LIBEND)
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

    def _detect_features(self, record: RecordInfo, record_idx: int) -> None:
        """Detect features from record content."""
        if record.type == RecordType.COMENT:
            self._detect_coment_features(record, record_idx)
        elif record.type == RecordType.VENDEXT:
            self._detect_vendext_features(record)

    def _detect_coment_features(self, record: RecordInfo, record_idx: int) -> None:
        """Detect variant and features from COMENT record."""
        if len(record.content) < 2:
            return

        comment_class = record.content[1]

        if comment_class == CommentClass.to_raw(CommentClass.EASY_OMF):
            self.variant = PHARLAP
            self._module_variant = PHARLAP
            self.features.add('easy_omf')
            self.features.add('pharlap')
            self._validate_easy_omf_placement(record, record_idx)

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

    def _detect_vendext_features(self, record: RecordInfo) -> None:
        """Detect features from VENDEXT record."""
        if len(record.content) >= 2:
            vendor_num = struct.unpack('<H', record.content[:2])[0]
            self.features.add(f'vendext_{vendor_num}')

    def _validate_easy_omf_placement(self, record: RecordInfo, record_idx: int) -> None:
        """Validate that Easy OMF-386 marker is immediately after THEADR.

        Per PharLap spec: "The 80386 comment record should be located
        immediately after the module header record (THEADR) and before
        any other records of the object module."
        """
        expected_idx = self._module_start_idx + 1
        if record_idx != expected_idx:
            position_in_module = record_idx - self._module_start_idx
            self.warnings.append(
                f"Easy OMF-386 marker at record {record_idx} (offset 0x{record.offset:X}) "
                f"is not immediately after THEADR; found at position {position_in_module} "
                f"in module (expected position 1)"
            )
