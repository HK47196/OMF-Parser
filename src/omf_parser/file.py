"""OMF file representation and two-phase parsing orchestration."""

from .scanner import Scanner, RecordInfo
from .parsing import RecordParser
from .records import get_record_handler
from .constants import RECORD_NAMES, RESERVED_SEGMENTS, RecordType, OMFVariant
from .variant import Variant, TIS_STANDARD
from .models import ParseResult


class OMFFile:
    """Represents a parsed OMF object file or library.

    Two-phase parsing:
    1. scan() - Enumerate records and detect variant/features
    2. parse() - Full parsing with variant-aware handlers

    Parsing returns structured ParseResult objects. Use a formatter
    (see omf_parser.formatters) to produce human-readable or JSON output.
    """

    def __init__(self, filepath: str | None = None, data: bytes | None = None) -> None:
        self.filepath = filepath or "MEMORY"
        self.data = data

        self.records: list[RecordInfo] = []
        self.variant: Variant = TIS_STANDARD
        self.features: set[str] = set()
        self.is_library = False
        self.has_32bit_records = False

        self.lnames: list[str] = ["<null>"]
        self.segdefs: list[str] = ["<null>"]
        self.grpdefs: list[str] = ["<null>"]
        self.extdefs: list[str] = ["<null>"]
        self.typdefs: list[str] = ["<null>"]

        self.last_data_record: tuple[str, int, int] | None = None

        self.lib_page_size = 0
        self.lib_dict_offset = 0
        self.lib_dict_blocks = 0

        self.mixed_variants = False
        self.seen_variants: set[OMFVariant] = set()
        self.parsed_records: list[ParseResult] = []

    def load(self) -> None:
        """Load file data from filepath."""
        if self.data is None:
            with open(self.filepath, 'rb') as f:
                self.data = f.read()

    def scan(self) -> None:
        """Phase 1: Enumerate records and detect variant/features."""
        if self.data is None:
            self.load()

        if self.data is None:
            raise ValueError("No data loaded - call load() first or check file exists")
        scanner = Scanner(self.data)
        self.records = scanner.scan()
        self.variant = scanner.variant
        self.features = scanner.features
        self.is_library = scanner.is_library
        self.has_32bit_records = scanner.has_32bit_records
        self.mixed_variants = scanner.mixed_variants
        self.seen_variants = scanner._seen_variants

    def parse(self) -> list[ParseResult]:
        """Phase 2: Parse all records with feature-aware handlers.

        Returns:
            List of ParseResult objects.
        """
        self.parsed_records = []

        for record in self.records:
            if record.module_variant is not None:
                self.variant = record.module_variant

            if self.is_library and record.type in (RecordType.THEADR, RecordType.LHEADR):
                self._reset_module_state()

            result = self._parse_record(record)
            self.parsed_records.append(result)

        return self.parsed_records

    def _reset_module_state(self) -> None:
        """Reset per-module state at module boundaries in libraries."""
        self.lnames = ["<null>"]
        self.segdefs = ["<null>"]
        self.grpdefs = ["<null>"]
        self.extdefs = ["<null>"]
        self.typdefs = ["<null>"]
        self.last_data_record = None

    def _parse_record(self, record: RecordInfo) -> ParseResult:
        """Parse a single record.

        Returns:
            ParseResult object containing the parsed data or error information.
        """
        rec_name = RECORD_NAMES.get(record.type, f"UNKNOWN(0x{record.type:02X})")

        result = ParseResult(
            record_type=record.type,
            record_name=rec_name,
            offset=record.offset,
            length=record.length,
            checksum=record.checksum,
            checksum_valid=record.checksum_valid,
            raw_content=record.content,
        )

        handler = get_record_handler(record.type, self.features)
        if handler:
            try:
                parsed = handler(self, record)
                result.parsed = parsed
            except Exception as e:
                result.error = str(e)
        else:
            result.error = f"No handler for record type 0x{record.type:02X}"

        return result

    def make_parser(self, record: RecordInfo) -> RecordParser:
        """Create a RecordParser for the given record."""
        return RecordParser(record.content, self.variant)

    def get_lname(self, index: int | None) -> str:
        if index is None:
            return "?"
        if 0 <= index < len(self.lnames):
            name = self.lnames[index]
            if name in RESERVED_SEGMENTS:
                return f"'{name}' [RESERVED]"
            return f"'{name}'"
        return f"LName#{index}(?)"

    def get_segdef(self, index: int | None) -> str:
        if index is None:
            return "?"
        if 0 <= index < len(self.segdefs):
            return self.segdefs[index]
        return f"Seg#{index}"

    def get_grpdef(self, index: int | None) -> str:
        if index is None:
            return "?"
        if 0 <= index < len(self.grpdefs):
            return self.grpdefs[index]
        return f"Grp#{index}"

    def get_extdef(self, index: int) -> str:
        if 0 <= index < len(self.extdefs):
            return f"'{self.extdefs[index]}'"
        return f"Ext#{index}"

    def get_typdef(self, index: int) -> str:
        if 0 <= index < len(self.typdefs):
            return self.typdefs[index]
        return f"Type#{index}"
