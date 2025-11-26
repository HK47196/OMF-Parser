"""Microsoft COMENT class handlers."""

from . import coment_class
from ..constants import CommentClass
from ..models import (
    ComentDosVersion, ComentDefaultLibrary,
    ComentComment, ComentCompiler, ComentDate, ComentTimestamp,
    ComentUser, ComentDependencyFile, ComentCmdLine, Coment32BitLinker,
    ComentProcModel
)
from ..protocols import OMFFileProtocol
from ..parsing import RecordParser


def _decode_text(text: bytes) -> str:
    """Helper to decode text bytes."""
    if text:
        try:
            return text.decode('ascii', errors='replace')
        except Exception:
            return text.hex()
    return ""


@coment_class(CommentClass.MSDOS_VERSION)
def handle_dos_version(omf: OMFFileProtocol, sub: RecordParser, flags: int, text: bytes) -> ComentDosVersion:
    """MS-DOS Version (obsolete)."""
    major = text[0] if text and len(text) >= 1 else None
    minor = text[1] if text and len(text) >= 2 else None
    return ComentDosVersion(major=major, minor=minor)


@coment_class(CommentClass.MS_PROC_MODEL)
def handle_ms_proc_model(omf: OMFFileProtocol, sub: RecordParser, flags: int, text: bytes) -> ComentProcModel:
    """MS Processor/Model - same format as Watcom 0x9B."""
    from .watcom import parse_proc_model
    return parse_proc_model(text, omf.variant.omf_variant)


@coment_class(CommentClass.DEFAULT_LIBRARY)
def handle_default_library(omf: OMFFileProtocol, sub: RecordParser, flags: int, text: bytes) -> ComentDefaultLibrary:
    """Default Library Search."""
    decoded = _decode_text(text)
    return ComentDefaultLibrary(library=decoded)


@coment_class(CommentClass.COMMENT)
def handle_comment(omf: OMFFileProtocol, sub: RecordParser, flags: int, text: bytes) -> ComentComment:
    """Comment text."""
    decoded = _decode_text(text)
    return ComentComment(comment=decoded)


@coment_class(CommentClass.COMPILER)
def handle_compiler(omf: OMFFileProtocol, sub: RecordParser, flags: int, text: bytes) -> ComentCompiler:
    """Compiler identification."""
    decoded = _decode_text(text)
    return ComentCompiler(compiler=decoded)


@coment_class(CommentClass.DATE)
def handle_date(omf: OMFFileProtocol, sub: RecordParser, flags: int, text: bytes) -> ComentDate:
    """Date stamp."""
    decoded = _decode_text(text)
    return ComentDate(date=decoded)


@coment_class(CommentClass.TIMESTAMP)
def handle_timestamp(omf: OMFFileProtocol, sub: RecordParser, flags: int, text: bytes) -> ComentTimestamp:
    """Timestamp."""
    decoded = _decode_text(text)
    return ComentTimestamp(timestamp=decoded)


@coment_class(CommentClass.USER)
def handle_user(omf: OMFFileProtocol, sub: RecordParser, flags: int, text: bytes) -> ComentUser:
    """User-defined comment."""
    decoded = _decode_text(text)
    return ComentUser(user=decoded)


@coment_class(CommentClass.DEPENDENCY)
def handle_dependency_file(omf: OMFFileProtocol, sub: RecordParser, flags: int, text: bytes) -> ComentDependencyFile:
    """Dependency File (Borland)."""
    decoded = _decode_text(text)
    return ComentDependencyFile(dependency=decoded)


@coment_class(CommentClass.COMMANDLINE)
def handle_cmdline(omf: OMFFileProtocol, sub: RecordParser, flags: int, text: bytes) -> ComentCmdLine:
    """Command Line (QuickC)."""
    decoded = _decode_text(text)
    return ComentCmdLine(cmdline=decoded)


@coment_class(CommentClass.LINKER_32BIT, CommentClass.LINKER_32BIT_ALT)
def handle_32bit_linker(omf: OMFFileProtocol, sub: RecordParser, flags: int, text: bytes) -> Coment32BitLinker:
    """32-bit linker extension."""
    return Coment32BitLinker(data=text if text else None)
