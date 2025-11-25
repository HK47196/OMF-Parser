"""Command-line interface for OMF parser."""

import sys
import argparse
from .file import OMFFile
from .formatters import HumanFormatter, JSONFormatter
from .records.library import parse_library_dictionary


def main():
    parser = argparse.ArgumentParser(
        description='Parse and dump OMF object files and libraries.'
    )
    parser.add_argument('file', help='Path to OMF file (.obj or .lib)')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON instead of human-readable text')
    parser.add_argument('--json-indent', type=int, default=2,
                        help='JSON indentation level (default: 2)')
    parser.add_argument('--include-raw', action='store_true',
                        help='Include raw record bytes in JSON output')
    parser.add_argument('--version', action='version', version='omf_parser 2.0')

    args = parser.parse_args()

    try:
        omf = OMFFile(args.file)
        omf.load()
        omf.scan()

        if omf.mixed_variants:
            print(f"Error: Library contains modules with mixed variants: {', '.join(sorted(omf.seen_variants))}", file=sys.stderr)
            print("Mixed-variant libraries are not supported.", file=sys.stderr)
            sys.exit(1)

        omf.parse()

        if args.json:
            formatter = JSONFormatter(indent=args.json_indent)
            print(formatter.format_file(omf, include_raw=args.include_raw))
        else:
            formatter = HumanFormatter()

            print(formatter.format_file_header(omf))

            for result in omf.parsed_records:
                print(formatter.format_result(result))

            # Handle library dictionary separately
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
