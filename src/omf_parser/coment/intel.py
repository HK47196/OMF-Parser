"""Intel/TIS standard COMENT class handlers."""

from . import coment_class
from ..constants import (
    CommentClass, A0Subtype, ExpdefFlags, LnkdirFlags, SignedConversion,
    A0_SUBTYPES
)
from ..models import (
    ComentTranslator, ComentCopyright, ComentLibSpec, ComentDosseg,
    ComentNewOmf, ComentLinkPass, ComentLibMod, ComentExeStr,
    ComentIncErr, ComentNoPad, ComentWkExt, ComentLzExt,
    ComentEasyOmf, ComentOmfExtensions,
    A0ImpDef, A0ExpDef, A0IncDef, A0ProtectedMemory, A0LnkDir,
    A0BigEndian, A0PreComp
)


def _decode_text(text):
    """Helper to decode text bytes."""
    if text:
        try:
            return text.decode('ascii', errors='replace')
        except:
            return None
    return None


@coment_class(CommentClass.TRANSLATOR)
def handle_translator(omf, sub, flags, text):
    """Translator - identifies compiler/assembler."""
    decoded = _decode_text(text)
    return ComentTranslator(translator=decoded or text.hex() if text else "")


@coment_class(CommentClass.COPYRIGHT)
def handle_copyright(omf, sub, flags, text):
    """Intel Copyright."""
    decoded = _decode_text(text)
    return ComentCopyright(copyright=decoded or text.hex() if text else "")


@coment_class(CommentClass.LIBSPEC)
def handle_libspec(omf, sub, flags, text):
    """Library Specifier (obsolete)."""
    decoded = _decode_text(text)
    return ComentLibSpec(library=decoded or text.hex() if text else "")


@coment_class(CommentClass.DOSSEG)
def handle_dosseg(omf, sub, flags, text):
    """DOSSEG - DOS segment ordering."""
    return ComentDosseg()


@coment_class(CommentClass.NEW_OMF)
def handle_new_omf(omf, sub, flags, text):
    """New OMF Extension."""
    return ComentNewOmf(data=text if text else None)


@coment_class(CommentClass.LINK_PASS)
def handle_link_pass(omf, sub, flags, text):
    """Link Pass Separator."""
    pass_num = text[0] if text and len(text) >= 1 else None
    return ComentLinkPass(pass_num=pass_num)


@coment_class(CommentClass.LIBMOD)
def handle_libmod(omf, sub, flags, text):
    """LIBMOD - Library Module Name."""
    decoded = _decode_text(text)
    return ComentLibMod(module_name=decoded or text.hex() if text else "")


@coment_class(CommentClass.EXESTR)
def handle_exestr(omf, sub, flags, text):
    """EXESTR - Executable String."""
    decoded = _decode_text(text)
    return ComentExeStr(exe_string=decoded or text.hex() if text else "")


@coment_class(CommentClass.INCERR)
def handle_incerr(omf, sub, flags, text):
    """INCERR - Incremental Compilation Error."""
    return ComentIncErr()


@coment_class(CommentClass.NOPAD)
def handle_nopad(omf, sub, flags, text):
    """NOPAD - No Segment Padding."""
    return ComentNoPad()


@coment_class(CommentClass.WKEXT)
def handle_wkext(omf, sub, flags, text):
    """WKEXT - Weak Extern."""
    result = ComentWkExt()
    pos = 0
    while pos < len(text) - 1:
        weak_idx = text[pos]
        default_idx = text[pos + 1]
        result.entries.append({
            'weak_extdef_index': weak_idx,
            'default_resolution_index': default_idx
        })
        pos += 2
    return result


@coment_class(CommentClass.LZEXT)
def handle_lzext(omf, sub, flags, text):
    """LZEXT - Lazy Extern."""
    result = ComentLzExt()
    pos = 0
    while pos < len(text) - 1:
        lazy_idx = text[pos]
        default_idx = text[pos + 1]
        result.entries.append({
            'lazy_extdef_index': lazy_idx,
            'default_resolution_index': default_idx
        })
        pos += 2
    return result


@coment_class(CommentClass.EASY_OMF)
def handle_easy_omf(omf, sub, flags, text):
    """Easy OMF-386 marker (PharLap)."""
    omf.features.add('easy_omf')
    omf.features.add('pharlap')

    decoded = _decode_text(text) if text else None
    return ComentEasyOmf(marker=decoded)


@coment_class(CommentClass.OMF_EXTENSIONS)
def handle_omf_extensions(omf, sub, flags, text):
    """OMF Extensions (A0 subtypes)."""
    if not text:
        return None

    subtype = text[0]
    subtype_name = A0_SUBTYPES.get(subtype, f"Unknown(0x{subtype:02X})")

    result = ComentOmfExtensions(subtype=subtype, subtype_name=subtype_name)

    remaining = text[1:]

    if subtype == A0Subtype.IMPDEF:
        result.content = _parse_impdef(omf, remaining)
    elif subtype == A0Subtype.EXPDEF:
        result.content = _parse_expdef(omf, remaining)
    elif subtype == A0Subtype.INCDEF:
        result.content = _parse_incdef(omf, remaining)
    elif subtype == A0Subtype.PROTECTED_MEMORY:
        result.content = A0ProtectedMemory()
    elif subtype == A0Subtype.LNKDIR:
        result.content = _parse_lnkdir(omf, remaining)
    elif subtype == A0Subtype.BIG_ENDIAN:
        omf.features.add('big_endian')
        result.content = A0BigEndian()
    elif subtype == A0Subtype.PRECOMP:
        result.content = A0PreComp()
    else:
        result.warnings.append(f"Unknown A0 subtype 0x{subtype:02X}")

    return result


def _parse_impdef(omf, data):
    """Parse IMPDEF subtype."""
    if len(data) < 3:
        return None

    ord_flag = data[0]
    pos = 1

    int_name_len = data[pos]
    int_name = data[pos + 1:pos + 1 + int_name_len].decode('ascii', errors='replace')
    pos += 1 + int_name_len

    if pos >= len(data):
        return None
    mod_name_len = data[pos]
    mod_name = data[pos + 1:pos + 1 + mod_name_len].decode('ascii', errors='replace')
    pos += 1 + mod_name_len

    result = A0ImpDef(
        by_ordinal=(ord_flag != 0),
        internal_name=int_name,
        module_name=mod_name
    )

    if ord_flag == 0:
        if pos < len(data):
            entry_len = data[pos]
            if entry_len == 0:
                result.entry_name = None  # same as internal
            else:
                result.entry_name = data[pos + 1:pos + 1 + entry_len].decode('ascii', errors='replace')
    else:
        if pos + 1 < len(data):
            result.ordinal = data[pos] | (data[pos + 1] << 8)

    return result


def _parse_expdef(omf, data):
    """Parse EXPDEF subtype."""
    if len(data) < 2:
        return None

    exp_flag = data[0]
    pos = 1

    by_ordinal = (exp_flag & ExpdefFlags.ORDINAL) != 0
    resident = (exp_flag & ExpdefFlags.RESIDENT) != 0
    no_data = (exp_flag & ExpdefFlags.NODATA) != 0
    parm_count = exp_flag & ExpdefFlags.PARM_COUNT_MASK

    exp_name_len = data[pos]
    exp_name = data[pos + 1:pos + 1 + exp_name_len].decode('ascii', errors='replace')
    pos += 1 + exp_name_len

    if pos >= len(data):
        return None
    int_name_len = data[pos]
    int_name = data[pos + 1:pos + 1 + int_name_len].decode('ascii', errors='replace') if int_name_len else ""
    pos += 1 + int_name_len

    result = A0ExpDef(
        exported_name=exp_name,
        internal_name=int_name if int_name else exp_name,
        by_ordinal=by_ordinal,
        resident=resident,
        no_data=no_data,
        parm_count=parm_count
    )

    if by_ordinal and pos + 1 < len(data):
        result.ordinal = data[pos] | (data[pos + 1] << 8)

    return result


def _parse_incdef(omf, data):
    """Parse INCDEF subtype."""
    if len(data) < 4:
        return None

    extdef_delta = data[0] | (data[1] << 8)
    linnum_delta = data[2] | (data[3] << 8)

    if extdef_delta >= SignedConversion.THRESHOLD_16BIT:
        extdef_delta -= SignedConversion.OFFSET_16BIT
    if linnum_delta >= SignedConversion.THRESHOLD_16BIT:
        linnum_delta -= SignedConversion.OFFSET_16BIT

    return A0IncDef(extdef_delta=extdef_delta, linnum_delta=linnum_delta)


def _parse_lnkdir(omf, data):
    """Parse LNKDIR subtype."""
    if len(data) < 3:
        return None

    bit_flags = data[0]
    pcode_ver = data[1]
    cv_ver = data[2]

    result = A0LnkDir(
        bit_flags=bit_flags,
        pcode_version=pcode_ver,
        cv_version=cv_ver
    )

    if bit_flags & LnkdirFlags.NEW_EXE:
        result.flags_meanings.append("Output new .EXE format")
    if bit_flags & LnkdirFlags.OMIT_PUBLICS:
        result.flags_meanings.append("Omit CodeView $PUBLICS")
    if bit_flags & LnkdirFlags.RUN_MPC:
        result.flags_meanings.append("Run MPC utility")

    return result
