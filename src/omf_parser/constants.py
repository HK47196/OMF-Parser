"""OMF constants and record type definitions."""

from enum import IntEnum, IntFlag, StrEnum, unique


class OMFVariant(StrEnum):
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


class CommentClass(StrEnum):
    """COMENT record class types.

    Note: Different vendors may use overlapping class numbers.
    """
    TRANSLATOR = "Translator"
    COPYRIGHT = "Intel Copyright"
    LIBSPEC = "Library Specifier (obsolete)"
    WAT_PROC_MODEL = "Watcom Processor/Model"
    MSDOS_VERSION = "MS-DOS Version (obsolete)"
    MS_PROC_MODEL = "MS Processor/Model"
    DOSSEG = "DOSSEG"
    DEFAULT_LIBRARY = "Default Library Search"
    OMF_EXTENSIONS = "OMF Extensions"
    NEW_OMF = "New OMF Extension"
    LINK_PASS = "Link Pass Separator"
    LIBMOD = "LIBMOD"
    EXESTR = "EXESTR"
    INCERR = "INCERR"
    NOPAD = "NOPAD"
    WKEXT = "WKEXT"
    LZEXT = "LZEXT"
    EASY_OMF = "Easy OMF"
    LINKER_32BIT = "32-bit Linker Extension"
    LINKER_32BIT_ALT = "32-bit Linker Extension (alt)"
    COMMENT = "Comment"
    COMPILER = "Compiler"
    DATE = "Date"
    TIMESTAMP = "Timestamp"
    USER = "User"
    DEPENDENCY = "Dependency File (Borland)"
    DISASM_DIRECTIVE = "Watcom Disassembler Directive"
    LINKER_DIRECTIVE = "Watcom Linker Directive"
    COMMANDLINE = "Command Line (QuickC)"

    @classmethod
    def from_raw(cls, value: int, variant: OMFVariant) -> "CommentClass":
        """Look up comment class from raw byte value."""
        match (value, variant):
            case (0x00, _): return cls.TRANSLATOR
            case (0x01, _): return cls.COPYRIGHT
            case (0x81, _): return cls.LIBSPEC
            case (0x9B, _): return cls.WAT_PROC_MODEL
            case (0x9C, _): return cls.MSDOS_VERSION
            case (0x9D, _): return cls.MS_PROC_MODEL
            case (0x9E, _): return cls.DOSSEG
            case (0x9F, _): return cls.DEFAULT_LIBRARY
            case (0xA0, _): return cls.OMF_EXTENSIONS
            case (0xA1, _): return cls.NEW_OMF
            case (0xA2, _): return cls.LINK_PASS
            case (0xA3, _): return cls.LIBMOD
            case (0xA4, _): return cls.EXESTR
            case (0xA6, _): return cls.INCERR
            case (0xA7, _): return cls.NOPAD
            case (0xA8, _): return cls.WKEXT
            case (0xA9, _): return cls.LZEXT
            case (0xAA, _): return cls.EASY_OMF
            case (0xB0, _): return cls.LINKER_32BIT
            case (0xB1, _): return cls.LINKER_32BIT_ALT
            case (0xDA, _): return cls.COMMENT
            case (0xDB, _): return cls.COMPILER
            case (0xDC, _): return cls.DATE
            case (0xDD, _): return cls.TIMESTAMP
            case (0xDF, _): return cls.USER
            case (0xE9, _): return cls.DEPENDENCY
            case (0xFD, _): return cls.DISASM_DIRECTIVE
            case (0xFE, _): return cls.LINKER_DIRECTIVE
            case (0xFF, _): return cls.COMMANDLINE
            case _: raise ValueError(f"Unknown {cls.__name__} value: 0x{value:02X}")

    @classmethod
    def to_raw(cls, member: "CommentClass") -> int:
        """Get raw byte value for a CommentClass member."""
        return _COMMENT_CLASS_TO_RAW[member]


_COMMENT_CLASS_TO_RAW: dict[CommentClass, int] = {
    CommentClass.TRANSLATOR: 0x00,
    CommentClass.COPYRIGHT: 0x01,
    CommentClass.LIBSPEC: 0x81,
    CommentClass.WAT_PROC_MODEL: 0x9B,
    CommentClass.MSDOS_VERSION: 0x9C,
    CommentClass.MS_PROC_MODEL: 0x9D,
    CommentClass.DOSSEG: 0x9E,
    CommentClass.DEFAULT_LIBRARY: 0x9F,
    CommentClass.OMF_EXTENSIONS: 0xA0,
    CommentClass.NEW_OMF: 0xA1,
    CommentClass.LINK_PASS: 0xA2,
    CommentClass.LIBMOD: 0xA3,
    CommentClass.EXESTR: 0xA4,
    CommentClass.INCERR: 0xA6,
    CommentClass.NOPAD: 0xA7,
    CommentClass.WKEXT: 0xA8,
    CommentClass.LZEXT: 0xA9,
    CommentClass.EASY_OMF: 0xAA,
    CommentClass.LINKER_32BIT: 0xB0,
    CommentClass.LINKER_32BIT_ALT: 0xB1,
    CommentClass.COMMENT: 0xDA,
    CommentClass.COMPILER: 0xDB,
    CommentClass.DATE: 0xDC,
    CommentClass.TIMESTAMP: 0xDD,
    CommentClass.USER: 0xDF,
    CommentClass.DEPENDENCY: 0xE9,
    CommentClass.DISASM_DIRECTIVE: 0xFD,
    CommentClass.LINKER_DIRECTIVE: 0xFE,
    CommentClass.COMMANDLINE: 0xFF,
}


class A0Subtype(StrEnum):
    """OMF Extensions (A0) comment subtypes."""
    IMPDEF = "IMPDEF"
    EXPDEF = "EXPDEF"
    INCDEF = "INCDEF"
    PROTECTED_MEMORY = "Protected Memory Library"
    LNKDIR = "LNKDIR"
    BIG_ENDIAN = "Big-endian"
    PRECOMP = "PRECOMP"

    @classmethod
    def from_raw(cls, value: int, variant: OMFVariant) -> "A0Subtype":
        """Look up A0 subtype from raw byte value."""
        match (value, variant):
            case (0x01, _): return cls.IMPDEF
            case (0x02, _): return cls.EXPDEF
            case (0x03, _): return cls.INCDEF
            case (0x04, _): return cls.PROTECTED_MEMORY
            case (0x05, _): return cls.LNKDIR
            case (0x06, _): return cls.BIG_ENDIAN
            case (0x07, _): return cls.PRECOMP
            case _: raise ValueError(f"Unknown {cls.__name__} value: 0x{value:02X}")


@unique
class GrpdefComponent(IntEnum):
    """GRPDEF component type markers."""
    SEGMENT_INDEX = 0xFF
    EXTERNAL_INDEX = 0xFE
    SEGDEF_INDICES = 0xFD
    LTL = 0xFB
    ABSOLUTE = 0xFA


class ComdefType(StrEnum):
    """COMDEF data type codes.

    - FAR: FAR data with element count and size
    - NEAR: NEAR data with byte size
    """
    FAR = "FAR"
    NEAR = "NEAR"

    @classmethod
    def from_raw(cls, value: int, variant: OMFVariant) -> "ComdefType":
        """Look up COMDEF type from raw byte value."""
        match (value, variant):
            case (0x61, _): return cls.FAR
            case (0x62, _): return cls.NEAR
            case _: raise ValueError(f"Unknown {cls.__name__} value: 0x{value:02X}")


# Raw byte values for COMDEF types (used in parsing comparisons)
COMDEF_TYPE_FAR = 0x61
COMDEF_TYPE_NEAR = 0x62


@unique
class TypdefLeaf(IntEnum):
    """TYPDEF leaf type codes."""
    FAR = 0x61
    NEAR = 0x62


class SegAlignment(StrEnum):
    """SEGDEF alignment values (A field in ACBP byte).

    - Absolute: Absolute segment (frame number and offset follow)
    - Byte: Relocatable, byte aligned
    - Word: Relocatable, word (2-byte) aligned
    - Paragraph: Relocatable, paragraph (16-byte) aligned
    - Page: Relocatable, page aligned (256-byte Intel / 4K IBM)
    - DWord: Relocatable, dword (4-byte) aligned
    - LTL(6): Not supported (Intel: LTL paragraph aligned) [PharLap: 4K page]
    - Undefined(7): Not defined
    """
    ABSOLUTE = "Absolute"
    BYTE = "Byte"
    WORD = "Word"
    PARAGRAPH = "Paragraph"
    PAGE = "Page (256-byte Intel / 4K IBM)"
    DWORD = "DWord"
    LTL = "LTL(6)"
    PHARLAP_PAGE_4K = "Page (4K) [PharLap]"
    UNDEFINED = "Undefined(7)"

    @classmethod
    def from_raw(cls, value: int, variant: OMFVariant) -> "SegAlignment":
        """Look up segment alignment from raw byte value."""
        match (value, variant):
            case (0, _): return cls.ABSOLUTE
            case (1, _): return cls.BYTE
            case (2, _): return cls.WORD
            case (3, _): return cls.PARAGRAPH
            case (4, _): return cls.PAGE
            case (5, _): return cls.DWORD
            case (6, OMFVariant.PHARLAP): return cls.PHARLAP_PAGE_4K
            case (6, _): return cls.LTL
            case (7, _): return cls.UNDEFINED
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value}")


class SegCombine(StrEnum):
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
    PRIVATE = "Private"
    RESERVED_1 = "Reserved(1) [Intel: Common]"
    PUBLIC = "Public"
    RESERVED_3 = "Reserved(3)"
    PUBLIC_4 = "Public(4)"
    STACK = "Stack"
    COMMON = "Common"
    PUBLIC_7 = "Public(7)"

    @classmethod
    def from_raw(cls, value: int, variant: OMFVariant) -> "SegCombine":
        """Look up segment combine from raw byte value."""
        match (value, variant):
            case (0, _): return cls.PRIVATE
            case (1, _): return cls.RESERVED_1
            case (2, _): return cls.PUBLIC
            case (3, _): return cls.RESERVED_3
            case (4, _): return cls.PUBLIC_4
            case (5, _): return cls.STACK
            case (6, _): return cls.COMMON
            case (7, _): return cls.PUBLIC_7
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value}")


class SegAccess(StrEnum):
    """SEGDEF access types (AT field in PharLap access byte).

    Per PharLap Easy OMF-386 specification, the access byte contains a 2-bit
    AT field specifying the segment's access type.

    - RO: Read only (0)
    - EO: Execute only (1)
    - ER: Execute/read (2)
    - RW: Read/write (3)
    """
    RO = "Read only"
    EO = "Execute only"
    ER = "Execute/read"
    RW = "Read/write"

    @classmethod
    def from_raw(cls, value: int, variant: OMFVariant) -> "SegAccess":
        """Look up segment access from raw byte value."""
        match (value, variant):
            case (0, _): return cls.RO
            case (1, _): return cls.EO
            case (2, _): return cls.ER
            case (3, _): return cls.RW
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value}")


class FixupLocation(StrEnum):
    """FIXUPP location types. Some values differ between TIS and PharLap variants.

    TIS standard locations:
    - 0: Byte(8) - Low-order byte (8-bit displacement or low byte of 16-bit offset)
    - 1: Offset(16) - 16-bit offset
    - 2: Segment(16) - 16-bit base/selector
    - 3: Ptr(16:16) - 32-bit far pointer (16-bit segment:16-bit offset)
    - 4: HiByte(8) - High-order byte of 16-bit offset
    - 5: Loader-resolved Offset(16) - 16-bit loader-resolved offset
    - 9: Offset(32) - 32-bit offset
    - 11: Ptr(16:32) - 48-bit far pointer (16-bit segment:32-bit offset)
    - 13: Loader-resolved Offset(32) - 32-bit loader-resolved offset

    PharLap Easy OMF-386 differences:
    - 5: 32-bit offset (PHARLAP_OFFSET_32)
    - 6: 48-bit pointer (16:32) (TIS: reserved)
    """
    BYTE = "Byte(8)"
    OFFSET_16 = "Offset(16)"
    SEGMENT_16 = "Segment(16)"
    PTR_16_16 = "Ptr(16:16)"
    HIBYTE = "HiByte(8)"
    LOADER_OFFSET_16 = "Loader-resolved Offset(16)"
    PHARLAP_OFFSET_32 = "Offset(32) [PharLap loc 5]"
    PHARLAP_PTR_16_32 = "Ptr(16:32) [PharLap loc 6]"
    OFFSET_32 = "Offset(32)"
    PTR_16_32 = "Ptr(16:32)"
    LOADER_OFFSET_32 = "Loader-resolved Offset(32)"

    @classmethod
    def from_raw(cls, value: int, variant: OMFVariant) -> "FixupLocation":
        """Look up fixup location from raw byte value."""
        match (value, variant):
            case (0, _): return cls.BYTE
            case (1, _): return cls.OFFSET_16
            case (2, _): return cls.SEGMENT_16
            case (3, _): return cls.PTR_16_16
            case (4, _): return cls.HIBYTE
            case (5, OMFVariant.PHARLAP): return cls.PHARLAP_OFFSET_32
            case (5, _): return cls.LOADER_OFFSET_16
            case (6, OMFVariant.PHARLAP): return cls.PHARLAP_PTR_16_32
            case (9, _): return cls.OFFSET_32
            case (11, _): return cls.PTR_16_32
            case (13, _): return cls.LOADER_OFFSET_32
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value}")


class FrameMethod(StrEnum):
    """FIXUPP frame determination methods.

    - F0:SEGDEF: Frame specified by SEGDEF index
    - F1:GRPDEF: Frame specified by GRPDEF index
    - F2:EXTDEF: Frame specified by EXTDEF index
    - F3:FrameNum: Explicit frame number (not supported by linkers)
    - F4:Location: Frame from previous LEDATA/LIDATA segment
    - F5:Target: Frame determined by target
    - F6:Invalid: Invalid/reserved
    """
    SEGDEF = "F0:SEGDEF"
    GRPDEF = "F1:GRPDEF"
    EXTDEF = "F2:EXTDEF"
    FRAME_NUM = "F3:FrameNum"
    LOCATION = "F4:Location"
    TARGET = "F5:Target"
    INVALID = "F6:Invalid"

    @classmethod
    def from_raw(cls, value: int, variant: OMFVariant) -> "FrameMethod":
        """Look up frame method from raw byte value."""
        match (value, variant):
            case (0, _): return cls.SEGDEF
            case (1, _): return cls.GRPDEF
            case (2, _): return cls.EXTDEF
            case (3, _): return cls.FRAME_NUM
            case (4, _): return cls.LOCATION
            case (5, _): return cls.TARGET
            case (6, _): return cls.INVALID
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value}")

    @classmethod
    def to_raw(cls, member: "FrameMethod") -> int:
        """Get raw byte value for a FrameMethod member."""
        return _FRAME_METHOD_TO_RAW[member]


_FRAME_METHOD_TO_RAW: dict[FrameMethod, int] = {
    FrameMethod.SEGDEF: 0,
    FrameMethod.GRPDEF: 1,
    FrameMethod.EXTDEF: 2,
    FrameMethod.FRAME_NUM: 3,
    FrameMethod.LOCATION: 4,
    FrameMethod.TARGET: 5,
    FrameMethod.INVALID: 6,
}


class TargetMethod(StrEnum):
    """FIXUPP target determination methods.

    - T0:SEGDEF: Target specified by SEGDEF index with displacement
    - T1:GRPDEF: Target specified by GRPDEF index with displacement
    - T2:EXTDEF: Target specified by EXTDEF index with displacement
    - T3:FrameNum: Explicit frame number (not supported)
    - T4:SEGDEF(0): Target specified by SEGDEF index, displacement assumed 0
    - T5:GRPDEF(0): Target specified by GRPDEF index, displacement assumed 0
    - T6:EXTDEF(0): Target specified by EXTDEF index, displacement assumed 0
    """
    SEGDEF = "T0:SEGDEF"
    GRPDEF = "T1:GRPDEF"
    EXTDEF = "T2:EXTDEF"
    FRAME_NUM = "T3:FrameNum"
    SEGDEF_NO_DISP = "T4:SEGDEF(0)"
    GRPDEF_NO_DISP = "T5:GRPDEF(0)"
    EXTDEF_NO_DISP = "T6:EXTDEF(0)"

    @classmethod
    def from_raw(cls, value: int, variant: OMFVariant) -> "TargetMethod":
        """Look up target method from raw byte value."""
        match (value, variant):
            case (0, _): return cls.SEGDEF
            case (1, _): return cls.GRPDEF
            case (2, _): return cls.EXTDEF
            case (3, _): return cls.FRAME_NUM
            case (4, _): return cls.SEGDEF_NO_DISP
            case (5, _): return cls.GRPDEF_NO_DISP
            case (6, _): return cls.EXTDEF_NO_DISP
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value}")

    @classmethod
    def to_raw(cls, member: "TargetMethod") -> int:
        """Get raw byte value for a TargetMethod member."""
        return _TARGET_METHOD_TO_RAW[member]

    def has_displacement(self) -> bool:
        """Check if this target method includes a displacement field."""
        return TargetMethod.to_raw(self) < 4


_TARGET_METHOD_TO_RAW: dict[TargetMethod, int] = {
    TargetMethod.SEGDEF: 0,
    TargetMethod.GRPDEF: 1,
    TargetMethod.EXTDEF: 2,
    TargetMethod.FRAME_NUM: 3,
    TargetMethod.SEGDEF_NO_DISP: 4,
    TargetMethod.GRPDEF_NO_DISP: 5,
    TargetMethod.EXTDEF_NO_DISP: 6,
}


class ComdatSelection(StrEnum):
    """COMDAT selection attribute (high-order 4 bits of attribute byte).

    - No Match: Only one instance allowed; duplicate definitions are errors
    - Pick Any: Pick any instance; all definitions assumed identical
    - Same Size: Pick any, but all definitions must have same size
    - Exact Match: Pick any, but all definitions must have matching checksums
    """
    NO_MATCH = "No Match"
    PICK_ANY = "Pick Any"
    SAME_SIZE = "Same Size"
    EXACT_MATCH = "Exact Match"

    @classmethod
    def from_raw(cls, value: int, variant: OMFVariant) -> "ComdatSelection":
        """Look up COMDAT selection from raw byte value."""
        match (value, variant):
            case (0, _): return cls.NO_MATCH
            case (1, _): return cls.PICK_ANY
            case (2, _): return cls.SAME_SIZE
            case (3, _): return cls.EXACT_MATCH
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value}")


class ComdatAllocation(StrEnum):
    """COMDAT allocation attribute (low-order 4 bits of attribute byte).

    - Explicit: Allocate in segment specified by SEGDEF index
    - Far Code (CODE16): Allocate in default 16-bit code segment
    - Far Data (DATA16): Allocate in default 16-bit data segment
    - Code32: Allocate in default 32-bit code segment
    - Data32: Allocate in default 32-bit data segment
    """
    EXPLICIT = "Explicit"
    FAR_CODE = "Far Code (CODE16)"
    FAR_DATA = "Far Data (DATA16)"
    CODE32 = "Code32"
    DATA32 = "Data32"

    @classmethod
    def from_raw(cls, value: int, variant: OMFVariant) -> "ComdatAllocation":
        """Look up COMDAT allocation from raw byte value."""
        match (value, variant):
            case (0, _): return cls.EXPLICIT
            case (1, _): return cls.FAR_CODE
            case (2, _): return cls.FAR_DATA
            case (3, _): return cls.CODE32
            case (4, _): return cls.DATA32
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value}")


class ComdatAlign(StrEnum):
    """COMDAT alignment values. Values 0-5 correspond to SEGDEF alignment.

    - FromSEGDEF: Use alignment from associated SEGDEF record
    - Byte: Byte aligned
    - Word: Word (2-byte) aligned
    - Para: Paragraph (16-byte) aligned
    - Page: Page aligned
    - DWord: DWord (4-byte) aligned
    """
    FROM_SEGDEF = "FromSEGDEF"
    BYTE = "Byte"
    WORD = "Word"
    PARAGRAPH = "Para"
    PAGE = "Page"
    DWORD = "DWord"

    @classmethod
    def from_raw(cls, value: int, variant: OMFVariant) -> "ComdatAlign":
        """Look up COMDAT alignment from raw byte value."""
        match (value, variant):
            case (0, _): return cls.FROM_SEGDEF
            case (1, _): return cls.BYTE
            case (2, _): return cls.WORD
            case (3, _): return cls.PARAGRAPH
            case (4, _): return cls.PAGE
            case (5, _): return cls.DWORD
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value}")


class BackpatchLocation(StrEnum):
    """BAKPAT/NBKPAT location types.

    - Byte(8): 8-bit value
    - Word(16): 16-bit value
    - DWord(32): 32-bit value
    - DWord(32-IBM): 32-bit value (IBM LINK386 extension)
    """
    BYTE = "Byte(8)"
    WORD = "Word(16)"
    DWORD = "DWord(32)"
    DWORD_IBM = "DWord(32-IBM)"

    @classmethod
    def from_raw(cls, value: int, variant: OMFVariant) -> "BackpatchLocation":
        """Look up backpatch location from raw byte value."""
        match (value, variant):
            case (0, _): return cls.BYTE
            case (1, _): return cls.WORD
            case (2, _): return cls.DWORD
            case (9, _): return cls.DWORD_IBM
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value}")


class WatcomProcessor(StrEnum):
    """Watcom processor type (COMENT 0x9B/0x9D first byte).

    Values from Watcom compiler processor/memory model string.
    """
    I8086 = "8086"
    I80286 = "80286"
    I80386_PLUS = "80386+"

    @classmethod
    def from_raw(cls, value: str, variant: OMFVariant) -> "WatcomProcessor":
        """Look up processor type from raw char value."""
        match (value, variant):
            case ('0', _): return cls.I8086
            case ('2', _): return cls.I80286
            case ('3', _): return cls.I80386_PLUS
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value!r}")


class WatcomMemModel(StrEnum):
    """Watcom memory model (COMENT 0x9B/0x9D second byte).

    Values from Watcom compiler processor/memory model string.
    """
    SMALL = "Small"
    MEDIUM = "Medium"
    COMPACT = "Compact"
    LARGE = "Large"
    HUGE = "Huge"
    FLAT = "Flat"

    @classmethod
    def from_raw(cls, value: str, variant: OMFVariant) -> "WatcomMemModel":
        """Look up memory model from raw char value."""
        match (value, variant):
            case ('s', _): return cls.SMALL
            case ('m', _): return cls.MEDIUM
            case ('c', _): return cls.COMPACT
            case ('l', _): return cls.LARGE
            case ('h', _): return cls.HUGE
            case ('f', _): return cls.FLAT
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value!r}")


class WatcomFPMode(StrEnum):
    """Watcom floating point mode (COMENT 0x9B/0x9D fourth byte).

    Values from Watcom compiler processor/memory model string.
    """
    EMULATED_INLINE = "Emulated inline"
    EMULATOR_CALLS = "Emulator calls"
    FP80X87_INLINE = "80x87 inline"

    @classmethod
    def from_raw(cls, value: str, variant: OMFVariant) -> "WatcomFPMode":
        """Look up FP mode from raw char value."""
        match (value, variant):
            case ('e', _): return cls.EMULATED_INLINE
            case ('c', _): return cls.EMULATOR_CALLS
            case ('p', _): return cls.FP80X87_INLINE
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value!r}")


class LinkerDirectiveCode(StrEnum):
    """Watcom linker directive codes (COMENT class 0xFE).

    Values from Watcom documentation, captured in coment/watcom.py.
    """
    SOURCE_LANG = "Source Language"
    DEFAULT_LIB = "Default Library"
    OPT_FAR_CALLS = "Optimize Far Calls"
    OPT_UNSAFE = "Optimization Unsafe"
    VF_TABLE_DEF = "VF Table Definition"
    VF_PURE_DEF = "VF Pure Definition"
    VF_REFERENCE = "VF Reference"
    PACK_DATA = "Pack Far Data"
    FLAT_ADDRS = "Flat Addresses"
    TIMESTAMP = "Object Timestamp"

    @classmethod
    def from_raw(cls, value: str, variant: OMFVariant) -> "LinkerDirectiveCode":
        """Look up linker directive code from raw char value."""
        match (value, variant):
            case ('D', _): return cls.SOURCE_LANG
            case ('L', _): return cls.DEFAULT_LIB
            case ('O', _): return cls.OPT_FAR_CALLS
            case ('U', _): return cls.OPT_UNSAFE
            case ('V', _): return cls.VF_TABLE_DEF
            case ('P', _): return cls.VF_PURE_DEF
            case ('R', _): return cls.VF_REFERENCE
            case ('7', _): return cls.PACK_DATA
            case ('F', _): return cls.FLAT_ADDRS
            case ('T', _): return cls.TIMESTAMP
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value!r}")


class DisasmDirectiveSubtype(StrEnum):
    """Watcom disassembler directive subtypes (COMENT class 0xFD).

    Marks non-executable data regions within code segments for disassemblers.

    - SCAN_TABLE_16: 16-bit scan table ('s', 0x73) - uses 16-bit offsets
    - SCAN_TABLE_32: 32-bit scan table ('S', 0x53) - uses 32-bit offsets
    """
    SCAN_TABLE_16 = "DDIR_SCAN_TABLE"
    SCAN_TABLE_32 = "DDIR_SCAN_TABLE_32"

    @classmethod
    def from_raw(cls, value: str, variant: OMFVariant) -> "DisasmDirectiveSubtype":
        """Look up disasm directive subtype from raw char value."""
        match (value, variant):
            case ('s', _): return cls.SCAN_TABLE_16
            case ('S', _): return cls.SCAN_TABLE_32
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value!r}")


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




RESERVED_SEGMENTS = {"$$TYPES", "$$SYMBOLS", "$$IMPORT"}


class RegisterType(StrEnum):
    """8086 register types for REGINT record (obsolete 70H).

    Per TIS OMF 1.1 Appendix 3, the REGINT record provides information
    about register/register-pairs: CS and IP, SS and SP, DS and ES.
    """
    CS = "CS"
    DS = "DS"
    SS = "SS"
    ES = "ES"
    IP = "IP"
    SP = "SP"

    @classmethod
    def from_raw(cls, value: int, variant: OMFVariant) -> "RegisterType":
        """Look up register type from raw byte value."""
        match (value, variant):
            case (0, _): return cls.CS
            case (1, _): return cls.DS
            case (2, _): return cls.SS
            case (3, _): return cls.ES
            case (4, _): return cls.IP
            case (5, _): return cls.SP
            case _: raise ValueError(f"Unknown {cls.__name__} value: {value}")


class TypDefVarType(StrEnum):
    """TYPDEF variable type values for NEAR/FAR leaves.

    Per TIS OMF 1.1 Appendix 3, the variable type field must contain one
    of these three values. The specific value is ignored by most linkers.

    - Array: Array type (0x77)
    - Structure: Structure type (0x79)
    - Scalar: Scalar type (0x7B)
    """
    ARRAY = "Array"
    STRUCTURE = "Structure"
    SCALAR = "Scalar"

    @classmethod
    def from_raw(cls, value: int, variant: OMFVariant) -> "TypDefVarType":
        """Look up variable type from raw byte value."""
        match (value, variant):
            case (0x77, _): return cls.ARRAY
            case (0x79, _): return cls.STRUCTURE
            case (0x7B, _): return cls.SCALAR
            case _: raise ValueError(f"Unknown {cls.__name__} value: 0x{value:02X}")


KNOWN_VENDORS: dict[int, str] = {
    0: "TIS (reserved)",
}
