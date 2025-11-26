"""OMF constants and record type definitions."""

from enum import Enum, IntEnum, IntFlag, unique
from typing import NamedTuple, overload


class OMFVariant(str, Enum):
    """OMF format variant.

    Variants change how records are parsed (field sizes, extra fields, etc.).
    This is distinct from extensions which add new semantics but use the same parsing.

    - TIS_STANDARD: Baseline OMF-86/286/386 per TIS specification
    - PHARLAP: PharLap Easy OMF-386 (4-byte offsets, SEGDEF access byte)
    - IBM_LINK386: OS/2 2.x+ format (inline names in COMDAT/NBKPAT/LINSYM)
    """
    TIS_STANDARD = "TIS Standard"
    PHARLAP = "PharLap Easy OMF-386"
    IBM_LINK386 = "IBM LINK386"


class EnumValue(NamedTuple):
    """Value for LabeledEnum members."""
    int_val: int
    label: str


class CharEnumValue(NamedTuple):
    """Value for CharLabeledEnum members (character-keyed)."""
    char_val: str
    label: str


class LabeledEnum(Enum):
    """Enum with both integer value and string label.

    Allows construction from int (for parsing) while keeping unique tuple values
    (avoiding Union collision in Pydantic).
    """

    int_val: int
    label: str

    @overload
    def __new__(cls, int_val: int, label: str) -> "LabeledEnum": ...
    @overload
    def __new__(cls, int_val: int) -> "LabeledEnum": ...

    def __new__(cls, int_val: int, label: str | None = None) -> "LabeledEnum":
        if label is None:
            # Lookup by int value - will be handled by _missing_
            raise ValueError("Use enum lookup")
        obj = object.__new__(cls)
        obj._value_ = EnumValue(int_val, label)
        obj.int_val = int_val
        obj.label = label
        return obj

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        int_vals = [m.int_val for m in cls]
        if len(int_vals) != len(set(int_vals)):
            dupes = [v for v in int_vals if int_vals.count(v) > 1]
            raise ValueError(f"{cls.__name__} has duplicate int values: {set(dupes)}")

    @classmethod
    def _missing_(cls, value: object) -> "LabeledEnum | None":
        if isinstance(value, int):
            if value < 0:
                raise ValueError(f"Invalid {cls.__name__} value: {value}")
            for member in cls:
                if member.int_val == value:
                    return member
        return None

    def __str__(self) -> str:
        return self.label


class CharLabeledEnum(Enum):
    """Enum with character value and string label.

    Similar to LabeledEnum but for character-keyed enums (e.g., Watcom fields).
    Allows construction from char (for parsing) while keeping unique tuple values.
    """

    char_val: str
    label: str

    @overload
    def __new__(cls, char_val: str, label: str) -> "CharLabeledEnum": ...
    @overload
    def __new__(cls, char_val: str) -> "CharLabeledEnum": ...

    def __new__(cls, char_val: str, label: str | None = None) -> "CharLabeledEnum":
        if label is None:
            raise ValueError("Use enum lookup")
        obj = object.__new__(cls)
        obj._value_ = CharEnumValue(char_val, label)
        obj.char_val = char_val
        obj.label = label
        return obj

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        char_vals = [m.char_val for m in cls]
        if len(char_vals) != len(set(char_vals)):
            dupes = [v for v in char_vals if char_vals.count(v) > 1]
            raise ValueError(f"{cls.__name__} has duplicate char values: {set(dupes)}")

    @classmethod
    def _missing_(cls, value: object) -> "CharLabeledEnum | None":
        if isinstance(value, str):
            for member in cls:
                if member.char_val == value:
                    return member
        return None

    def __str__(self) -> str:
        return self.label


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

    # TIS OMF 1.1 Extension Records
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


class SegAlignment(LabeledEnum):
    """SEGDEF alignment values (A field in ACBP byte).

    - Absolute: Absolute segment (frame number and offset follow)
    - Byte: Relocatable, byte aligned
    - Word: Relocatable, word (2-byte) aligned
    - Paragraph: Relocatable, paragraph (16-byte) aligned
    - Page: Relocatable, page aligned (256-byte Intel / 4K IBM)
    - DWord: Relocatable, dword (4-byte) aligned
    - LTL(6): Not supported (Intel: LTL paragraph aligned)
    - Undefined(7): Not defined
    """
    ABSOLUTE = EnumValue(0, "Absolute")
    BYTE = EnumValue(1, "Byte")
    WORD = EnumValue(2, "Word")
    PARAGRAPH = EnumValue(3, "Paragraph")
    PAGE = EnumValue(4, "Page (256-byte Intel / 4K IBM)")
    DWORD = EnumValue(5, "DWord")
    LTL = EnumValue(6, "LTL(6)")
    UNDEFINED = EnumValue(7, "Undefined(7)")


class SegCombine(LabeledEnum):
    """SEGDEF combine values (C field in ACBP byte).

    - Private: Do not combine with any other segment
    - Reserved(1) [Intel: Common]: Reserved (Intel 8086 used this for Common)
    - Public: Combine by appending at alignment boundary
    - Reserved(3): Reserved
    - Public(4): Same as Public
    - Stack: Combine as Public, forces byte alignment
    - Common: Combine by overlay using maximum size
    - Public(7): Same as Public
    """
    PRIVATE = EnumValue(0, "Private")
    RESERVED_1 = EnumValue(1, "Reserved(1) [Intel: Common]")
    PUBLIC = EnumValue(2, "Public")
    RESERVED_3 = EnumValue(3, "Reserved(3)")
    PUBLIC_4 = EnumValue(4, "Public(4)")
    STACK = EnumValue(5, "Stack")
    COMMON = EnumValue(6, "Common")
    PUBLIC_7 = EnumValue(7, "Public(7)")


class FixupLocation(LabeledEnum):
    """FIXUPP location types. Some values differ between TIS and PharLap variants.

    - Byte(8): Low-order byte (8-bit displacement or low byte of 16-bit offset)
    - Offset(16): 16-bit offset
    - Segment(16): 16-bit base/selector
    - Ptr(16:16): 32-bit far pointer (16-bit segment:16-bit offset) [PharLap: 16:32]
    - HiByte(8): High-order byte of 16-bit offset
    - Loader-resolved Offset(16): 16-bit loader-resolved offset [PharLap: 32-bit offset]
    - Ptr(16:32) [loc 6]: PharLap 48-bit pointer [TIS: reserved]
    - Offset(32): 32-bit offset
    - Ptr(16:32) [loc 11]: 48-bit far pointer (16-bit segment:32-bit offset)
    - Loader-resolved Offset(32): 32-bit loader-resolved offset
    """
    BYTE = EnumValue(0, "Byte(8)")
    OFFSET_16 = EnumValue(1, "Offset(16)")
    SEGMENT_16 = EnumValue(2, "Segment(16)")
    PTR_16_16 = EnumValue(3, "Ptr(16:16)")
    HIBYTE = EnumValue(4, "HiByte(8)")
    LOADER_OFFSET_16 = EnumValue(5, "Loader-resolved Offset(16)")
    PHARLAP_PTR_16_32 = EnumValue(6, "Ptr(16:32) [loc 6]")
    OFFSET_32 = EnumValue(9, "Offset(32)")
    PTR_16_32 = EnumValue(11, "Ptr(16:32)")
    LOADER_OFFSET_32 = EnumValue(13, "Loader-resolved Offset(32)")


class FrameMethod(LabeledEnum):
    """FIXUPP frame determination methods.

    - F0:SEGDEF: Frame specified by SEGDEF index
    - F1:GRPDEF: Frame specified by GRPDEF index
    - F2:EXTDEF: Frame specified by EXTDEF index
    - F3:FrameNum: Explicit frame number (not supported by linkers)
    - F4:Location: Frame from previous LEDATA/LIDATA segment
    - F5:Target: Frame determined by target
    - F6:Invalid: Invalid/reserved
    """
    SEGDEF = EnumValue(0, "F0:SEGDEF")
    GRPDEF = EnumValue(1, "F1:GRPDEF")
    EXTDEF = EnumValue(2, "F2:EXTDEF")
    FRAME_NUM = EnumValue(3, "F3:FrameNum")
    LOCATION = EnumValue(4, "F4:Location")
    TARGET = EnumValue(5, "F5:Target")
    INVALID = EnumValue(6, "F6:Invalid")


class TargetMethod(LabeledEnum):
    """FIXUPP target determination methods.

    - T0:SEGDEF: Target specified by SEGDEF index with displacement
    - T1:GRPDEF: Target specified by GRPDEF index with displacement
    - T2:EXTDEF: Target specified by EXTDEF index with displacement
    - T3:FrameNum: Explicit frame number (not supported)
    - T4:SEGDEF(0): Target specified by SEGDEF index, displacement assumed 0
    - T5:GRPDEF(0): Target specified by GRPDEF index, displacement assumed 0
    - T6:EXTDEF(0): Target specified by EXTDEF index, displacement assumed 0
    """
    SEGDEF = EnumValue(0, "T0:SEGDEF")
    GRPDEF = EnumValue(1, "T1:GRPDEF")
    EXTDEF = EnumValue(2, "T2:EXTDEF")
    FRAME_NUM = EnumValue(3, "T3:FrameNum")
    SEGDEF_NO_DISP = EnumValue(4, "T4:SEGDEF(0)")
    GRPDEF_NO_DISP = EnumValue(5, "T5:GRPDEF(0)")
    EXTDEF_NO_DISP = EnumValue(6, "T6:EXTDEF(0)")


class ComdatSelection(LabeledEnum):
    """COMDAT selection attribute (high-order 4 bits of attribute byte).

    - No Match: Only one instance allowed; duplicate definitions are errors
    - Pick Any: Pick any instance; all definitions assumed identical
    - Same Size: Pick any, but all definitions must have same size
    - Exact Match: Pick any, but all definitions must have matching checksums
    """
    NO_MATCH = EnumValue(0, "No Match")
    PICK_ANY = EnumValue(1, "Pick Any")
    SAME_SIZE = EnumValue(2, "Same Size")
    EXACT_MATCH = EnumValue(3, "Exact Match")


class ComdatAllocation(LabeledEnum):
    """COMDAT allocation attribute (low-order 4 bits of attribute byte).

    - Explicit: Allocate in segment specified by SEGDEF index
    - Far Code (CODE16): Allocate in default 16-bit code segment
    - Far Data (DATA16): Allocate in default 16-bit data segment
    - Code32: Allocate in default 32-bit code segment
    - Data32: Allocate in default 32-bit data segment
    """
    EXPLICIT = EnumValue(0, "Explicit")
    FAR_CODE = EnumValue(1, "Far Code (CODE16)")
    FAR_DATA = EnumValue(2, "Far Data (DATA16)")
    CODE32 = EnumValue(3, "Code32")
    DATA32 = EnumValue(4, "Data32")


class ComdatAlign(LabeledEnum):
    """COMDAT alignment values. Values 0-5 correspond to SEGDEF alignment.

    - FromSEGDEF: Use alignment from associated SEGDEF record
    - Byte: Byte aligned
    - Word: Word (2-byte) aligned
    - Para: Paragraph (16-byte) aligned
    - Page: Page aligned
    - DWord: DWord (4-byte) aligned
    """
    FROM_SEGDEF = EnumValue(0, "FromSEGDEF")
    BYTE = EnumValue(1, "Byte")
    WORD = EnumValue(2, "Word")
    PARAGRAPH = EnumValue(3, "Para")
    PAGE = EnumValue(4, "Page")
    DWORD = EnumValue(5, "DWord")


class BackpatchLocation(LabeledEnum):
    """BAKPAT/NBKPAT location types.

    - Byte(8): 8-bit value
    - Word(16): 16-bit value
    - DWord(32): 32-bit value
    - DWord(32-IBM): 32-bit value (IBM LINK386 extension)
    """
    BYTE = EnumValue(0, "Byte(8)")
    WORD = EnumValue(1, "Word(16)")
    DWORD = EnumValue(2, "DWord(32)")
    DWORD_IBM = EnumValue(9, "DWord(32-IBM)")


class WatcomProcessor(CharLabeledEnum):
    """Watcom processor type (COMENT 0x9B/0x9D first byte).

    Values from Watcom compiler processor/memory model string.
    """
    I8086 = CharEnumValue('0', "8086")
    I80286 = CharEnumValue('2', "80286")
    I80386_PLUS = CharEnumValue('3', "80386+")


class WatcomMemModel(CharLabeledEnum):
    """Watcom memory model (COMENT 0x9B/0x9D second byte).

    Values from Watcom compiler processor/memory model string.
    """
    SMALL = CharEnumValue('s', "Small")
    MEDIUM = CharEnumValue('m', "Medium")
    COMPACT = CharEnumValue('c', "Compact")
    LARGE = CharEnumValue('l', "Large")
    HUGE = CharEnumValue('h', "Huge")
    FLAT = CharEnumValue('f', "Flat")


class WatcomFPMode(CharLabeledEnum):
    """Watcom floating point mode (COMENT 0x9B/0x9D fourth byte).

    Values from Watcom compiler processor/memory model string.
    """
    EMULATED_INLINE = CharEnumValue('e', "Emulated inline")
    EMULATOR_CALLS = CharEnumValue('c', "Emulator calls")
    FP80X87_INLINE = CharEnumValue('p', "80x87 inline")


class ModEndType(IntFlag):
    """MODEND module type flags.

    See docs/OMF_spec/02_OMF_Headers_Comments_and_Module_Meta.md lines 607-626.
    """
    RELOCATABLE = 0x01  # Start address is relocatable
    HAS_START = 0x40    # Module contains a start address
    IS_MAIN = 0x80      # Module is a main program module


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

    # TIS OMF 1.1 Extension Records
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


class RegisterType(LabeledEnum):
    """8086 register types for REGINT record (obsolete 70H).

    Per TIS OMF 1.1 Appendix 3, the REGINT record provides information
    about register/register-pairs: CS and IP, SS and SP, DS and ES.
    """
    CS = EnumValue(0, "CS")
    DS = EnumValue(1, "DS")
    SS = EnumValue(2, "SS")
    ES = EnumValue(3, "ES")
    IP = EnumValue(4, "IP")
    SP = EnumValue(5, "SP")

class TypDefVarType(LabeledEnum):
    """TYPDEF variable type values for NEAR/FAR leaves.

    Per TIS OMF 1.1 Appendix 3, the variable type field must contain one
    of these three values. The specific value is ignored by most linkers.

    - Array: Array type (0x77)
    - Structure: Structure type (0x79)
    - Scalar: Scalar type (0x7B)
    """
    ARRAY = EnumValue(0x77, "Array")
    STRUCTURE = EnumValue(0x79, "Structure")
    SCALAR = EnumValue(0x7B, "Scalar")


KNOWN_VENDORS: dict[int, str] = {
    0: "TIS (reserved)",
}
