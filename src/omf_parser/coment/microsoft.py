"""Microsoft COMENT class handlers."""

from . import coment_class
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


@coment_class(0x9C)
def handle_dos_version(omf, sub, flags, text):
    """MS-DOS Version (obsolete)."""
    major = text[0] if text and len(text) >= 1 else None
    minor = text[1] if text and len(text) >= 2 else None
    return ComentDosVersion(major=major, minor=minor)


@coment_class(0x9D)
def handle_memory_model(omf, sub, flags, text):
    """Memory Model."""
    decoded = _decode_text(text)
    return ComentMemoryModel(model=decoded)


@coment_class(0x9F)
def handle_default_library(omf, sub, flags, text):
    """Default Library Search."""
    decoded = _decode_text(text)
    return ComentDefaultLibrary(library=decoded)


@coment_class(0xDA)
def handle_comment(omf, sub, flags, text):
    """Comment text."""
    decoded = _decode_text(text)
    return ComentComment(comment=decoded)


@coment_class(0xDB)
def handle_compiler(omf, sub, flags, text):
    """Compiler identification."""
    decoded = _decode_text(text)
    return ComentCompiler(compiler=decoded)


@coment_class(0xDC)
def handle_date(omf, sub, flags, text):
    """Date stamp."""
    decoded = _decode_text(text)
    return ComentDate(date=decoded)


@coment_class(0xDD)
def handle_timestamp(omf, sub, flags, text):
    """Timestamp."""
    decoded = _decode_text(text)
    return ComentTimestamp(timestamp=decoded)


@coment_class(0xDF)
def handle_user(omf, sub, flags, text):
    """User-defined comment."""
    decoded = _decode_text(text)
    return ComentUser(user=decoded)


@coment_class(0xE9)
def handle_dependency_file(omf, sub, flags, text):
    """Dependency File (Borland)."""
    decoded = _decode_text(text)
    return ComentDependencyFile(dependency=decoded)


@coment_class(0xFF)
def handle_cmdline(omf, sub, flags, text):
    """Command Line (QuickC)."""
    decoded = _decode_text(text)
    return ComentCmdLine(cmdline=decoded)


@coment_class(0xB0, 0xB1)
def handle_32bit_linker(omf, sub, flags, text):
    """32-bit linker extension."""
    return Coment32BitLinker(data=text if text else None)
