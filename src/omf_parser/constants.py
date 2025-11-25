"""OMF constants and record type definitions."""

from enum import IntEnum, unique


@unique
class RecordType(IntEnum):
    """OMF record type identifiers."""

    # Obsolete Intel 8086 Records (Appendix 3)
    RHEADR = 0x6E
    REGINT = 0x70
    REDATA = 0x72
    RIDATA = 0x74
    OVLDEF = 0x76
    ENDREC = 0x78
    BLKDEF = 0x7A
    BLKEND = 0x7C
    DEBSYM = 0x7E

    # Standard OMF Records
    THEADR = 0x80
    LHEADR = 0x82
    PEDATA = 0x84
    PIDATA = 0x86
    COMENT = 0x88
    MODEND = 0x8A
    MODEND32 = 0x8B
    EXTDEF = 0x8C
    TYPDEF = 0x8E
    PUBDEF = 0x90
    PUBDEF32 = 0x91
    LOCSYM = 0x92
    LINNUM = 0x94
    LINNUM32 = 0x95
    LNAMES = 0x96
    SEGDEF = 0x98
    SEGDEF32 = 0x99
    GRPDEF = 0x9A
    FIXUPP = 0x9C
    FIXUPP32 = 0x9D
    LEDATA = 0xA0
    LEDATA32 = 0xA1
    LIDATA = 0xA2
    LIDATA32 = 0xA3

    # Obsolete Intel Library Records
    LIBHED = 0xA4
    LIBNAM = 0xA6
    LIBLOC = 0xA8
    LIBDIC = 0xAA

    # Microsoft Extensions
    COMDEF = 0xB0
    BAKPAT = 0xB2
    BAKPAT32 = 0xB3
    LEXTDEF = 0xB4
    LEXTDEF2 = 0xB5
    LPUBDEF = 0xB6
    LPUBDEF32 = 0xB7
    LCOMDEF = 0xB8
    CEXTDEF = 0xBC
    COMDAT = 0xC2
    COMDAT32 = 0xC3
    LINSYM = 0xC4
    LINSYM32 = 0xC5
    ALIAS = 0xC6
    NBKPAT = 0xC8
    NBKPAT32 = 0xC9
    LLNAMES = 0xCA
    VERNUM = 0xCC
    VENDEXT = 0xCE

    # Library Records (Microsoft format)
    LIBHDR = 0xF0
    LIBEND = 0xF1

    # Extended Dictionary marker
    EXTDICT = 0xF2

    @property
    def is_32bit(self) -> bool:
        """Check if this is a 32-bit variant."""
        return self.name.endswith("32")

    @property
    def base_type(self) -> "RecordType":
        """Get the 16-bit base type (e.g., MODEND32 → MODEND)."""
        if self.is_32bit:
            return RecordType(self.value - 1)
        return self


class CommentClass(IntEnum):
    """COMENT record class types.

    Note: No @unique - different vendors may use overlapping class numbers.
    """
    TRANSLATOR = 0x00
    COPYRIGHT = 0x01
    LIBSPEC = 0x81
    WAT_PROC_MODEL = 0x9B
    MSDOS_VERSION = 0x9C
    MS_PROC_MODEL = 0x9D
    DOSSEG = 0x9E
    DEFAULT_LIBRARY = 0x9F
    OMF_EXTENSIONS = 0xA0
    NEW_OMF = 0xA1
    LINK_PASS = 0xA2
    LIBMOD = 0xA3
    EXESTR = 0xA4
    INCERR = 0xA6
    NOPAD = 0xA7
    WKEXT = 0xA8
    LZEXT = 0xA9
    EASY_OMF = 0xAA
    LINKER_32BIT = 0xB0
    LINKER_32BIT_ALT = 0xB1
    COMMENT = 0xDA
    COMPILER = 0xDB
    DATE = 0xDC
    TIMESTAMP = 0xDD
    USER = 0xDF
    DEPENDENCY = 0xE9
    DISASM_DIRECTIVE = 0xFD
    LINKER_DIRECTIVE = 0xFE
    COMMANDLINE = 0xFF


@unique
class A0Subtype(IntEnum):
    """OMF Extensions (A0) comment subtypes."""
    IMPDEF = 0x01
    EXPDEF = 0x02
    INCDEF = 0x03
    PROTECTED_MEMORY = 0x04
    LNKDIR = 0x05
    BIG_ENDIAN = 0x06
    PRECOMP = 0x07


@unique
class GrpdefComponent(IntEnum):
    """GRPDEF component type markers."""
    SEGMENT_INDEX = 0xFF
    EXTERNAL_INDEX = 0xFE
    SEGDEF_INDICES = 0xFD
    LTL = 0xFB
    ABSOLUTE = 0xFA


@unique
class ComdefType(IntEnum):
    """COMDEF data type codes."""
    FAR = 0x61
    NEAR = 0x62


@unique
class TypdefLeaf(IntEnum):
    """TYPDEF leaf type codes."""
    FAR = 0x61
    NEAR = 0x62


class SegdefFlags:
    """SEGDEF ACBP field bit positions and masks."""
    ALIGN_SHIFT = 5
    COMBINE_SHIFT = 2
    ALIGN_MASK = 0x07
    COMBINE_MASK = 0x07
    BIG_MASK = 0x01
    USE32_MASK = 0x01
    ACCESS_TYPE_MASK = 0x03


class ComentFlags:
    """COMENT flag byte bit positions."""
    NP = 0x80  # No Purge
    NL = 0x40  # No List


class ModendFlags:
    """MODEND flag byte bit positions and masks."""
    MAIN = 0x80
    START = 0x40
    RELOCATABLE = 0x01
    FRAME_SHIFT = 4
    FRAME_MASK = 0x07
    P_BIT_MASK = 0x04
    P_BIT_SHIFT = 2
    TARGET_MASK = 0x03


class FixuppFlags:
    """FIXUPP field bit positions and masks."""
    # LOCAT byte
    IS_FIXUP = 0x80
    MODE_MASK = 0x40
    MODE_SHIFT = 6
    LOC_TYPE_MASK = 0x0F
    LOC_TYPE_SHIFT = 2
    OFFSET_HIGH_MASK = 0x03

    # THREAD byte
    THREAD_IS_FRAME = 0x40
    THREAD_METHOD_SHIFT = 2
    THREAD_METHOD_MASK = 0x07
    THREAD_NUM_MASK = 0x03

    # FIXDAT byte
    F_BIT = 0x80
    FRAME_SHIFT = 4
    FRAME_MASK = 0x07
    T_BIT = 0x08
    P_BIT = 0x04
    P_BIT_SHIFT = 2
    TARGET_MASK = 0x03


class ComdatFlags:
    """COMDAT flag byte bit positions and masks."""
    CONTINUATION = 0x01
    ITERATED = 0x02
    LOCAL = 0x04
    DATA_IN_CODE = 0x08
    SELECTION_SHIFT = 4
    SELECTION_MASK = 0x0F
    ALLOCATION_MASK = 0x0F


class ExpdefFlags:
    """EXPDEF flag byte bit positions and masks."""
    ORDINAL = 0x80
    RESIDENT = 0x40
    NODATA = 0x20
    PARM_COUNT_MASK = 0x1F


class LnkdirFlags:
    """LNKDIR flag byte bit positions."""
    NEW_EXE = 0x01
    OMIT_PUBLICS = 0x02
    RUN_MPC = 0x04


class IndexFlags:
    """OMF index field bit positions."""
    TWO_BYTE_FLAG = 0x80
    HIGH_MASK = 0x7F


class VarlenMarkers:
    """Variable-length integer markers (COMDEF/TYPDEF)."""
    MAX_1BYTE = 0x80
    MARKER_2BYTE = 0x81
    MARKER_3BYTE = 0x84
    MARKER_4BYTE = 0x88


class LibraryConsts:
    """Library format constants."""
    DICT_BLOCK_SIZE = 512
    DICT_BUCKET_COUNT = 37
    FLAG_CASE_SENSITIVE = 0x01


class SegmentSize:
    """Segment size limits."""
    SIZE_64K = 0x10000
    SIZE_4GB = 0x100000000


class SignedConversion:
    """Signed integer conversion constants."""
    THRESHOLD_16BIT = 0x8000
    OFFSET_16BIT = 0x10000


class AsciiRange:
    """ASCII range constants for hex display."""
    PRINTABLE_MIN = 32
    PRINTABLE_MAX = 127


COMDEF_BORLAND_MAX = 0x5F

RECORD_NAMES: dict[int, str] = {
    # Obsolete Intel 8086 Records (Appendix 3)
    RecordType.RHEADR: "RHEADR",
    RecordType.REGINT: "REGINT",
    RecordType.REDATA: "REDATA",
    RecordType.RIDATA: "RIDATA",
    RecordType.OVLDEF: "OVLDEF",
    RecordType.ENDREC: "ENDREC",
    RecordType.BLKDEF: "BLKDEF",
    RecordType.BLKEND: "BLKEND",
    RecordType.DEBSYM: "DEBSYM",

    # Standard OMF Records
    RecordType.THEADR: "THEADR",
    RecordType.LHEADR: "LHEADR",
    RecordType.PEDATA: "PEDATA",
    RecordType.PIDATA: "PIDATA",
    RecordType.COMENT: "COMENT",
    RecordType.MODEND: "MODEND",
    RecordType.MODEND32: "MODEND32",
    RecordType.EXTDEF: "EXTDEF",
    RecordType.TYPDEF: "TYPDEF",
    RecordType.PUBDEF: "PUBDEF",
    RecordType.PUBDEF32: "PUBDEF32",
    RecordType.LOCSYM: "LOCSYM",
    RecordType.LINNUM: "LINNUM",
    RecordType.LINNUM32: "LINNUM32",
    RecordType.LNAMES: "LNAMES",
    RecordType.SEGDEF: "SEGDEF",
    RecordType.SEGDEF32: "SEGDEF32",
    RecordType.GRPDEF: "GRPDEF",
    RecordType.FIXUPP: "FIXUPP",
    RecordType.FIXUPP32: "FIXUPP32",
    RecordType.LEDATA: "LEDATA",
    RecordType.LEDATA32: "LEDATA32",
    RecordType.LIDATA: "LIDATA",
    RecordType.LIDATA32: "LIDATA32",

    # Obsolete Intel Library Records
    RecordType.LIBHED: "LIBHED",
    RecordType.LIBNAM: "LIBNAM",
    RecordType.LIBLOC: "LIBLOC",
    RecordType.LIBDIC: "LIBDIC",

    # Microsoft Extensions
    RecordType.COMDEF: "COMDEF",
    RecordType.BAKPAT: "BAKPAT",
    RecordType.BAKPAT32: "BAKPAT32",
    RecordType.LEXTDEF: "LEXTDEF",
    RecordType.LEXTDEF2: "LEXTDEF2",
    RecordType.LPUBDEF: "LPUBDEF",
    RecordType.LPUBDEF32: "LPUBDEF32",
    RecordType.LCOMDEF: "LCOMDEF",
    RecordType.CEXTDEF: "CEXTDEF",
    RecordType.COMDAT: "COMDAT",
    RecordType.COMDAT32: "COMDAT32",
    RecordType.LINSYM: "LINSYM",
    RecordType.LINSYM32: "LINSYM32",
    RecordType.ALIAS: "ALIAS",
    RecordType.NBKPAT: "NBKPAT",
    RecordType.NBKPAT32: "NBKPAT32",
    RecordType.LLNAMES: "LLNAMES",
    RecordType.VERNUM: "VERNUM",
    RecordType.VENDEXT: "VENDEXT",

    # Library Records
    RecordType.LIBHDR: "LIBHDR",
    RecordType.LIBEND: "LIBEND",
}

COMMENT_CLASSES: dict[int, str] = {
    CommentClass.TRANSLATOR: "Translator",
    CommentClass.COPYRIGHT: "Intel Copyright",
    CommentClass.LIBSPEC: "Library Specifier (obsolete)",
    CommentClass.WAT_PROC_MODEL: "Watcom Processor/Model",
    CommentClass.MSDOS_VERSION: "MS-DOS Version (obsolete)",
    CommentClass.MS_PROC_MODEL: "MS Processor/Model",
    CommentClass.DOSSEG: "DOSSEG",
    CommentClass.DEFAULT_LIBRARY: "Default Library Search",
    CommentClass.OMF_EXTENSIONS: "OMF Extensions",
    CommentClass.NEW_OMF: "New OMF Extension",
    CommentClass.LINK_PASS: "Link Pass Separator",
    CommentClass.LIBMOD: "LIBMOD",
    CommentClass.EXESTR: "EXESTR",
    CommentClass.INCERR: "INCERR",
    CommentClass.NOPAD: "NOPAD",
    CommentClass.WKEXT: "WKEXT",
    CommentClass.LZEXT: "LZEXT",
    CommentClass.EASY_OMF: "Easy OMF",
    CommentClass.LINKER_32BIT: "32-bit Linker Extension",
    CommentClass.LINKER_32BIT_ALT: "32-bit Linker Extension",
    CommentClass.COMMENT: "Comment",
    CommentClass.COMPILER: "Compiler",
    CommentClass.DATE: "Date",
    CommentClass.TIMESTAMP: "Timestamp",
    CommentClass.USER: "User",
    CommentClass.DEPENDENCY: "Dependency File (Borland)",
    CommentClass.DISASM_DIRECTIVE: "Watcom Disassembler Directive",
    CommentClass.LINKER_DIRECTIVE: "Watcom Linker Directive",
    CommentClass.COMMANDLINE: "Command Line (QuickC)",
}

A0_SUBTYPES: dict[int, str] = {
    A0Subtype.IMPDEF: "IMPDEF",
    A0Subtype.EXPDEF: "EXPDEF",
    A0Subtype.INCDEF: "INCDEF",
    A0Subtype.PROTECTED_MEMORY: "Protected Memory Library",
    A0Subtype.LNKDIR: "LNKDIR",
    A0Subtype.BIG_ENDIAN: "Big-endian",
    A0Subtype.PRECOMP: "PRECOMP",
}


RESERVED_SEGMENTS = {"$$TYPES", "$$SYMBOLS", "$$IMPORT"}

ALIGN_NAMES = [
    "Absolute", "Byte", "Word", "Paragraph",
    "Page (256-byte Intel / 4K IBM)", "DWord", "LTL(6)", "Undefined(7)"
]

COMBINE_NAMES = [
    "Private", "Reserved(1) [Intel: Common]", "Public", "Reserved(3)",
    "Public(4)", "Stack", "Common", "Public(7)"
]


COMDAT_SELECTION_NAMES: dict[int, str] = {
    0x00: "No Match",
    0x01: "Pick Any",
    0x02: "Same Size",
    0x03: "Exact Match",
}

COMDAT_ALLOCATION_NAMES: dict[int, str] = {
    0x00: "Explicit",
    0x01: "Far Code (CODE16)",
    0x02: "Far Data (DATA16)",
    0x03: "Code32",
    0x04: "Data32",
}

COMDAT_ALIGN_NAMES: dict[int, str] = {
    0: "FromSEGDEF", 1: "Byte", 2: "Word", 3: "Para",
    4: "Page", 5: "DWord"
}


FRAME_METHOD_NAMES = [
    "F0:SEGDEF", "F1:GRPDEF", "F2:EXTDEF", "F3:FrameNum",
    "F4:Location", "F5:Target", "F6:Invalid", "F7:?"
]

TARGET_METHOD_NAMES = [
    "T0:SEGDEF", "T1:GRPDEF", "T2:EXTDEF", "T3:FrameNum",
    "T4:SEGDEF(0)", "T5:GRPDEF(0)", "T6:EXTDEF(0)", "T7:?"
]


BAKPAT_LOCATION_NAMES: dict[int, str] = {
    0: "Byte(8)",
    1: "Word(16)",
    2: "DWord(32)",
}


REGISTER_NAMES: dict[int, str] = {
    0: "CS", 1: "DS", 2: "SS", 3: "ES", 4: "IP", 5: "SP"
}

VAR_TYPE_NAMES: dict[int, str] = {
    0x77: "Array",
    0x79: "Structure",
    0x7B: "Scalar"
}


KNOWN_VENDORS: dict[int, str] = {
    0: "TIS (reserved)",
}
