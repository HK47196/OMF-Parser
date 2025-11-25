"""OMF constants and record type definitions."""


# OMF Record Type Definitions
RECORD_NAMES = {
    # Obsolete Intel 8086 Records (Appendix 3)
    0x6E: "RHEADR",      # R-Module Header Record
    0x70: "REGINT",      # Register Initialization Record
    0x72: "REDATA",      # Relocatable Enumerated Data Record
    0x74: "RIDATA",      # Relocatable Iterated Data Record
    0x76: "OVLDEF",      # Overlay Definition Record
    0x78: "ENDREC",      # End Record
    0x7A: "BLKDEF",      # Block Definition Record
    0x7C: "BLKEND",      # Block End Record
    0x7E: "DEBSYM",      # Debug Symbols Record

    # Standard OMF Records
    0x80: "THEADR",      # Translator Header Record
    0x82: "LHEADR",      # Library Module Header Record
    0x84: "PEDATA",      # Physical Enumerated Data (obsolete)
    0x86: "PIDATA",      # Physical Iterated Data (obsolete)
    0x88: "COMENT",      # Comment Record
    0x8A: "MODEND",      # Module End Record (16-bit)
    0x8B: "MODEND32",    # Module End Record (32-bit)
    0x8C: "EXTDEF",      # External Names Definition Record
    0x8E: "TYPDEF",      # Type Definition Record (obsolete)

    0x90: "PUBDEF",      # Public Names Definition Record (16-bit)
    0x91: "PUBDEF32",    # Public Names Definition Record (32-bit)
    0x92: "LOCSYM",      # Local Symbols Record (obsolete)
    0x94: "LINNUM",      # Line Numbers Record (16-bit)
    0x95: "LINNUM32",    # Line Numbers Record (32-bit)
    0x96: "LNAMES",      # List of Names Record
    0x98: "SEGDEF",      # Segment Definition Record (16-bit)
    0x99: "SEGDEF32",    # Segment Definition Record (32-bit)
    0x9A: "GRPDEF",      # Group Definition Record
    0x9C: "FIXUPP",      # Fixup Record (16-bit)
    0x9D: "FIXUPP32",    # Fixup Record (32-bit)
    0x9E: "UNNAMED",     # Unnamed record (never defined)

    0xA0: "LEDATA",      # Logical Enumerated Data Record (16-bit)
    0xA1: "LEDATA32",    # Logical Enumerated Data Record (32-bit)
    0xA2: "LIDATA",      # Logical Iterated Data Record (16-bit)
    0xA3: "LIDATA32",    # Logical Iterated Data Record (32-bit)

    # Obsolete Intel Library Records (conflict with MS usage)
    0xA4: "LIBHED",      # Library Header Record (obsolete Intel)
    0xA6: "LIBNAM",      # Library Module Names Record (obsolete Intel)
    0xA8: "LIBLOC",      # Library Module Locations Record (obsolete Intel)
    0xAA: "LIBDIC",      # Library Dictionary Record (obsolete Intel)

    # Microsoft Extensions
    0xB0: "COMDEF",      # Communal Names Definition Record
    0xB2: "BAKPAT",      # Backpatch Record (16-bit)
    0xB3: "BAKPAT32",    # Backpatch Record (32-bit)
    0xB4: "LEXTDEF",     # Local External Names Definition Record
    0xB5: "LEXTDEF2",    # Local External Names Definition Record (alt)
    0xB6: "LPUBDEF",     # Local Public Names Definition Record (16-bit)
    0xB7: "LPUBDEF32",   # Local Public Names Definition Record (32-bit)
    0xB8: "LCOMDEF",     # Local Communal Names Definition Record
    0xBC: "CEXTDEF",     # COMDAT External Names Definition Record

    0xC2: "COMDAT",      # Initialized Communal Data Record (16-bit)
    0xC3: "COMDAT32",    # Initialized Communal Data Record (32-bit)
    0xC4: "LINSYM",      # Symbol Line Numbers Record (16-bit)
    0xC5: "LINSYM32",    # Symbol Line Numbers Record (32-bit)
    0xC6: "ALIAS",       # Alias Definition Record
    0xC8: "NBKPAT",      # Named Backpatch Record (16-bit)
    0xC9: "NBKPAT32",    # Named Backpatch Record (32-bit)
    0xCA: "LLNAMES",     # Local Logical Names Definition Record
    0xCC: "VERNUM",      # OMF Version Number Record
    0xCE: "VENDEXT",     # Vendor-specific OMF Extension Record

    # Library Records (Microsoft format)
    0xF0: "LIBHDR",      # Library Header Record
    0xF1: "LIBEND",      # Library End Record
}


# Comment Class Definitions
COMMENT_CLASSES = {
    0x00: "Translator",
    0x01: "Intel Copyright",
    0x81: "Library Specifier (obsolete)",
    0x9C: "MS-DOS Version (obsolete)",
    0x9D: "Memory Model",
    0x9E: "DOSSEG",
    0x9F: "Default Library Search",
    0xA0: "OMF Extensions",
    0xA1: "New OMF Extension",
    0xA2: "Link Pass Separator",
    0xA3: "LIBMOD",
    0xA4: "EXESTR",
    0xA6: "INCERR",
    0xA7: "NOPAD",
    0xA8: "WKEXT",
    0xA9: "LZEXT",
    0xAA: "Easy OMF",
    0xB0: "Unknown (32-bit linker extension)",
    0xB1: "Unknown (32-bit linker extension)",
    0xDA: "Comment",
    0xDB: "Compiler",
    0xDC: "Date",
    0xDD: "Timestamp",
    0xDF: "User",
    0xE9: "Dependency File (Borland)",
    0xFF: "Command Line (QuickC)",
}


# A0 Comment Subtypes (OMF Extensions)
A0_SUBTYPES = {
    0x01: "IMPDEF",
    0x02: "EXPDEF",
    0x03: "INCDEF",
    0x04: "Protected Memory Library",
    0x05: "LNKDIR",
    0x06: "Big-endian",
    0x07: "PRECOMP",
}


# Reserved segment names (Appendix 1)
RESERVED_SEGMENTS = {"$$TYPES", "$$SYMBOLS", "$$IMPORT"}


# Segment alignment types
ALIGN_NAMES = [
    "Absolute", "Byte", "Word", "Paragraph",
    "Page (256-byte Intel / 4K IBM)", "DWord", "LTL(6)", "Undefined(7)"
]


# Segment combine types
COMBINE_NAMES = [
    "Private", "Reserved(1) [Intel: Common]", "Public", "Reserved(3)",
    "Public(4)", "Stack", "Common", "Public(7)"
]


# COMDAT Selection types
COMDAT_SELECTION_NAMES = {
    0x00: "No Match",
    0x01: "Pick Any",
    0x02: "Same Size",
    0x03: "Exact Match",
}


# COMDAT Allocation types
COMDAT_ALLOCATION_NAMES = {
    0x00: "Explicit",
    0x01: "Far Code (CODE16)",
    0x02: "Far Data (DATA16)",
    0x03: "Code32",
    0x04: "Data32",
}


# COMDAT Alignment types
COMDAT_ALIGN_NAMES = {
    0: "FromSEGDEF", 1: "Byte", 2: "Word", 3: "Para",
    4: "Page", 5: "DWord"
}


# FIXUPP Frame methods
FRAME_METHOD_NAMES = [
    "F0:SEGDEF", "F1:GRPDEF", "F2:EXTDEF", "F3:FrameNum",
    "F4:Location", "F5:Target", "F6:Invalid", "F7:?"
]


# FIXUPP Target methods
TARGET_METHOD_NAMES = [
    "T0:SEGDEF", "T1:GRPDEF", "T2:EXTDEF", "T3:FrameNum",
    "T4:SEGDEF(0)", "T5:GRPDEF(0)", "T6:EXTDEF(0)", "T7:?"
]


# BAKPAT Location types
BAKPAT_LOCATION_NAMES = {
    0: "Byte(8)",
    1: "Word(16)",
    2: "DWord(32)",
}


# Intel 8086 OMF register constants
REGISTER_NAMES = {
    0: "CS", 1: "DS", 2: "SS", 3: "ES", 4: "IP", 5: "SP"
}


# Variable type names for TYPDEF
VAR_TYPE_NAMES = {
    0x77: "Array",
    0x79: "Structure",
    0x7B: "Scalar"
}


KNOWN_VENDORS = {
    0: "TIS (reserved)",
}
