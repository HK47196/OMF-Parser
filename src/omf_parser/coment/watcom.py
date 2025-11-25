"""Watcom COMENT class handlers."""

from datetime import datetime

from . import coment_class
from ..constants import CommentClass
from ..models import (
    ComentProcModel, ComentLinkerDirective,
    LinkerDirSourceLang, LinkerDirDefaultLib, LinkerDirOptFarCalls,
    LinkerDirOptUnsafe, LinkerDirVFTableDef, LinkerDirVFReference,
    LinkerDirPackData, LinkerDirFlatAddrs, LinkerDirTimestamp
)
from ..parsing import RecordParser


PROCESSOR_NAMES = {
    '0': '8086',
    '2': '80286',
    '3': '80386+',
}

MEM_MODEL_NAMES = {
    's': 'Small',
    'm': 'Medium',
    'c': 'Compact',
    'l': 'Large',
    'h': 'Huge',
    'f': 'Flat',
}

FP_MODE_NAMES = {
    'e': 'Emulated inline',
    'c': 'Emulator calls',
    'p': '80x87 inline',
}


def parse_proc_model(text: bytes) -> ComentProcModel:
    """Parse processor/model string (shared by 0x9B and 0x9D)."""
    if not text or len(text) < 4:
        return ComentProcModel(
            processor='Unknown',
            processor_raw='',
            mem_model='Unknown',
            mem_model_raw='',
            optimized=False,
            fp_mode='Unknown',
            fp_mode_raw='',
            pic=False,
        )

    proc_raw = chr(text[0])
    model_raw = chr(text[1])
    opt_raw = chr(text[2])
    fp_raw = chr(text[3])
    pic = len(text) >= 5 and chr(text[4]) == 'i'

    return ComentProcModel(
        processor=PROCESSOR_NAMES.get(proc_raw, f'Unknown({proc_raw})'),
        processor_raw=proc_raw,
        mem_model=MEM_MODEL_NAMES.get(model_raw, f'Unknown({model_raw})'),
        mem_model_raw=model_raw,
        optimized=(opt_raw == 'O'),
        fp_mode=FP_MODE_NAMES.get(fp_raw, f'Unknown({fp_raw})'),
        fp_mode_raw=fp_raw,
        pic=pic,
    )


@coment_class(CommentClass.WAT_PROC_MODEL)
def handle_wat_proc_model(omf, sub, flags, text):
    """Watcom Processor & Model info (0x9B)."""
    return parse_proc_model(text)


LINKER_DIRECTIVE_NAMES = {
    0x44: ('D', 'Source Language'),
    0x4C: ('L', 'Default Library'),
    0x4F: ('O', 'Optimize Far Calls'),
    0x55: ('U', 'Optimization Unsafe'),
    0x56: ('V', 'VF Table Definition'),
    0x50: ('P', 'VF Pure Definition'),
    0x52: ('R', 'VF Reference'),
    0x37: ('7', 'Pack Far Data'),
    0x46: ('F', 'Flat Addresses'),
    0x54: ('T', 'Object Timestamp'),
}


def _safe_lookup(table, index, prefix=""):
    """Safely look up an index in a 1-based table."""
    if index <= 0 or index >= len(table):
        return f"{prefix}[{index}]"
    return table[index]


@coment_class(CommentClass.LINKER_DIRECTIVE)
def handle_linker_directive(omf, sub, flags, text):
    """Watcom Linker Directive (0xFE)."""
    if not text:
        return None

    directive = text[0]
    code, name = LINKER_DIRECTIVE_NAMES.get(directive, (chr(directive), f'Unknown(0x{directive:02X})'))

    result = ComentLinkerDirective(directive_code=code, directive_name=name)
    remaining = text[1:]

    if directive == 0x44:  # 'D' - Source Language
        result.content = _parse_source_language(omf, remaining, result)
    elif directive == 0x4C:  # 'L' - Default Library
        result.content = _parse_default_library(omf, remaining, result)
    elif directive == 0x4F:  # 'O' - Optimize Far Calls
        result.content = _parse_opt_far_calls(omf, remaining, result)
    elif directive == 0x55:  # 'U' - Optimization Unsafe
        result.content = LinkerDirOptUnsafe()
    elif directive == 0x56:  # 'V' - VF Table Definition
        result.content = _parse_vf_table_def(omf, remaining, result, is_pure=False)
    elif directive == 0x50:  # 'P' - VF Pure Definition
        result.content = _parse_vf_table_def(omf, remaining, result, is_pure=True)
    elif directive == 0x52:  # 'R' - VF Reference
        result.content = _parse_vf_reference(omf, remaining, result)
    elif directive == 0x37:  # '7' - Pack Far Data
        result.content = _parse_pack_data(omf, remaining, result)
    elif directive == 0x46:  # 'F' - Flat Addresses
        result.content = LinkerDirFlatAddrs()
    elif directive == 0x54:  # 'T' - Object Timestamp
        result.content = _parse_timestamp(omf, remaining, result)
    else:
        result.warnings.append(f"Unknown linker directive code: 0x{directive:02X}")

    return result


def _parse_source_language(omf, data, result):
    """Parse 'D' - Source Language directive."""
    if len(data) < 2:
        result.warnings.append("Source language directive too short")
        return None

    major = data[0]
    minor = data[1]
    language = data[2:].decode('ascii', errors='replace') if len(data) > 2 else ""

    return LinkerDirSourceLang(
        major_version=major,
        minor_version=minor,
        language=language
    )


def _parse_default_library(omf, data, result):
    """Parse 'L' - Default Library directive."""
    if len(data) < 2:
        result.warnings.append("Default library directive too short")
        return None

    priority_char = chr(data[0])
    if priority_char.isdigit():
        priority = int(priority_char)
    else:
        result.warnings.append(f"Non-digit priority character: {repr(priority_char)}")
        priority = data[0]

    library_name = data[1:].decode('ascii', errors='replace')

    return LinkerDirDefaultLib(
        priority=priority,
        library_name=library_name
    )


def _parse_opt_far_calls(omf, data, result):
    """Parse 'O' - Optimize Far Calls directive."""
    parser = RecordParser(data)
    seg_idx = parser.parse_index()

    seg_name = _safe_lookup(omf.segdefs, seg_idx, "Segment")

    return LinkerDirOptFarCalls(
        segment_index=seg_idx,
        segment_name=seg_name
    )


def _parse_vf_table_def(omf, data, result, is_pure):
    """Parse 'V'/'P' - VF Table Definition directive."""
    parser = RecordParser(data)

    vf_ext_idx = parser.parse_index()
    default_ext_idx = parser.parse_index()

    lname_indices = []
    while not parser.at_end():
        lname_idx = parser.parse_index()
        lname_indices.append(lname_idx)

    vf_symbol = _safe_lookup(omf.extdefs, vf_ext_idx, "External")
    default_symbol = _safe_lookup(omf.extdefs, default_ext_idx, "External")

    function_names = []
    for idx in lname_indices:
        function_names.append(_safe_lookup(omf.lnames, idx, "LNAME"))

    return LinkerDirVFTableDef(
        is_pure=is_pure,
        vf_table_ext_index=vf_ext_idx,
        default_ext_index=default_ext_idx,
        lname_indices=lname_indices,
        vf_table_symbol=vf_symbol,
        default_symbol=default_symbol,
        function_names=function_names
    )


def _parse_vf_reference(omf, data, result):
    """Parse 'R' - VF Reference directive."""
    parser = RecordParser(data)

    ext_idx = parser.parse_index()
    type_idx = parser.parse_index()

    ext_symbol = _safe_lookup(omf.extdefs, ext_idx, "External")

    is_comdat = (type_idx == 0)

    content = LinkerDirVFReference(
        ext_index=ext_idx,
        ext_symbol=ext_symbol,
        is_comdat=is_comdat
    )

    if is_comdat:
        lname_idx = parser.parse_index()
        content.lname_index = lname_idx
        content.comdat_name = _safe_lookup(omf.lnames, lname_idx, "LNAME")
    else:
        content.segment_index = type_idx
        content.segment_name = _safe_lookup(omf.segdefs, type_idx, "Segment")

    return content


def _parse_pack_data(omf, data, result):
    """Parse '7' - Pack Far Data directive."""
    if len(data) < 4:
        result.warnings.append("Pack data directive too short (expected 4 bytes)")
        pack_limit = 0
        for i, b in enumerate(data):
            pack_limit |= (b << (8 * i))
    else:
        pack_limit = data[0] | (data[1] << 8) | (data[2] << 16) | (data[3] << 24)

    return LinkerDirPackData(pack_limit=pack_limit)


def _parse_timestamp(omf, data, result):
    """Parse 'T' - Object Timestamp directive."""
    if len(data) < 4:
        result.warnings.append("Timestamp directive too short (expected 4 bytes)")
        timestamp = 0
        for i, b in enumerate(data):
            timestamp |= (b << (8 * i))
    else:
        timestamp = data[0] | (data[1] << 8) | (data[2] << 16) | (data[3] << 24)

    try:
        dt = datetime.fromtimestamp(timestamp)
        readable = dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, OSError):
        readable = None

    return LinkerDirTimestamp(
        timestamp=timestamp,
        timestamp_readable=readable
    )
