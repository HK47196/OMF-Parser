"""OMF file representation and two-phase parsing orchestration."""

from .scanner import Scanner, RecordInfo
from .parsing import RecordParser, format_hex_with_ascii
from .records import get_record_handler
from .constants import RECORD_NAMES, RESERVED_SEGMENTS
from .variant import Variant, TIS_STANDARD


class OMFFile:
    """Represents a parsed OMF object file or library.

    Two-phase parsing:
    1. scan() - Enumerate records and detect variant/features
    2. parse() - Full parsing with variant-aware handlers
    """

    def __init__(self, filepath: str = None, data: bytes = None):
        self.filepath = filepath or "MEMORY"
        self.data = data

        self.records = []
        self.variant: Variant = TIS_STANDARD
        self.features = set()  # Extension features (not variant-specific)
        self.is_library = False

        self.lnames = ["<null>"]
        self.segdefs = ["<null>"]
        self.grpdefs = ["<null>"]
        self.extdefs = ["<null>"]
        self.typdefs = ["<null>"]

        self.last_data_record = None

        self.lib_page_size = 0
        self.lib_dict_offset = 0
        self.lib_dict_blocks = 0

        self.warnings = []
        self.errors = []

    def load(self):
        """Load file data from filepath."""
        if self.data is None:
            with open(self.filepath, 'rb') as f:
                self.data = f.read()

    def scan(self):
        """Phase 1: Enumerate records and detect variant/features."""
        if self.data is None:
            self.load()

        scanner = Scanner(self.data)
        self.records = scanner.scan()
        self.variant = scanner.variant
        self.features = scanner.features
        self.is_library = scanner.is_library

    def parse(self, output=True):
        """Phase 2: Parse all records with feature-aware handlers."""
        for record in self.records:
            self._parse_record(record, output)

    def dump(self):
        """Scan, parse, and print human-readable output."""
        self.load()

        print(f"{'='*60}")
        print(f"OMF Analysis: {self.filepath}")
        print(f"{'='*60}")
        print(f"File Size: {len(self.data)} bytes")

        self.scan()

        if self.is_library:
            print("File Type: OMF Library (.LIB)")
        else:
            print("File Type: OMF Object Module (.OBJ)")

        print(f"Variant: {self.variant.name}")
        if self.features:
            print(f"Features: {', '.join(sorted(self.features))}")
        print()

        self.parse(output=True)

        if self.is_library and self.lib_dict_offset > 0:
            from .records.library import handle_library_dictionary
            handle_library_dictionary(self)

        self._print_summary()

    def _parse_record(self, record: RecordInfo, output: bool):
        """Parse a single record."""
        rec_name = RECORD_NAMES.get(record.type, f"UNKNOWN(0x{record.type:02X})")

        if output:
            self._print_record_header(record, rec_name)

        handler = get_record_handler(record.type, self.features)
        if handler:
            try:
                handler(self, record)
            except Exception as e:
                self.add_error(f"  [!] Error parsing record: {e}")
                if record.content:
                    print(f"      Raw: {format_hex_with_ascii(record.content[:32])}")
        else:
            self.add_warning(f"  [?] No handler for record type 0x{record.type:02X}")
            if record.content:
                preview = record.content[:32]
                suffix = '...' if len(record.content) > 32 else ''
                print(f"      Raw: {format_hex_with_ascii(preview)}{suffix}")

    def _print_record_header(self, record: RecordInfo, rec_name: str):
        """Print record header line."""
        if record.checksum is not None:
            if record.checksum == 0:
                status = "Skipped (0)"
            elif record.checksum_valid:
                status = "Valid"
            else:
                status = "Invalid"
            print(f"[{record.offset:06X}] {rec_name:<14} Len={record.length:<5} Chk={record.checksum:02X} ({status})")
        else:
            print(f"[{record.offset:06X}] {rec_name:<14} Len={record.length}")

    def _print_summary(self):
        """Print end-of-parse summary."""
        print()
        print(f"{'='*60}")
        print(f"Total Records: {len(self.records)}")

        if self.warnings or self.errors:
            print(f"{'='*60}")
            print("SUMMARY:")

            if self.errors:
                print(f"\nErrors ({len(self.errors)}):")
                for error in self.errors:
                    print(error)

            if self.warnings:
                print(f"\nWarnings ({len(self.warnings)}):")
                for warning in self.warnings:
                    print(warning)

        print(f"{'='*60}")

    def make_parser(self, record: RecordInfo) -> RecordParser:
        """Create a RecordParser for the given record."""
        return RecordParser(record.content, self.variant)

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

    def add_warning(self, message):
        print(message)
        self.warnings.append(message)

    def add_error(self, message):
        print(message)
        self.errors.append(message)
