"""Intel/TIS standard COMENT class handlers."""

from . import coment_class
from ..parsing import format_hex_with_ascii
from ..constants import A0_SUBTYPES


@coment_class(0x00)
def handle_translator(omf, sub, flags, text):
    """Translator - identifies compiler/assembler."""
    if text:
        try:
            print(f"  Translator: {text.decode('ascii', errors='replace')}")
        except:
            print(f"  Translator: {format_hex_with_ascii(text)}")


@coment_class(0x01)
def handle_copyright(omf, sub, flags, text):
    """Intel Copyright."""
    if text:
        try:
            print(f"  Copyright: {text.decode('ascii', errors='replace')}")
        except:
            print(f"  Copyright: {format_hex_with_ascii(text)}")


@coment_class(0x81)
def handle_libspec(omf, sub, flags, text):
    """Library Specifier (obsolete)."""
    print("  [Obsolete] Library Specifier")
    if text:
        try:
            print(f"  Library: {text.decode('ascii', errors='replace')}")
        except:
            print(f"  Library: {format_hex_with_ascii(text)}")


@coment_class(0x9E)
def handle_dosseg(omf, sub, flags, text):
    """DOSSEG - DOS segment ordering."""
    print("  DOSSEG: Use DOS segment ordering convention")


@coment_class(0xA1)
def handle_new_omf(omf, sub, flags, text):
    """New OMF Extension."""
    print("  New OMF Extension marker")
    if text:
        print(f"  Data: {format_hex_with_ascii(text)}")


@coment_class(0xA2)
def handle_link_pass(omf, sub, flags, text):
    """Link Pass Separator."""
    print("  Link Pass Separator")
    if text and len(text) >= 1:
        print(f"  Pass: {text[0]}")


@coment_class(0xA3)
def handle_libmod(omf, sub, flags, text):
    """LIBMOD - Library Module Name."""
    if text:
        try:
            print(f"  Library Module: {text.decode('ascii', errors='replace')}")
        except:
            print(f"  Library Module: {format_hex_with_ascii(text)}")


@coment_class(0xA4)
def handle_exestr(omf, sub, flags, text):
    """EXESTR - Executable String."""
    if text:
        try:
            print(f"  Exe String: {text.decode('ascii', errors='replace')}")
        except:
            print(f"  Exe String: {format_hex_with_ascii(text)}")


@coment_class(0xA6)
def handle_incerr(omf, sub, flags, text):
    """INCERR - Incremental Compilation Error."""
    print("  Incremental Compilation Error - forces full recompile")


@coment_class(0xA7)
def handle_nopad(omf, sub, flags, text):
    """NOPAD - No Segment Padding."""
    print("  NOPAD: Do not pad segments")


@coment_class(0xA8)
def handle_wkext(omf, sub, flags, text):
    """WKEXT - Weak Extern."""
    print("  Weak Extern definitions:")
    pos = 0
    while pos < len(text) - 1:
        weak_idx = text[pos]
        default_idx = text[pos + 1]
        print(f"    Weak Ext#{weak_idx} -> Default Ext#{default_idx}")
        pos += 2


@coment_class(0xA9)
def handle_lzext(omf, sub, flags, text):
    """LZEXT - Lazy Extern."""
    print("  Lazy Extern definitions:")
    pos = 0
    while pos < len(text) - 1:
        lazy_idx = text[pos]
        default_idx = text[pos + 1]
        print(f"    Lazy Ext#{lazy_idx} -> Default Ext#{default_idx}")
        pos += 2


@coment_class(0xAA)
def handle_easy_omf(omf, sub, flags, text):
    """Easy OMF-386 marker (PharLap)."""
    omf.features.add('easy_omf')
    omf.features.add('pharlap')
    print("  Easy OMF-386: 32-bit extensions enabled")
    if text:
        try:
            print(f"  Marker: {text.decode('ascii', errors='replace')}")
        except:
            print(f"  Marker: {format_hex_with_ascii(text)}")


@coment_class(0xA0)
def handle_omf_extensions(omf, sub, flags, text):
    """OMF Extensions (A0 subtypes)."""
    if not text:
        return

    subtype = text[0]
    subtype_name = A0_SUBTYPES.get(subtype, f"Unknown(0x{subtype:02X})")
    print(f"  A0 Subtype: {subtype_name}")

    remaining = text[1:]

    if subtype == 0x01:  # IMPDEF
        _handle_impdef(omf, remaining)
    elif subtype == 0x02:  # EXPDEF
        _handle_expdef(omf, remaining)
    elif subtype == 0x03:  # INCDEF
        _handle_incdef(omf, remaining)
    elif subtype == 0x04:  # Protected Memory Library
        print("    DLL uses protected memory (_loadds)")
    elif subtype == 0x05:  # LNKDIR
        _handle_lnkdir(omf, remaining)
    elif subtype == 0x06:  # Big-endian
        omf.features.add('big_endian')
        print("    Target is big-endian architecture")
    elif subtype == 0x07:  # PRECOMP
        print("    $$TYPES should use sstPreComp instead of sstTypes")
    else:
        omf.add_warning(f"    [!] Unknown A0 subtype 0x{subtype:02X}")
        if remaining:
            print(f"    Data: {format_hex_with_ascii(remaining)}")


def _handle_impdef(omf, data):
    """Handle IMPDEF subtype."""
    if len(data) < 3:
        return

    ord_flag = data[0]
    pos = 1

    # Parse internal name
    int_name_len = data[pos]
    int_name = data[pos + 1:pos + 1 + int_name_len].decode('ascii', errors='replace')
    pos += 1 + int_name_len

    # Parse module name
    if pos >= len(data):
        return
    mod_name_len = data[pos]
    mod_name = data[pos + 1:pos + 1 + mod_name_len].decode('ascii', errors='replace')
    pos += 1 + mod_name_len

    print(f"    Internal Name: {int_name}")
    print(f"    Module Name: {mod_name}")

    if ord_flag == 0:
        if pos < len(data):
            entry_len = data[pos]
            if entry_len == 0:
                print(f"    Entry: (same as internal)")
            else:
                entry_name = data[pos + 1:pos + 1 + entry_len].decode('ascii', errors='replace')
                print(f"    Entry Name: {entry_name}")
    else:
        if pos + 1 < len(data):
            ordinal = data[pos] | (data[pos + 1] << 8)
            print(f"    Ordinal: {ordinal}")


def _handle_expdef(omf, data):
    """Handle EXPDEF subtype."""
    if len(data) < 2:
        return

    exp_flag = data[0]
    pos = 1

    by_ordinal = (exp_flag & 0x80) != 0
    resident = (exp_flag & 0x40) != 0
    no_data = (exp_flag & 0x20) != 0
    parm_count = exp_flag & 0x1F

    # Parse exported name
    exp_name_len = data[pos]
    exp_name = data[pos + 1:pos + 1 + exp_name_len].decode('ascii', errors='replace')
    pos += 1 + exp_name_len

    # Parse internal name
    if pos >= len(data):
        return
    int_name_len = data[pos]
    int_name = data[pos + 1:pos + 1 + int_name_len].decode('ascii', errors='replace') if int_name_len else ""
    pos += 1 + int_name_len

    print(f"    Exported Name: {exp_name}")
    if int_name:
        print(f"    Internal Name: {int_name}")
    else:
        print(f"    Internal Name: (same as exported)")
    print(f"    By Ordinal: {by_ordinal}, Resident: {resident}, NoData: {no_data}, Parms: {parm_count}")

    if by_ordinal and pos + 1 < len(data):
        ordinal = data[pos] | (data[pos + 1] << 8)
        print(f"    Export Ordinal: {ordinal}")


def _handle_incdef(omf, data):
    """Handle INCDEF subtype."""
    if len(data) < 4:
        return

    extdef_delta = data[0] | (data[1] << 8)
    linnum_delta = data[2] | (data[3] << 8)

    if extdef_delta >= 0x8000:
        extdef_delta -= 0x10000
    if linnum_delta >= 0x8000:
        linnum_delta -= 0x10000

    print(f"    EXTDEF Delta: {extdef_delta}")
    print(f"    LINNUM Delta: {linnum_delta}")


def _handle_lnkdir(omf, data):
    """Handle LNKDIR subtype."""
    if len(data) < 3:
        return

    bit_flags = data[0]
    pcode_ver = data[1]
    cv_ver = data[2]

    print(f"    Bit Flags: 0x{bit_flags:02X}")
    if bit_flags & 0x01:
        print("      - Output new .EXE format")
    if bit_flags & 0x02:
        print("      - Omit CodeView $PUBLICS")
    if bit_flags & 0x04:
        print("      - Run MPC utility")
    print(f"    Pseudocode Version: {pcode_ver}")
    print(f"    CodeView Version: {cv_ver}")
