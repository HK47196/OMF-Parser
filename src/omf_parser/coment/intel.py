"""Intel/TIS standard COMENT class handlers."""

from . import coment_class
from ..constants import (
    A0_SUBTYPES, A0_IMPDEF, A0_EXPDEF, A0_INCDEF,
    A0_PROTECTED_MEMORY, A0_LNKDIR, A0_BIG_ENDIAN, A0_PRECOMP
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


@coment_class(0x00)
def handle_translator(omf, sub, flags, text):
    """Translator - identifies compiler/assembler."""
    decoded = _decode_text(text)
    return ComentTranslator(translator=decoded or text.hex() if text else "")


@coment_class(0x01)
def handle_copyright(omf, sub, flags, text):
    """Intel Copyright."""
    decoded = _decode_text(text)
    return ComentCopyright(copyright=decoded or text.hex() if text else "")


@coment_class(0x81)
def handle_libspec(omf, sub, flags, text):
    """Library Specifier (obsolete)."""
    decoded = _decode_text(text)
    return ComentLibSpec(library=decoded or text.hex() if text else "")


@coment_class(0x9E)
def handle_dosseg(omf, sub, flags, text):
    """DOSSEG - DOS segment ordering."""
    return ComentDosseg()


@coment_class(0xA1)
def handle_new_omf(omf, sub, flags, text):
    """New OMF Extension."""
    return ComentNewOmf(data=text if text else None)


@coment_class(0xA2)
def handle_link_pass(omf, sub, flags, text):
    """Link Pass Separator."""
    pass_num = text[0] if text and len(text) >= 1 else None
    return ComentLinkPass(pass_num=pass_num)


@coment_class(0xA3)
def handle_libmod(omf, sub, flags, text):
    """LIBMOD - Library Module Name."""
    decoded = _decode_text(text)
    return ComentLibMod(module_name=decoded or text.hex() if text else "")


@coment_class(0xA4)
def handle_exestr(omf, sub, flags, text):
    """EXESTR - Executable String."""
    decoded = _decode_text(text)
    return ComentExeStr(exe_string=decoded or text.hex() if text else "")


@coment_class(0xA6)
def handle_incerr(omf, sub, flags, text):
    """INCERR - Incremental Compilation Error."""
    return ComentIncErr()


@coment_class(0xA7)
def handle_nopad(omf, sub, flags, text):
    """NOPAD - No Segment Padding."""
    return ComentNoPad()


@coment_class(0xA8)
def handle_wkext(omf, sub, flags, text):
    """WKEXT - Weak Extern."""
    result = ComentWkExt()
    pos = 0
    while pos < len(text) - 1:
        weak_idx = text[pos]
        default_idx = text[pos + 1]
        result.entries.append({
            'weak_index': weak_idx,
            'default_index': default_idx
        })
        pos += 2
    return result


@coment_class(0xA9)
def handle_lzext(omf, sub, flags, text):
    """LZEXT - Lazy Extern."""
    result = ComentLzExt()
    pos = 0
    while pos < len(text) - 1:
        lazy_idx = text[pos]
        default_idx = text[pos + 1]
        result.entries.append({
            'lazy_index': lazy_idx,
            'default_index': default_idx
        })
        pos += 2
    return result


@coment_class(0xAA)
def handle_easy_omf(omf, sub, flags, text):
    """Easy OMF-386 marker (PharLap)."""
    omf.features.add('easy_omf')
    omf.features.add('pharlap')

    decoded = _decode_text(text) if text else None
    return ComentEasyOmf(marker=decoded)


@coment_class(0xA0)
def handle_omf_extensions(omf, sub, flags, text):
    """OMF Extensions (A0 subtypes)."""
    if not text:
        return None

    subtype = text[0]
    subtype_name = A0_SUBTYPES.get(subtype, f"Unknown(0x{subtype:02X})")

    result = ComentOmfExtensions(subtype=subtype, subtype_name=subtype_name)

    remaining = text[1:]

    if subtype == A0_IMPDEF:
        result.content = _parse_impdef(omf, remaining)
    elif subtype == A0_EXPDEF:
        result.content = _parse_expdef(omf, remaining)
    elif subtype == A0_INCDEF:
        result.content = _parse_incdef(omf, remaining)
    elif subtype == A0_PROTECTED_MEMORY:
        result.content = A0ProtectedMemory()
    elif subtype == A0_LNKDIR:
        result.content = _parse_lnkdir(omf, remaining)
    elif subtype == A0_BIG_ENDIAN:
        omf.features.add('big_endian')
        result.content = A0BigEndian()
    elif subtype == A0_PRECOMP:
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

    by_ordinal = (exp_flag & 0x80) != 0
    resident = (exp_flag & 0x40) != 0
    no_data = (exp_flag & 0x20) != 0
    parm_count = exp_flag & 0x1F

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

    if extdef_delta >= 0x8000:
        extdef_delta -= 0x10000
    if linnum_delta >= 0x8000:
        linnum_delta -= 0x10000

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

    if bit_flags & 0x01:
        result.flags_meanings.append("Output new .EXE format")
    if bit_flags & 0x02:
        result.flags_meanings.append("Omit CodeView $PUBLICS")
    if bit_flags & 0x04:
        result.flags_meanings.append("Run MPC utility")

    return result
