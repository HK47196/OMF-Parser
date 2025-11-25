"""Command-line interface for OMF parser."""

import sys
import argparse
from .file import OMFFile


def main():
    parser = argparse.ArgumentParser(
        description='Parse and dump OMF object files and libraries.'
    )
    parser.add_argument('file', help='Path to OMF file (.obj or .lib)')
    parser.add_argument('--version', action='version', version='omf_parser 2.0')

    args = parser.parse_args()

    try:
        omf = OMFFile(args.file)
        omf.dump()
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
