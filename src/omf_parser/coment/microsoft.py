"""Microsoft COMENT class handlers."""

from . import coment_class
from ..parsing import format_hex_with_ascii


@coment_class(0x9C)
def handle_dos_version(omf, sub, flags, text):
    """MS-DOS Version (obsolete)."""
    print("  [Obsolete] MS-DOS Version")
    if text and len(text) >= 2:
        major = text[0]
        minor = text[1]
        print(f"    Version: {major}.{minor}")


@coment_class(0x9D)
def handle_memory_model(omf, sub, flags, text):
    """Memory Model."""
    if text:
        try:
            model = text.decode('ascii', errors='replace')
            print(f"  Memory Model: {model}")
        except:
            print(f"  Memory Model: {format_hex_with_ascii(text)}")


@coment_class(0x9F)
def handle_default_library(omf, sub, flags, text):
    """Default Library Search."""
    if text:
        try:
            lib_name = text.decode('ascii', errors='replace')
            print(f"  Default Library: {lib_name}")
        except:
            print(f"  Default Library: {format_hex_with_ascii(text)}")


@coment_class(0xDA)
def handle_comment(omf, sub, flags, text):
    """Comment text."""
    if text:
        try:
            print(f"  Comment: {text.decode('ascii', errors='replace')}")
        except:
            print(f"  Comment: {format_hex_with_ascii(text)}")


@coment_class(0xDB)
def handle_compiler(omf, sub, flags, text):
    """Compiler identification."""
    if text:
        try:
            print(f"  Compiler: {text.decode('ascii', errors='replace')}")
        except:
            print(f"  Compiler: {format_hex_with_ascii(text)}")


@coment_class(0xDC)
def handle_date(omf, sub, flags, text):
    """Date stamp."""
    if text:
        try:
            print(f"  Date: {text.decode('ascii', errors='replace')}")
        except:
            print(f"  Date: {format_hex_with_ascii(text)}")


@coment_class(0xDD)
def handle_timestamp(omf, sub, flags, text):
    """Timestamp."""
    if text:
        try:
            print(f"  Timestamp: {text.decode('ascii', errors='replace')}")
        except:
            print(f"  Timestamp: {format_hex_with_ascii(text)}")


@coment_class(0xDF)
def handle_user(omf, sub, flags, text):
    """User-defined comment."""
    if text:
        try:
            print(f"  User: {text.decode('ascii', errors='replace')}")
        except:
            print(f"  User: {format_hex_with_ascii(text)}")


@coment_class(0xE9)
def handle_dependency_file(omf, sub, flags, text):
    """Dependency File (Borland)."""
    if text:
        try:
            print(f"  Dependency: {text.decode('ascii', errors='replace')}")
        except:
            print(f"  Dependency: {format_hex_with_ascii(text)}")


@coment_class(0xFF)
def handle_cmdline(omf, sub, flags, text):
    """Command Line (QuickC)."""
    if text:
        try:
            print(f"  Command Line: {text.decode('ascii', errors='replace')}")
        except:
            print(f"  Command Line: {format_hex_with_ascii(text)}")


@coment_class(0xB0, 0xB1)
def handle_32bit_linker(omf, sub, flags, text):
    """32-bit linker extension."""
    print("  32-bit linker extension")
    if text:
        print(f"  Data: {format_hex_with_ascii(text)}")
