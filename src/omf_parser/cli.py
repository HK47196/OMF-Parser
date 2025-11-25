"""Command-line interface for OMF parser."""

import json
import sys
import argparse
from .file import OMFFile
from .formatters import HumanFormatter, JSONFormatter
from .records.library import parse_library_dictionary


def generate_schema():
    """Generate JSON schema for the parser output format."""
    from pydantic import BaseModel
    from typing import List, Union, Optional
    from . import models

    # Collect all ParsedRecord subclasses
    record_types = []
    coment_types = []
    a0_types = []

    for name in dir(models):
        cls = getattr(models, name)
        if isinstance(cls, type) and issubclass(cls, BaseModel):
            if issubclass(cls, models.ParsedRecord) and cls is not models.ParsedRecord:
                record_types.append(cls)
            elif issubclass(cls, models.ParsedComentContent) and cls is not models.ParsedComentContent:
                coment_types.append(cls)
            elif issubclass(cls, models.ParsedA0Content) and cls is not models.ParsedA0Content:
                a0_types.append(cls)

    # Create union types
    ParsedRecordUnion = Union[tuple(record_types)]
    ComentContentUnion = Union[tuple(coment_types)]
    A0ContentUnion = Union[tuple(a0_types)]

    # Create result model with proper union type
    class ParseResultSchema(BaseModel):
        """Container for a parsed record result."""
        record_type: int
        record_name: str
        offset: int
        length: int
        checksum: Optional[int]
        checksum_valid: Optional[bool]
        parsed: Optional[ParsedRecordUnion] = None
        error: Optional[str] = None
        raw_content: Optional[bytes] = None

    class OMFFileOutput(BaseModel):
        """Complete JSON output from the OMF parser."""
        filepath: str
        file_size: int
        is_library: bool
        variant: str
        features: List[str]
        records: List[ParseResultSchema]
        warnings: List[str]
        errors: List[str]

    schema = OMFFileOutput.model_json_schema(mode='serialization')
    return schema


def main():
    parser = argparse.ArgumentParser(
        description='Parse and dump OMF object files and libraries.'
    )
    parser.add_argument('file', nargs='?', help='Path to OMF file (.obj or .lib)')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON instead of human-readable text')
    parser.add_argument('--json-indent', type=int, default=2,
                        help='JSON indentation level (default: 2)')
    parser.add_argument('--include-raw', action='store_true',
                        help='Include raw record bytes in JSON output')
    parser.add_argument('--schema', action='store_true',
                        help='Output JSON schema for the parser output format')
    parser.add_argument('--version', action='version', version='omf_parser 2.0')

    args = parser.parse_args()

    if args.schema:
        schema = generate_schema()
        print(json.dumps(schema, indent=2))
        return

    if not args.file:
        parser.error('file is required unless --schema is specified')

    try:
        omf = OMFFile(args.file)
        omf.load()
        omf.scan()

        omf.parse()

        if args.json:
            formatter = JSONFormatter(indent=args.json_indent)
            print(formatter.format_file(omf, include_raw=args.include_raw))
        else:
            formatter = HumanFormatter()

            print(formatter.format_file_header(omf))

            for result in omf.parsed_records:
                print(formatter.format_result(result))

            if omf.is_library and omf.lib_dict_offset > 0:
                lib_dict, ext_dict = parse_library_dictionary(omf)
                if lib_dict:
                    print(f"\n[{omf.lib_dict_offset:06X}] === LIBRARY DICTIONARY ===")
                    print(formatter._format_ParsedLibDict(lib_dict))
                if ext_dict:
                    ext_offset = omf.lib_dict_offset + (omf.lib_dict_blocks * 512)
                    print(f"\n[{ext_offset:06X}] === EXTENDED DICTIONARY ===")
                    print(formatter._format_ParsedExtDict(ext_dict))

            print(formatter.format_summary(omf))

    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
