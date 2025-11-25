"""Data models for parsed OMF records.

These Pydantic models represent the structured output from parsing OMF records.
They provide runtime type validation and are serializable to JSON.
"""

from enum import Enum
from typing import List, Optional, Union, Literal, Tuple, Annotated

from pydantic import BaseModel, Field, ConfigDict


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


class PubDefSymbol(BaseModel):
    """Symbol entry in PUBDEF/LPUBDEF records."""
    model_config = ConfigDict(strict=True)

    name: str
    offset: int
    type_index: int


class ExtDefEntry(BaseModel):
    """External definition entry."""
    model_config = ConfigDict(strict=True)

    index: int
    name: str
    type_index: int


class CExtDefEntry(BaseModel):
    """COMDAT external definition entry."""
    model_config = ConfigDict(strict=True)

    index: int
    name: str
    type_index: int


class StartAddress(BaseModel):
    """MODEND start address information."""
    model_config = ConfigDict(strict=True)

    frame_method: int
    p_bit: int
    target_method: int
    frame_datum: Optional[int] = None
    target_datum: Optional[int] = None
    target_displacement: Optional[int] = None


class LineEntry(BaseModel):
    """Line number entry in LINNUM/LINSYM records."""
    model_config = ConfigDict(strict=True)

    line: int
    offset: int
    is_end_of_function: bool


class ComDefFarDefinition(BaseModel):
    """FAR COMDEF definition."""
    model_config = ConfigDict(strict=True)

    name: str
    type_index: int
    data_type: int
    kind: Literal["FAR"]
    num_elements: int
    element_size: int
    total_size: int


class ComDefNearDefinition(BaseModel):
    """NEAR COMDEF definition."""
    model_config = ConfigDict(strict=True)

    name: str
    type_index: int
    data_type: int
    kind: Literal["NEAR"]
    size: int


class ComDefBorlandDefinition(BaseModel):
    """Borland COMDEF definition."""
    model_config = ConfigDict(strict=True)

    name: str
    type_index: int
    data_type: int
    kind: Literal["Borland"]
    seg_index: int
    length: int


class ComDefUnknownDefinition(BaseModel):
    """Unknown COMDEF definition."""
    model_config = ConfigDict(strict=True)

    name: str
    type_index: int
    data_type: int
    kind: Literal["Unknown"]
    length: int


ComDefDefinition = Union[ComDefFarDefinition, ComDefNearDefinition, ComDefBorlandDefinition, ComDefUnknownDefinition]


class BackpatchRecord(BaseModel):
    """BAKPAT backpatch record entry."""
    model_config = ConfigDict(strict=True)

    segment: str
    segment_index: int
    location_type: int
    location_name: str
    offset: int
    value: int


class NamedBackpatchRecord(BaseModel):
    """NBKPAT named backpatch record entry."""
    model_config = ConfigDict(strict=True)

    location_type: int
    location_name: str
    symbol: str
    offset: int
    value: int


class AliasEntry(BaseModel):
    """Alias definition entry."""
    model_config = ConfigDict(strict=True)

    alias: str
    substitute: str


class WeakExternEntry(BaseModel):
    """Weak extern definition entry."""
    model_config = ConfigDict(strict=True)

    weak_extdef_index: int
    default_resolution_index: int


class LazyExternEntry(BaseModel):
    """Lazy extern definition entry."""
    model_config = ConfigDict(strict=True)

    lazy_extdef_index: int
    default_resolution_index: int


class DictEntry(BaseModel):
    """Library dictionary entry."""
    model_config = ConfigDict(strict=True)

    block: int
    bucket: int
    symbol: str
    page: int


class ExtDictModule(BaseModel):
    """Extended dictionary module entry."""
    model_config = ConfigDict(strict=True)

    index: int
    page: int
    dep_offset: int


class RegisterEntry(BaseModel):
    """Register initialization entry (obsolete)."""
    model_config = ConfigDict(strict=True)

    reg_name: str
    reg_type: int
    value: int


class TypDefLeafNear(BaseModel):
    """TYPDEF NEAR leaf descriptor."""
    model_config = ConfigDict(strict=True)

    type: Literal["NEAR"]
    leaf_index: Optional[int] = None
    leaf_type: int
    var_type: str
    var_type_raw: int
    size_bits: int
    size_bytes: int


class TypDefLeafFar(BaseModel):
    """TYPDEF FAR leaf descriptor."""
    model_config = ConfigDict(strict=True)

    type: Literal["FAR"]
    leaf_index: Optional[int] = None
    leaf_type: int
    num_elements: int
    element_type: str
    element_type_index: int


class TypDefLeafUnknown(BaseModel):
    """TYPDEF unknown leaf descriptor."""
    model_config = ConfigDict(strict=True, arbitrary_types_allowed=True)

    type: Literal["Unknown"]
    leaf_index: Optional[int] = None
    leaf_type: int
    remaining: Optional[bytes] = None


TypDefLeaf = Union[TypDefLeafNear, TypDefLeafFar, TypDefLeafUnknown]


class LibLocEntry(BaseModel):
    """Library location entry (obsolete)."""
    model_config = ConfigDict(strict=True)

    module: str
    block_num: int
    byte_offset: int


LNameEntry = Tuple[int, str, bool]

class ParsedRecord(BaseModel):
    """Base class for all parsed record data."""
    model_config = ConfigDict(strict=True, arbitrary_types_allowed=True)


class ParsedComentContent(BaseModel):
    """Base class for COMENT content."""
    model_config = ConfigDict(strict=True, arbitrary_types_allowed=True)


class ParsedA0Content(BaseModel):
    """Base for A0 subtype content."""
    model_config = ConfigDict(strict=True, arbitrary_types_allowed=True)


class ParsedTheadr(ParsedRecord):
    """THEADR/LHEADR - Module header."""
    record_name: Literal["THEADR", "LHEADR"]
    module_name: str


class ParsedLNames(ParsedRecord):
    """LNAMES/LLNAMES - Logical names."""
    record_name: Literal["LNAMES", "LLNAMES (Local)"]
    start_index: int
    end_index: int
    names: List[LNameEntry]


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


class ParsedGrpDef(ParsedRecord):
    """GRPDEF - Group definition."""
    name: str
    name_index: int
    is_flat: bool = False
    components: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ParsedPubDef(ParsedRecord):
    """PUBDEF/LPUBDEF - Public definitions."""
    is_32bit: bool
    is_local: bool
    base_group: str
    base_segment: str
    absolute_frame: Optional[int] = None
    frame_note: Optional[str] = None
    symbols: List[PubDefSymbol] = Field(default_factory=list)


class ParsedExtDef(ParsedRecord):
    """EXTDEF/LEXTDEF - External definitions."""
    is_local: bool
    externals: List[ExtDefEntry] = Field(default_factory=list)


class ParsedCExtDef(ParsedRecord):
    """CEXTDEF - COMDAT external definitions."""
    externals: List[CExtDefEntry] = Field(default_factory=list)


class ParsedModEnd(ParsedRecord):
    """MODEND - Module end."""
    mod_type: int
    is_main: bool
    has_start: bool
    is_relocatable: bool
    start_address: Optional[StartAddress] = None
    warnings: List[str] = Field(default_factory=list)


class ParsedLinNum(ParsedRecord):
    """LINNUM - Line number information."""
    is_32bit: bool
    base_group: str
    base_segment: str
    entries: List[LineEntry] = Field(default_factory=list)


class ParsedVerNum(ParsedRecord):
    """VERNUM - Version number."""
    version: str
    tis_base: Optional[str] = None
    vendor_num: Optional[str] = None
    vendor_ver: Optional[str] = None
    vendor_name: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


class ParsedVendExt(ParsedRecord):
    """VENDEXT - Vendor extension."""
    vendor_num: int
    vendor_name: Optional[str] = None
    extension_data: Optional[bytes] = None
    warnings: List[str] = Field(default_factory=list)


class ParsedLocSym(ParsedRecord):
    """LOCSYM - Local symbols (obsolete)."""
    base_group: str
    base_segment: str
    absolute_frame: Optional[int] = None
    frame_note: Optional[str] = None
    symbols: List[PubDefSymbol] = Field(default_factory=list)


class ParsedTypDef(ParsedRecord):
    """TYPDEF - Type definition."""
    name: Optional[str] = None
    en_byte: int = 0
    format: Literal["Microsoft", "Intel", ""] = ""
    leaves: List[TypDefLeaf] = Field(default_factory=list)


class ParsedLEData(ParsedRecord):
    """LEDATA - Logical enumerated data."""
    is_32bit: bool
    segment: str
    segment_index: int
    offset: int
    data_length: int
    data_preview: Optional[bytes] = None


class ParsedLIDataBlock(BaseModel):
    """A single LIDATA block (can be nested)."""
    model_config = ConfigDict(strict=True, arbitrary_types_allowed=True)

    repeat_count: int
    block_count: int
    content: Optional[bytes] = None
    nested_blocks: List["ParsedLIDataBlock"] = Field(default_factory=list)
    expanded_size: int = 0

    def calculate_expanded_size(self) -> int:
        """Calculate the total expanded size when repeat counts are applied."""
        if self.block_count == 0:
            content_size = len(self.content) if self.content else 0
            self.expanded_size = self.repeat_count * content_size
        else:
            nested_total = sum(b.calculate_expanded_size() for b in self.nested_blocks)
            self.expanded_size = self.repeat_count * nested_total
        return self.expanded_size


class ParsedLIData(ParsedRecord):
    """LIDATA - Logical iterated data."""
    is_32bit: bool
    segment: str
    segment_index: int
    offset: int
    blocks: List[ParsedLIDataBlock] = Field(default_factory=list)
    total_expanded_size: int = 0
    warnings: List[str] = Field(default_factory=list)


class ParsedThread(BaseModel):
    """FIXUPP thread subrecord."""
    model_config = ConfigDict(strict=True)

    kind: ThreadKind
    thread_num: int
    method: int
    method_name: str
    index: Optional[int] = None
    warnings: List[str] = Field(default_factory=list)


class ParsedFixup(BaseModel):
    """FIXUPP fixup subrecord."""
    model_config = ConfigDict(strict=True)

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


class ParsedFixupp(ParsedRecord):
    """FIXUPP - Fixup record."""
    is_32bit: bool
    subrecords: List[Union[ParsedThread, ParsedFixup]] = Field(default_factory=list)


class ParsedComDef(ParsedRecord):
    """COMDEF/LCOMDEF - Communal definitions."""
    is_local: bool
    definitions: List[ComDefDefinition] = Field(default_factory=list)


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
    enum_offset: int = 0
    type_index: int = 0
    base_group: Optional[str] = None
    base_segment: Optional[str] = None
    absolute_frame: Optional[int] = None
    symbol: str = ""
    data_length: int = 0
    iterated_blocks: List["ParsedLIDataBlock"] = Field(default_factory=list)
    iterated_expanded_size: int = 0


class ParsedBakPat(ParsedRecord):
    """BAKPAT - Backpatch record."""
    is_32bit: bool
    records: List[BackpatchRecord] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ParsedNBkPat(ParsedRecord):
    """NBKPAT - Named backpatch record."""
    is_32bit: bool
    records: List[NamedBackpatchRecord] = Field(default_factory=list)


class ParsedLinSym(ParsedRecord):
    """LINSYM - Line numbers for symbol."""
    is_32bit: bool
    continuation: bool
    symbol: str
    entries: List[LineEntry] = Field(default_factory=list)


class ParsedAlias(ParsedRecord):
    """ALIAS - Alias definitions."""
    aliases: List[AliasEntry] = Field(default_factory=list)


class ParsedLibHdr(ParsedRecord):
    """Library header (F0H)."""
    page_size: int
    dict_offset: int
    dict_blocks: int
    flags: int
    case_sensitive: bool


class ParsedLibEnd(ParsedRecord):
    """Library end (F1H)."""
    pass


class ParsedLibDict(ParsedRecord):
    """Library dictionary."""
    entries: List[DictEntry] = Field(default_factory=list)
    total_entries: int = 0


class ParsedExtDict(ParsedRecord):
    """Extended dictionary."""
    length: int
    num_modules: int
    modules: List[ExtDictModule] = Field(default_factory=list)


class ParsedRheadr(ParsedRecord):
    """RHEADR - R-Module header (obsolete)."""
    name: Optional[str] = None
    attributes: Optional[bytes] = None


class ParsedRegInt(ParsedRecord):
    """REGINT - Register initialization (obsolete)."""
    registers: List[RegisterEntry] = Field(default_factory=list)


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


class ParsedRiDataPiData(ParsedRecord):
    """RIDATA/PIDATA - Iterated data (obsolete)."""
    record_type: Literal["RIDATA", "PIDATA"]
    segment: Optional[str] = None
    segment_index: Optional[int] = None
    frame: Optional[int] = None
    offset: int = 0
    physical_address: Optional[int] = None
    remaining_bytes: int = 0


class ParsedOvlDef(ParsedRecord):
    """OVLDEF - Overlay definition (obsolete)."""
    overlay_name: str
    attribute: Optional[int] = None
    file_location: Optional[int] = None
    additional_data: Optional[bytes] = None


class ParsedEndRec(ParsedRecord):
    """ENDREC - End record (obsolete)."""
    pass


class ParsedBlkDef(ParsedRecord):
    """BLKDEF - Block definition (obsolete)."""
    base_group: str
    base_segment: str
    frame: Optional[int] = None
    block_name: str = ""
    offset: int = 0
    debug_length: Optional[int] = None
    debug_data: Optional[bytes] = None


class ParsedBlkEnd(ParsedRecord):
    """BLKEND - Block end (obsolete)."""
    pass


class ParsedDebSym(ParsedRecord):
    """DEBSYM - Debug symbols (obsolete)."""
    data: Optional[bytes] = None


class ParsedObsoleteLib(ParsedRecord):
    """Obsolete Intel library records."""
    record_type: Literal["LIBHED", "LIBNAM", "LIBLOC", "LIBDIC"]
    data: Optional[bytes] = None
    modules: List[str] = Field(default_factory=list)
    locations: List[LibLocEntry] = Field(default_factory=list)


class ParsedComent(ParsedRecord):
    """COMENT - Comment record."""
    comment_class: int
    class_name: str
    no_purge: bool
    no_list: bool
    content: Optional["ParsedComentContent"] = None
    raw_data: Optional[bytes] = None
    warnings: List[str] = Field(default_factory=list)


class ComentTranslator(ParsedComentContent):
    """Translator identification."""
    translator: str


class ComentCopyright(ParsedComentContent):
    """Copyright notice."""
    copyright: str


class ComentLibSpec(ParsedComentContent):
    """Library specifier (obsolete)."""
    library: str


class ComentDosseg(ParsedComentContent):
    """DOSSEG ordering."""
    pass


class ComentNewOmf(ParsedComentContent):
    """New OMF extension marker."""
    data: Optional[bytes] = None


class ComentLinkPass(ParsedComentContent):
    """Link pass separator."""
    pass_num: Optional[int] = None


class ComentLibMod(ParsedComentContent):
    """Library module name."""
    module_name: str


class ComentExeStr(ParsedComentContent):
    """Executable string."""
    exe_string: str


class ComentIncErr(ParsedComentContent):
    """Incremental compilation error."""
    pass


class ComentNoPad(ParsedComentContent):
    """No segment padding."""
    pass


class ComentWkExt(ParsedComentContent):
    """Weak extern definitions."""
    entries: List[WeakExternEntry] = Field(default_factory=list)


class ComentLzExt(ParsedComentContent):
    """Lazy extern definitions."""
    entries: List[LazyExternEntry] = Field(default_factory=list)


class ComentEasyOmf(ParsedComentContent):
    """Easy OMF-386 marker."""
    marker: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


class ComentOmfExtensions(ParsedComentContent):
    """OMF Extensions (A0 subtypes)."""
    subtype: int
    subtype_name: str
    content: Optional["ParsedA0Content"] = None
    warnings: List[str] = Field(default_factory=list)


class A0ImpDef(ParsedA0Content):
    """IMPDEF - Import definition."""
    by_ordinal: bool
    internal_name: str
    module_name: str
    entry_name: Optional[str] = None
    ordinal: Optional[int] = None


class A0ExpDef(ParsedA0Content):
    """EXPDEF - Export definition."""
    exported_name: str
    internal_name: str
    by_ordinal: bool
    resident: bool
    no_data: bool
    parm_count: int
    ordinal: Optional[int] = None


class A0IncDef(ParsedA0Content):
    """INCDEF - Incremental definition."""
    extdef_delta: int
    linnum_delta: int


class A0ProtectedMemory(ParsedA0Content):
    """Protected memory library."""
    pass


class A0LnkDir(ParsedA0Content):
    """LNKDIR - Linker directive."""
    bit_flags: int
    flags_meanings: List[str] = Field(default_factory=list)
    pcode_version: int = 0
    cv_version: int = 0


class A0BigEndian(ParsedA0Content):
    """Big-endian marker."""
    pass


class A0PreComp(ParsedA0Content):
    """Precompiled types marker."""
    pass


class ComentDosVersion(ParsedComentContent):
    """MS-DOS version (obsolete)."""
    major: Optional[int] = None
    minor: Optional[int] = None


class ComentProcModel(ParsedComentContent):
    """Processor and memory model info (Watcom 0x9B / MS 0x9D)."""
    processor: str
    processor_raw: str
    mem_model: str
    mem_model_raw: str
    optimized: bool
    fp_mode: str
    fp_mode_raw: str
    pic: bool


class ComentDefaultLibrary(ParsedComentContent):
    """Default library search."""
    library: str


class ComentComment(ParsedComentContent):
    """Comment text."""
    comment: str


class ComentCompiler(ParsedComentContent):
    """Compiler identification."""
    compiler: str


class ComentDate(ParsedComentContent):
    """Date stamp."""
    date: str


class ComentTimestamp(ParsedComentContent):
    """Timestamp."""
    timestamp: str


class ComentUser(ParsedComentContent):
    """User-defined comment."""
    user: str


class ComentDependencyFile(ParsedComentContent):
    """Dependency file (Borland)."""
    dependency: str


class ComentCmdLine(ParsedComentContent):
    """Command line (QuickC)."""
    cmdline: str


class Coment32BitLinker(ParsedComentContent):
    """32-bit linker extension."""
    data: Optional[bytes] = None


class ParseResult(BaseModel):
    """Container for a parsed record result."""
    model_config = ConfigDict(strict=True, arbitrary_types_allowed=True)

    record_type: int
    record_name: str
    offset: int
    length: int
    checksum: Optional[int]
    checksum_valid: Optional[bool]
    parsed: Optional[ParsedRecord] = None
    error: Optional[str] = None
    raw_content: Optional[bytes] = None


ParsedLIDataBlock.model_rebuild()
ParsedComent.model_rebuild()
ComentOmfExtensions.model_rebuild()
