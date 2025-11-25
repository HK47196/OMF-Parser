"""Obsolete Intel 8086 record handlers."""

from . import omf_record
from ..constants import REGISTER_NAMES
from ..models import (
    ParsedRheadr, ParsedRegInt, ParsedReDataPeData, ParsedRiDataPiData,
    ParsedOvlDef, ParsedEndRec, ParsedBlkDef, ParsedBlkEnd,
    ParsedDebSym, ParsedObsoleteLib, RegisterEntry
)


@omf_record(0x6E)
def handle_rheadr(omf, record):
    """Handle RHEADR (6EH) - R-Module Header."""
    sub = omf.make_parser(record)
    name = sub.parse_name()

    result = ParsedRheadr(name=name if name else None)

    if sub.bytes_remaining() > 0:
        result.attributes = sub.data[sub.offset:]

    return result


@omf_record(0x70)
def handle_regint(omf, record):
    """Handle REGINT (70H) - Register Initialization."""
    sub = omf.make_parser(record)

    result = ParsedRegInt()

    while sub.bytes_remaining() >= 3:
        reg_type = sub.read_byte()
        value = sub.parse_numeric(2)
        result.registers.append(RegisterEntry(
            reg_name=REGISTER_NAMES.get(reg_type, f'Reg{reg_type}'),
            reg_type=reg_type,
            value=value
        ))

    return result


@omf_record(0x72, 0x84)
def handle_redata_pedata(omf, record):
    """Handle REDATA (72H) / PEDATA (84H)."""
    sub = omf.make_parser(record)

    if record.type == 0x72:
        rec_type = "REDATA"
        seg_idx = sub.parse_index()
        offset = sub.parse_numeric(2)

        result = ParsedReDataPeData(
            record_type=rec_type,
            segment=omf.get_segdef(seg_idx),
            segment_index=seg_idx,
            offset=offset
        )
    else:
        rec_type = "PEDATA"
        frame = sub.parse_numeric(2)
        offset = sub.parse_numeric(2)

        result = ParsedReDataPeData(
            record_type=rec_type,
            frame=frame,
            offset=offset,
            physical_address=(frame << 4) + offset
        )

    data_len = sub.bytes_remaining()
    result.data_length = data_len

    if data_len > 0:
        result.data_preview = sub.data[sub.offset:sub.offset + min(16, data_len)]

    return result


@omf_record(0x74, 0x86)
def handle_ridata_pidata(omf, record):
    """Handle RIDATA (74H) / PIDATA (86H)."""
    sub = omf.make_parser(record)

    if record.type == 0x74:
        rec_type = "RIDATA"
        seg_idx = sub.parse_index()
        offset = sub.parse_numeric(2)

        result = ParsedRiDataPiData(
            record_type=rec_type,
            segment=omf.get_segdef(seg_idx),
            segment_index=seg_idx,
            offset=offset
        )
    else:
        rec_type = "PIDATA"
        frame = sub.parse_numeric(2)
        offset = sub.parse_numeric(2)

        result = ParsedRiDataPiData(
            record_type=rec_type,
            frame=frame,
            offset=offset,
            physical_address=(frame << 4) + offset
        )

    result.remaining_bytes = sub.bytes_remaining()

    return result


@omf_record(0x76)
def handle_ovldef(omf, record):
    """Handle OVLDEF (76H) - Overlay Definition."""
    sub = omf.make_parser(record)
    name = sub.parse_name()

    result = ParsedOvlDef(overlay_name=name)

    if sub.bytes_remaining() >= 2:
        result.attribute = sub.parse_numeric(2)

    if sub.bytes_remaining() >= 4:
        result.file_location = sub.parse_numeric(4)

    if sub.bytes_remaining() > 0:
        result.additional_data = sub.data[sub.offset:]

    return result


@omf_record(0x78)
def handle_endrec(omf, record):
    """Handle ENDREC (78H) - End Record."""
    return ParsedEndRec()


@omf_record(0x7A)
def handle_blkdef(omf, record):
    """Handle BLKDEF (7AH) - Block Definition."""
    sub = omf.make_parser(record)

    base_grp = sub.parse_index()
    base_seg = sub.parse_index()

    result = ParsedBlkDef(
        base_group=omf.get_grpdef(base_grp),
        base_segment=omf.get_segdef(base_seg)
    )

    if base_seg == 0:
        result.frame = sub.parse_numeric(2)

    result.block_name = sub.parse_name()
    result.offset = sub.parse_numeric(2)

    if sub.bytes_remaining() > 0:
        result.debug_length = sub.parse_numeric(2)
        if result.debug_length > 0 and sub.bytes_remaining() > 0:
            result.debug_data = sub.read_bytes(min(result.debug_length, sub.bytes_remaining()))

    return result


@omf_record(0x7C)
def handle_blkend(omf, record):
    """Handle BLKEND (7CH) - Block End."""
    return ParsedBlkEnd()


@omf_record(0x7E)
def handle_debsym(omf, record):
    """Handle DEBSYM (7EH) - Debug Symbols."""
    sub = omf.make_parser(record)

    result = ParsedDebSym()

    if sub.bytes_remaining() > 0:
        result.data = sub.data[sub.offset:]

    return result


@omf_record(0xA4)
def handle_libhed_obsolete(omf, record):
    """Handle LIBHED (A4H) - Obsolete Intel Library Header."""
    sub = omf.make_parser(record)

    result = ParsedObsoleteLib(record_type="LIBHED")

    if sub.bytes_remaining() > 0:
        result.data = sub.data[sub.offset:]

    return result


@omf_record(0xA6)
def handle_libnam_obsolete(omf, record):
    """Handle LIBNAM (A6H) - Obsolete Intel Library Names."""
    sub = omf.make_parser(record)

    result = ParsedObsoleteLib(record_type="LIBNAM")

    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        if name:
            result.modules.append(name)

    return result


@omf_record(0xA8)
def handle_libloc_obsolete(omf, record):
    """Handle LIBLOC (A8H) - Obsolete Intel Library Locations."""
    sub = omf.make_parser(record)

    result = ParsedObsoleteLib(record_type="LIBLOC")

    count = 0
    while sub.bytes_remaining() >= 4:
        location = sub.parse_numeric(4)
        result.locations.append({
            'module': count,
            'offset': location
        })
        count += 1

    return result


@omf_record(0xAA)
def handle_libdic_obsolete(omf, record):
    """Handle LIBDIC (AAH) - Obsolete Intel Library Dictionary."""
    sub = omf.make_parser(record)

    result = ParsedObsoleteLib(record_type="LIBDIC")

    if sub.bytes_remaining() > 0:
        result.data = sub.data[sub.offset:]

    return result
