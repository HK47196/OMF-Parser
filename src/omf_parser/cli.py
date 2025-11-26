"""Command-line interface for OMF parser."""

import json
import sys
import argparse
from typing import Any
from .file import OMFFile
from .formatters import HumanFormatter, JSONFormatter
from .constants import OMFVariant
from .records.library import parse_library_dictionary
from .detect import detect_omf, scan_for_omf, scan_for_patterns, GREP_PATTERNS


def generate_schema() -> dict[str, Any]:
    """Generate JSON schema for the parser output format."""
    from .models import ParsedOMFFile
    return ParsedOMFFile.model_json_schema(mode='serialization')


def main() -> None:
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
    parser.add_argument('--detect', action='store_true',
                        help='Detect OMF format and output structured info (JSON)')
    parser.add_argument('--scan', action='store_true',
                        help='Scan file for embedded OMF structures')
    parser.add_argument('--scan-patterns', action='store_true',
                        help='Scan using regex patterns (faster, less accurate)')
    parser.add_argument('--min-confidence', type=float, default=0.5,
                        help='Minimum confidence for --scan (0.0-1.0, default: 0.5)')
    parser.add_argument('--version', action='version', version='omf_parser 2.0')

    args = parser.parse_args()

    if args.schema:
        schema = generate_schema()
        print(json.dumps(schema, indent=2))
        return

    if not args.file:
        parser.error('file is required unless --schema is specified')

    # Detection mode
    if args.detect:
        try:
            with open(args.file, 'rb') as f:
                data = f.read()
            is_omf, confidence, description = detect_omf(data)

            if is_omf:
                # Run scan phase to get detailed info
                try:
                    omf = OMFFile(args.file, data=data)
                    omf.scan()
                    # PharLap is always 32-bit
                    is_32bit = omf.has_32bit_records or omf.variant.omf_variant == OMFVariant.PHARLAP
                    output = {
                        'valid': True,
                        'is_library': omf.is_library,
                        'is_32bit': is_32bit,
                        'variant': omf.variant.name,
                    }
                except Exception as e:
                    output = {
                        'valid': False,
                        'is_library': None,
                        'is_32bit': None,
                        'variant': None,
                        'error': str(e),
                    }
                    is_omf = False
            else:
                output = {
                    'valid': False,
                    'is_library': None,
                    'is_32bit': None,
                    'variant': None,
                }

            print(json.dumps(output, indent=args.json_indent))
            sys.exit(0 if is_omf else 1)
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(2)

    # Scan mode for embedded OMF
    if args.scan:
        try:
            with open(args.file, 'rb') as f:
                data = f.read()
            candidates = list(scan_for_omf(data, min_confidence=args.min_confidence))
            if args.json:
                output = {
                    'file': args.file,
                    'file_size': len(data),
                    'candidates': [
                        {
                            'offset': c.offset,
                            'offset_hex': f"0x{c.offset:X}",
                            'header_type': c.header_type,
                            'confidence': c.confidence,
                            'description': c.description,
                            'estimated_size': c.estimated_size
                        }
                        for c in candidates
                    ]
                }
                print(json.dumps(output, indent=args.json_indent))
            else:
                print(f"Scanning {args.file} ({len(data)} bytes)")
                print(f"Found {len(candidates)} OMF structure(s):\n")
                for c in candidates:
                    size_info = f", ~{c.estimated_size} bytes" if c.estimated_size else ""
                    print(f"  0x{c.offset:08X}: {c.description}")
                    print(f"              confidence={c.confidence:.0%}{size_info}")
            sys.exit(0)
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(2)

    # Pattern scan mode
    if args.scan_patterns:
        try:
            with open(args.file, 'rb') as f:
                data = f.read()
            matches = list(scan_for_patterns(data))
            if args.json:
                output = {
                    'file': args.file,
                    'file_size': len(data),
                    'matches': [
                        {
                            'pattern': name,
                            'offset': offset,
                            'offset_hex': f"0x{offset:X}",
                            'match': match.hex()
                        }
                        for name, offset, match in matches
                    ]
                }
                print(json.dumps(output, indent=args.json_indent))
            else:
                print(f"Scanning {args.file} ({len(data)} bytes)")
                print(f"Available patterns: {', '.join(GREP_PATTERNS.keys())}")
                print(f"Found {len(matches)} match(es):\n")
                for name, offset, match in matches:
                    preview = match[:20].hex() + ('...' if len(match) > 20 else '')
                    print(f"  0x{offset:08X}: {name}")
                    print(f"              {preview}")
            sys.exit(0)
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(2)

    try:
        omf = OMFFile(args.file)
        omf.load()
        omf.scan()

        omf.parse()

        if args.json:
            json_formatter = JSONFormatter(indent=args.json_indent)
            print(json_formatter.format_file(omf, include_raw=args.include_raw))
        else:
            human_formatter = HumanFormatter()

            print(human_formatter.format_file_header(omf))

            for result in omf.parsed_records:
                print(human_formatter.format_result(result))

            if omf.is_library and omf.lib_dict_offset > 0:
                lib_dict, ext_dict = parse_library_dictionary(omf)
                if lib_dict:
                    print(f"\n[{omf.lib_dict_offset:06X}] === LIBRARY DICTIONARY ===")
                    print(human_formatter._format_ParsedLibDict(lib_dict))
                if ext_dict:
                    ext_offset = omf.lib_dict_offset + (omf.lib_dict_blocks * 512)
                    print(f"\n[{ext_offset:06X}] === EXTENDED DICTIONARY ===")
                    print(human_formatter._format_ParsedExtDict(ext_dict))

            print(human_formatter.format_summary(omf))

    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
