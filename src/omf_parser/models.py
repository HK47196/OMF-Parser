"""Data models for parsed OMF records.

These dataclasses represent the structured output from parsing OMF records.
They are designed to be serializable to JSON and formattable to human-readable text.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, Union, Literal, Tuple
from typing_extensions import TypedDict, NotRequired


# =============================================================================
# Enums for categorical values
# =============================================================================

class ThreadKind(str, Enum):
    """FIXUPP thread type."""
    FRAME = "FRAME"
    TARGET = "TARGET"


class FixupMode(str, Enum):
    """FIXUPP fixup mode."""
    SEGMENT_RELATIVE = "Segment-relative"
    SELF_RELATIVE = "Self-relative"


class TypDefFormat(str, Enum):
    """TYPDEF format type."""
    MICROSOFT = "Microsoft"
    INTEL = "Intel"


class ComDefKind(str, Enum):
    """COMDEF definition kind."""
    FAR = "FAR"
    NEAR = "NEAR"
    BORLAND = "Borland"
    UNKNOWN = "Unknown"


# =============================================================================
# TypedDict definitions for structured dictionaries
# =============================================================================

class PubDefSymbol(TypedDict):
    """Symbol entry in PUBDEF/LPUBDEF records."""
    name: str
    offset: int
    type_index: int


class ExtDefEntry(TypedDict):
    """External definition entry."""
    index: int
    name: str
    type_index: int


class CExtDefEntry(TypedDict):
    """COMDAT external definition entry."""
    index: int
    name: str
    type_index: int


class StartAddress(TypedDict, total=False):
    """MODEND start address information."""
    frame_method: int
    p_bit: int
    target_method: int
    frame_datum: int
    target_datum: int
    target_displacement: int


class LineEntry(TypedDict):
    """Line number entry in LINNUM/LINSYM records."""
    line: int
    offset: int
    is_end_of_function: bool


class ComDefDefinitionBase(TypedDict):
    """Base fields for COMDEF definitions."""
    name: str
    type_index: int
    data_type: int
    kind: str


class ComDefFarDefinition(ComDefDefinitionBase):
    """FAR COMDEF definition."""
    num_elements: int
    element_size: int
    total_size: int


class ComDefNearDefinition(ComDefDefinitionBase):
    """NEAR COMDEF definition."""
    size: int


class ComDefBorlandDefinition(ComDefDefinitionBase):
    """Borland COMDEF definition."""
    seg_index: int
    length: int


class ComDefUnknownDefinition(ComDefDefinitionBase):
    """Unknown COMDEF definition."""
    length: int


ComDefDefinition = Union[ComDefFarDefinition, ComDefNearDefinition, ComDefBorlandDefinition, ComDefUnknownDefinition]


class BackpatchRecord(TypedDict):
    """BAKPAT backpatch record entry."""
    segment: str
    segment_index: int
    location_type: int
    location_name: str
    offset: int
    value: int


class NamedBackpatchRecord(TypedDict):
    """NBKPAT named backpatch record entry."""
    location_type: int
    location_name: str
    symbol: str
    offset: int
    value: int


class AliasEntry(TypedDict):
    """Alias definition entry."""
    alias: str
    substitute: str


class WeakExternEntry(TypedDict):
    """Weak extern definition entry."""
    weak_extdef_index: int
    default_resolution_index: int


class LazyExternEntry(TypedDict):
    """Lazy extern definition entry."""
    lazy_extdef_index: int
    default_resolution_index: int


class DictEntry(TypedDict):
    """Library dictionary entry."""
    block: int
    bucket: int
    symbol: str
    page: int


class ExtDictModule(TypedDict, total=False):
    """Extended dictionary module entry."""
    page: int
    dependencies: List[int]


class RegisterEntry(TypedDict):
    """Register initialization entry (obsolete)."""
    register: str
    register_value: int
    content_type: str
    content: Union[int, str, None]


class TypDefLeafNear(TypedDict, total=False):
    """TYPDEF NEAR leaf descriptor."""
    type: Literal["NEAR"]
    leaf_index: int
    leaf_type: int
    var_type: str
    var_type_raw: int
    size_bits: int
    size_bytes: int


class TypDefLeafFar(TypedDict, total=False):
    """TYPDEF FAR leaf descriptor."""
    type: Literal["FAR"]
    leaf_index: int
    leaf_type: int
    num_elements: int
    element_type: str
    element_type_index: int


class TypDefLeafUnknown(TypedDict, total=False):
    """TYPDEF unknown leaf descriptor."""
    type: Literal["Unknown"]
    leaf_index: int
    leaf_type: int
    remaining: bytes


TypDefLeaf = Union[TypDefLeafNear, TypDefLeafFar, TypDefLeafUnknown]


class LibLocEntry(TypedDict):
    """Library location entry (obsolete)."""
    module: str
    block_num: int
    byte_offset: int


# Type alias for LNAMES entry (index, name, is_reserved)
LNameEntry = Tuple[int, str, bool]


@dataclass
class ParsedRecord:
    """Base class for all parsed record data."""
    pass


# Standard record models

@dataclass
class ParsedTheadr(ParsedRecord):
    """THEADR/LHEADR - Module header."""
    record_name: Literal["THEADR", "LHEADR"]
    module_name: str


@dataclass
class ParsedLNames(ParsedRecord):
    """LNAMES/LLNAMES - Logical names."""
    record_name: Literal["LNAMES", "LLNAMES (Local)"]
    start_index: int
    end_index: int
    names: List[LNameEntry]


@dataclass
class ParsedSegDef(ParsedRecord):
    """SEGDEF - Segment definition."""
    acbp: int
    alignment: str
    align_value: int
    combine: str
    big: bool
    use32: bool
    absolute_frame: Optional[int] = None
    absolute_offset: Optional[int] = None
    length: int = 0
    length_display: str = ""
    segment_name: str = ""
    class_name: str = ""
    overlay_name: str = ""
    access_byte: Optional[int] = None
    access_name: Optional[Literal["RO", "EO", "ER", "RW"]] = None
    extra_byte: Optional[int] = None


@dataclass
class ParsedGrpDef(ParsedRecord):
    """GRPDEF - Group definition."""
    name: str
    name_index: int
    is_flat: bool = False
    components: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ParsedPubDef(ParsedRecord):
    """PUBDEF/LPUBDEF - Public definitions."""
    is_32bit: bool
    is_local: bool
    base_group: str
    base_segment: str
    absolute_frame: Optional[int] = None
    frame_note: Optional[str] = None
    symbols: List[PubDefSymbol] = field(default_factory=list)


@dataclass
class ParsedExtDef(ParsedRecord):
    """EXTDEF/LEXTDEF - External definitions."""
    is_local: bool
    externals: List[ExtDefEntry] = field(default_factory=list)


@dataclass
class ParsedCExtDef(ParsedRecord):
    """CEXTDEF - COMDAT external definitions."""
    externals: List[CExtDefEntry] = field(default_factory=list)


@dataclass
class ParsedModEnd(ParsedRecord):
    """MODEND - Module end."""
    mod_type: int
    is_main: bool
    has_start: bool
    is_relocatable: bool
    start_address: Optional[StartAddress] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class ParsedLinNum(ParsedRecord):
    """LINNUM - Line number information."""
    is_32bit: bool
    base_group: str
    base_segment: str
    entries: List[LineEntry] = field(default_factory=list)


@dataclass
class ParsedVerNum(ParsedRecord):
    """VERNUM - Version number."""
    version: str
    tis_base: Optional[str] = None
    vendor_num: Optional[str] = None
    vendor_ver: Optional[str] = None
    vendor_name: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class ParsedVendExt(ParsedRecord):
    """VENDEXT - Vendor extension."""
    vendor_num: int
    vendor_name: Optional[str] = None
    extension_data: Optional[bytes] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class ParsedLocSym(ParsedRecord):
    """LOCSYM - Local symbols (obsolete)."""
    base_group: str
    base_segment: str
    absolute_frame: Optional[int] = None
    frame_note: Optional[str] = None
    symbols: List[PubDefSymbol] = field(default_factory=list)


@dataclass
class ParsedTypDef(ParsedRecord):
    """TYPDEF - Type definition."""
    name: Optional[str] = None
    en_byte: int = 0
    format: Literal["Microsoft", "Intel", ""] = ""
    leaves: List[TypDefLeaf] = field(default_factory=list)


# Data record models

@dataclass
class ParsedLEData(ParsedRecord):
    """LEDATA - Logical enumerated data."""
    is_32bit: bool
    segment: str
    segment_index: int
    offset: int
    data_length: int
    data_preview: Optional[bytes] = None


@dataclass
class ParsedLIDataBlock:
    """A single LIDATA block (can be nested)."""
    repeat_count: int
    block_count: int
    content: Optional[bytes] = None  # If block_count == 0
    nested_blocks: List['ParsedLIDataBlock'] = field(default_factory=list)


@dataclass
class ParsedLIData(ParsedRecord):
    """LIDATA - Logical iterated data."""
    is_32bit: bool
    segment: str
    segment_index: int
    offset: int
    blocks: List[ParsedLIDataBlock] = field(default_factory=list)


@dataclass
class ParsedThread:
    """FIXUPP thread subrecord."""
    kind: ThreadKind
    thread_num: int
    method: int
    method_name: str
    index: Optional[int] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class ParsedFixup:
    """FIXUPP fixup subrecord."""
    data_offset: int
    location: str
    mode: FixupMode
    frame_method: int
    frame_source: str
    target_method: int
    target_source: str
    frame_datum: Optional[int] = None
    target_datum: Optional[int] = None
    displacement: Optional[int] = None


@dataclass
class ParsedFixupp(ParsedRecord):
    """FIXUPP - Fixup record."""
    is_32bit: bool
    subrecords: List[Union[ParsedThread, ParsedFixup]] = field(default_factory=list)


# Microsoft extension models

@dataclass
class ParsedComDef(ParsedRecord):
    """COMDEF/LCOMDEF - Communal definitions."""
    is_local: bool
    definitions: List[ComDefDefinition] = field(default_factory=list)


@dataclass
class ParsedComDat(ParsedRecord):
    """COMDAT - Initialized communal data."""
    is_32bit: bool
    flags: int
    continuation: bool
    iterated: bool
    local: bool
    data_in_code: bool
    attributes: int
    selection: str
    allocation: str
    alignment: str
    enum_offset: int
    type_index: int
    base_group: Optional[str] = None
    base_segment: Optional[str] = None
    absolute_frame: Optional[int] = None
    symbol: str = ""
    data_length: int = 0


@dataclass
class ParsedBakPat(ParsedRecord):
    """BAKPAT - Backpatch record."""
    is_32bit: bool
    records: List[BackpatchRecord] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ParsedNBkPat(ParsedRecord):
    """NBKPAT - Named backpatch record."""
    is_32bit: bool
    records: List[NamedBackpatchRecord] = field(default_factory=list)


@dataclass
class ParsedLinSym(ParsedRecord):
    """LINSYM - Line numbers for symbol."""
    is_32bit: bool
    continuation: bool
    symbol: str
    entries: List[LineEntry] = field(default_factory=list)


@dataclass
class ParsedAlias(ParsedRecord):
    """ALIAS - Alias definitions."""
    aliases: List[AliasEntry] = field(default_factory=list)


# Library record models

@dataclass
class ParsedLibHdr(ParsedRecord):
    """Library header (F0H)."""
    page_size: int
    dict_offset: int
    dict_blocks: int
    flags: int
    case_sensitive: bool


@dataclass
class ParsedLibEnd(ParsedRecord):
    """Library end (F1H)."""
    pass


@dataclass
class ParsedLibDict(ParsedRecord):
    """Library dictionary."""
    entries: List[DictEntry] = field(default_factory=list)
    total_entries: int = 0


@dataclass
class ParsedExtDict(ParsedRecord):
    """Extended dictionary."""
    length: int
    num_modules: int
    modules: List[ExtDictModule] = field(default_factory=list)


# Obsolete record models

@dataclass
class ParsedRheadr(ParsedRecord):
    """RHEADR - R-Module header (obsolete)."""
    name: Optional[str] = None
    attributes: Optional[bytes] = None


@dataclass
class ParsedRegInt(ParsedRecord):
    """REGINT - Register initialization (obsolete)."""
    registers: List[RegisterEntry] = field(default_factory=list)


@dataclass
class ParsedReDataPeData(ParsedRecord):
    """REDATA/PEDATA - Enumerated data (obsolete)."""
    record_type: Literal["REDATA", "PEDATA"]
    segment: Optional[str] = None
    segment_index: Optional[int] = None
    frame: Optional[int] = None
    offset: int = 0
    physical_address: Optional[int] = None
    data_length: int = 0
    data_preview: Optional[bytes] = None


@dataclass
class ParsedRiDataPiData(ParsedRecord):
    """RIDATA/PIDATA - Iterated data (obsolete)."""
    record_type: Literal["RIDATA", "PIDATA"]
    segment: Optional[str] = None
    segment_index: Optional[int] = None
    frame: Optional[int] = None
    offset: int = 0
    physical_address: Optional[int] = None
    remaining_bytes: int = 0


@dataclass
class ParsedOvlDef(ParsedRecord):
    """OVLDEF - Overlay definition (obsolete)."""
    overlay_name: str
    attribute: Optional[int] = None
    file_location: Optional[int] = None
    additional_data: Optional[bytes] = None


@dataclass
class ParsedEndRec(ParsedRecord):
    """ENDREC - End record (obsolete)."""
    pass


@dataclass
class ParsedBlkDef(ParsedRecord):
    """BLKDEF - Block definition (obsolete)."""
    base_group: str
    base_segment: str
    frame: Optional[int] = None
    block_name: str = ""
    offset: int = 0
    debug_length: Optional[int] = None
    debug_data: Optional[bytes] = None


@dataclass
class ParsedBlkEnd(ParsedRecord):
    """BLKEND - Block end (obsolete)."""
    pass


@dataclass
class ParsedDebSym(ParsedRecord):
    """DEBSYM - Debug symbols (obsolete)."""
    data: Optional[bytes] = None


@dataclass
class ParsedObsoleteLib(ParsedRecord):
    """Obsolete Intel library records."""
    record_type: Literal["LIBHED", "LIBNAM", "LIBLOC", "LIBDIC"]
    data: Optional[bytes] = None
    modules: List[str] = field(default_factory=list)
    locations: List[LibLocEntry] = field(default_factory=list)


# COMENT models

@dataclass
class ParsedComent(ParsedRecord):
    """COMENT - Comment record."""
    comment_class: int
    class_name: str
    no_purge: bool
    no_list: bool
    content: Optional['ParsedComentContent'] = None
    raw_data: Optional[bytes] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class ParsedComentContent:
    """Base class for COMENT content."""
    pass


@dataclass
class ComentTranslator(ParsedComentContent):
    """Translator identification."""
    translator: str


@dataclass
class ComentCopyright(ParsedComentContent):
    """Copyright notice."""
    copyright: str


@dataclass
class ComentLibSpec(ParsedComentContent):
    """Library specifier (obsolete)."""
    library: str


@dataclass
class ComentDosseg(ParsedComentContent):
    """DOSSEG ordering."""
    pass


@dataclass
class ComentNewOmf(ParsedComentContent):
    """New OMF extension marker."""
    data: Optional[bytes] = None


@dataclass
class ComentLinkPass(ParsedComentContent):
    """Link pass separator."""
    pass_num: Optional[int] = None


@dataclass
class ComentLibMod(ParsedComentContent):
    """Library module name."""
    module_name: str


@dataclass
class ComentExeStr(ParsedComentContent):
    """Executable string."""
    exe_string: str


@dataclass
class ComentIncErr(ParsedComentContent):
    """Incremental compilation error."""
    pass


@dataclass
class ComentNoPad(ParsedComentContent):
    """No segment padding."""
    pass


@dataclass
class ComentWkExt(ParsedComentContent):
    """Weak extern definitions."""
    entries: List[WeakExternEntry] = field(default_factory=list)


@dataclass
class ComentLzExt(ParsedComentContent):
    """Lazy extern definitions."""
    entries: List[LazyExternEntry] = field(default_factory=list)


@dataclass
class ComentEasyOmf(ParsedComentContent):
    """Easy OMF-386 marker."""
    marker: Optional[str] = None


@dataclass
class ComentOmfExtensions(ParsedComentContent):
    """OMF Extensions (A0 subtypes)."""
    subtype: int
    subtype_name: str
    content: Optional['ParsedA0Content'] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class ParsedA0Content:
    """Base for A0 subtype content."""
    pass


@dataclass
class A0ImpDef(ParsedA0Content):
    """IMPDEF - Import definition."""
    by_ordinal: bool
    internal_name: str
    module_name: str
    entry_name: Optional[str] = None
    ordinal: Optional[int] = None


@dataclass
class A0ExpDef(ParsedA0Content):
    """EXPDEF - Export definition."""
    exported_name: str
    internal_name: str
    by_ordinal: bool
    resident: bool
    no_data: bool
    parm_count: int
    ordinal: Optional[int] = None


@dataclass
class A0IncDef(ParsedA0Content):
    """INCDEF - Incremental definition."""
    extdef_delta: int
    linnum_delta: int


@dataclass
class A0ProtectedMemory(ParsedA0Content):
    """Protected memory library."""
    pass


@dataclass
class A0LnkDir(ParsedA0Content):
    """LNKDIR - Linker directive."""
    bit_flags: int
    flags_meanings: List[str] = field(default_factory=list)
    pcode_version: int = 0
    cv_version: int = 0


@dataclass
class A0BigEndian(ParsedA0Content):
    """Big-endian marker."""
    pass


@dataclass
class A0PreComp(ParsedA0Content):
    """Precompiled types marker."""
    pass


# Microsoft COMENT content models

@dataclass
class ComentDosVersion(ParsedComentContent):
    """MS-DOS version (obsolete)."""
    major: Optional[int] = None
    minor: Optional[int] = None


@dataclass
class ComentMemoryModel(ParsedComentContent):
    """Memory model."""
    model: str


@dataclass
class ComentDefaultLibrary(ParsedComentContent):
    """Default library search."""
    library: str


@dataclass
class ComentComment(ParsedComentContent):
    """Comment text."""
    comment: str


@dataclass
class ComentCompiler(ParsedComentContent):
    """Compiler identification."""
    compiler: str


@dataclass
class ComentDate(ParsedComentContent):
    """Date stamp."""
    date: str


@dataclass
class ComentTimestamp(ParsedComentContent):
    """Timestamp."""
    timestamp: str


@dataclass
class ComentUser(ParsedComentContent):
    """User-defined comment."""
    user: str


@dataclass
class ComentDependencyFile(ParsedComentContent):
    """Dependency file (Borland)."""
    dependency: str


@dataclass
class ComentCmdLine(ParsedComentContent):
    """Command line (QuickC)."""
    cmdline: str


@dataclass
class Coment32BitLinker(ParsedComentContent):
    """32-bit linker extension."""
    data: Optional[bytes] = None


# Result container

@dataclass
class ParseResult:
    """Container for a parsed record result."""
    record_type: int
    record_name: str
    offset: int
    length: int
    checksum: Optional[int]
    checksum_valid: bool
    parsed: Optional[ParsedRecord] = None
    error: Optional[str] = None
    raw_content: Optional[bytes] = None
