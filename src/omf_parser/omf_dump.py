#!/usr/bin/env python3
"""OMF parser CLI."""

import sys
import os
import argparse

from .omf_parser import OMFCompleteParser
from .constants import MODE_AUTO, MODE_MS, MODE_IBM, MODE_PHARLAP, MODE_NAMES


def main():
    parser_cli = argparse.ArgumentParser(
        description="OMF Complete Parser - Supports ALL OMF record types",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported records:
  - Standard OMF (80H-F1H)
  - Microsoft extensions
  - Obsolete Intel 8086 records (Appendix 3)
  - PharLap extensions
  - Borland extensions
  - Library format with extended dictionary

Architectural Modes:
  auto     - Automatically detect vendor format (default)
  ms       - Microsoft/TIS Standard format
  ibm      - IBM LINK386 format
  pharlap  - PharLap 386|DOS-Extender format
        """
    )

    parser_cli.add_argument('file', help='OMF object file (.obj) or library (.lib) to parse')
    parser_cli.add_argument(
        '--mode',
        choices=['auto', 'ms', 'ibm', 'pharlap'],
        default='auto',
        help='Architectural mode for handling vendor-specific conflicts (default: auto)'
    )

    args = parser_cli.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)

    # Create parser instance
    parser = OMFCompleteParser(args.file)

    # Handle mode selection
    mode_map = {
        'auto': MODE_AUTO,
        'ms': MODE_MS,
        'ibm': MODE_IBM,
        'pharlap': MODE_PHARLAP
    }

    requested_mode = mode_map[args.mode]

    # Load file data for detection
    try:
        with open(args.file, 'rb') as f:
            parser.data = f.read()
            parser.file_size = len(parser.data)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Auto-detect or use explicit mode
    if requested_mode == MODE_AUTO:
        detected = parser.detect_mode()
        parser.target_mode = detected
        print(f"Auto-detected mode: {MODE_NAMES.get(detected, 'Unknown')}")
        print()
    else:
        parser.target_mode = requested_mode

    # Run the parser
    parser.run()


if __name__ == "__main__":
    main()
