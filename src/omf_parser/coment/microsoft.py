"""Microsoft COMENT class handlers."""

from . import coment_class
from ..constants import CommentClass
from ..models import (
    ComentDosVersion, ComentMemoryModel, ComentDefaultLibrary,
    ComentComment, ComentCompiler, ComentDate, ComentTimestamp,
    ComentUser, ComentDependencyFile, ComentCmdLine, Coment32BitLinker
)


def _decode_text(text):
    """Helper to decode text bytes."""
    if text:
        try:
            return text.decode('ascii', errors='replace')
        except:
            return text.hex()
    return ""


@coment_class(CommentClass.MSDOS_VERSION)
def handle_dos_version(omf, sub, flags, text):
    """MS-DOS Version (obsolete)."""
    major = text[0] if text and len(text) >= 1 else None
    minor = text[1] if text and len(text) >= 2 else None
    return ComentDosVersion(major=major, minor=minor)


@coment_class(CommentClass.MEMORY_MODEL)
def handle_memory_model(omf, sub, flags, text):
    """Memory Model."""
    decoded = _decode_text(text)
    return ComentMemoryModel(model=decoded)


@coment_class(CommentClass.DEFAULT_LIBRARY)
def handle_default_library(omf, sub, flags, text):
    """Default Library Search."""
    decoded = _decode_text(text)
    return ComentDefaultLibrary(library=decoded)


@coment_class(CommentClass.COMMENT)
def handle_comment(omf, sub, flags, text):
    """Comment text."""
    decoded = _decode_text(text)
    return ComentComment(comment=decoded)


@coment_class(CommentClass.COMPILER)
def handle_compiler(omf, sub, flags, text):
    """Compiler identification."""
    decoded = _decode_text(text)
    return ComentCompiler(compiler=decoded)


@coment_class(CommentClass.DATE)
def handle_date(omf, sub, flags, text):
    """Date stamp."""
    decoded = _decode_text(text)
    return ComentDate(date=decoded)


@coment_class(CommentClass.TIMESTAMP)
def handle_timestamp(omf, sub, flags, text):
    """Timestamp."""
    decoded = _decode_text(text)
    return ComentTimestamp(timestamp=decoded)


@coment_class(CommentClass.USER)
def handle_user(omf, sub, flags, text):
    """User-defined comment."""
    decoded = _decode_text(text)
    return ComentUser(user=decoded)


@coment_class(CommentClass.DEPENDENCY)
def handle_dependency_file(omf, sub, flags, text):
    """Dependency File (Borland)."""
    decoded = _decode_text(text)
    return ComentDependencyFile(dependency=decoded)


@coment_class(CommentClass.COMMANDLINE)
def handle_cmdline(omf, sub, flags, text):
    """Command Line (QuickC)."""
    decoded = _decode_text(text)
    return ComentCmdLine(cmdline=decoded)


@coment_class(CommentClass.LINKER_32BIT, CommentClass.LINKER_32BIT_ALT)
def handle_32bit_linker(omf, sub, flags, text):
    """32-bit linker extension."""
    return Coment32BitLinker(data=text if text else None)
