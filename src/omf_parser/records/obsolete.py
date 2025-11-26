"""Obsolete Intel 8086 record handlers."""

from . import omf_record
from ..constants import OMFVariant, RegisterType
from ..models import (
    ParsedRheadr, ParsedRegInt, ParsedReDataPeData, ParsedRiDataPiData,
    ParsedOvlDef, ParsedEndRec, ParsedBlkDef, ParsedBlkEnd,
    ParsedDebSym, ParsedObsoleteLib, RegisterEntry, LibLocEntry
)
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


@omf_record(0x6E)
def handle_rheadr(omf: OMFFileProtocol, record: RecordInfo) -> ParsedRheadr:
    """Handle RHEADR (6EH) - R-Module Header."""
    sub = omf.make_parser(record)
    name = sub.parse_name()

    result = ParsedRheadr(name=name if name else None)

    if sub.bytes_remaining() > 0:
        result.attributes = sub.data[sub.offset:]

    return result


@omf_record(0x70)
def handle_regint(omf: OMFFileProtocol, record: RecordInfo) -> ParsedRegInt:
    """Handle REGINT (70H) - Register Initialization."""
    sub = omf.make_parser(record)

    result = ParsedRegInt()

    while sub.bytes_remaining() >= 3:
        reg_type_byte = sub.read_byte()
        if reg_type_byte is None:
            # Per TIS OMF 1.1: Record Length declares expected size.
            # Missing data indicates malformed record.
            result.warnings.append("Truncated REGINT record")
            break
        reg_type = RegisterType.from_raw(reg_type_byte, omf.variant.omf_variant)
        value = sub.parse_numeric(2)
        result.registers.append(RegisterEntry(
            reg_type=reg_type,
            value=value
        ))

    return result


@omf_record(0x72, 0x84)
def handle_redata_pedata(omf: OMFFileProtocol, record: RecordInfo) -> ParsedReDataPeData:
    """Handle REDATA (72H) / PEDATA (84H)."""
    sub = omf.make_parser(record)

    result: ParsedReDataPeData
    if record.type == 0x72:
        seg_idx = sub.parse_index()
        offset = sub.parse_numeric(2)

        result = ParsedReDataPeData(
            record_type="REDATA",
            segment=omf.get_segdef(seg_idx),
            segment_index=seg_idx,
            offset=offset
        )
    else:
        frame = sub.parse_numeric(2)
        offset = sub.parse_numeric(2)

        result = ParsedReDataPeData(
            record_type="PEDATA",
            frame=frame,
            offset=offset,
            physical_address=(frame << 4) + offset
        )

    data_len = sub.bytes_remaining()
    result.data_length = data_len

    if data_len > 0:
        result.data_preview = sub.data[sub.offset:sub.offset + min(16, data_len)]

    if omf.variant.omf_variant == OMFVariant.PHARLAP:
        result.warnings.append(
            f"Obsolete 8086 record {result.record_type} in PharLap file - "
            "using 2-byte offsets (not extended by Easy OMF-386)"
        )

    return result


@omf_record(0x74, 0x86)
def handle_ridata_pidata(omf: OMFFileProtocol, record: RecordInfo) -> ParsedRiDataPiData:
    """Handle RIDATA (74H) / PIDATA (86H)."""
    sub = omf.make_parser(record)

    result: ParsedRiDataPiData
    if record.type == 0x74:
        seg_idx = sub.parse_index()
        offset = sub.parse_numeric(2)

        result = ParsedRiDataPiData(
            record_type="RIDATA",
            segment=omf.get_segdef(seg_idx),
            segment_index=seg_idx,
            offset=offset
        )
    else:
        frame = sub.parse_numeric(2)
        offset = sub.parse_numeric(2)

        result = ParsedRiDataPiData(
            record_type="PIDATA",
            frame=frame,
            offset=offset,
            physical_address=(frame << 4) + offset
        )

    result.remaining_bytes = sub.bytes_remaining()

    if omf.variant.omf_variant == OMFVariant.PHARLAP:
        result.warnings.append(
            f"Obsolete 8086 record {result.record_type} in PharLap file - "
            "using 2-byte offsets (not extended by Easy OMF-386)"
        )

    return result


@omf_record(0x76)
def handle_ovldef(omf: OMFFileProtocol, record: RecordInfo) -> ParsedOvlDef:
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
def handle_endrec(omf: OMFFileProtocol, record: RecordInfo) -> ParsedEndRec:
    """Handle ENDREC (78H) - End Record."""
    return ParsedEndRec()


@omf_record(0x7A)
def handle_blkdef(omf: OMFFileProtocol, record: RecordInfo) -> ParsedBlkDef:
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
    offset_size = sub.get_offset_field_size(False)  # Per TIS OMF 1.1 (PharLap extends via variant)
    result.offset = sub.parse_numeric(offset_size)

    if sub.bytes_remaining() > 0:
        result.debug_length = sub.parse_numeric(2)
        if result.debug_length > 0 and sub.bytes_remaining() > 0:
            result.debug_data = sub.read_bytes(min(result.debug_length, sub.bytes_remaining()))

    return result


@omf_record(0x7C)
def handle_blkend(omf: OMFFileProtocol, record: RecordInfo) -> ParsedBlkEnd:
    """Handle BLKEND (7CH) - Block End."""
    return ParsedBlkEnd()


@omf_record(0x7E)
def handle_debsym(omf: OMFFileProtocol, record: RecordInfo) -> ParsedDebSym:
    """Handle DEBSYM (7EH) - Debug Symbols."""
    sub = omf.make_parser(record)

    result = ParsedDebSym()

    if sub.bytes_remaining() > 0:
        result.data = sub.data[sub.offset:]

    return result


@omf_record(0xA4)
def handle_libhed_obsolete(omf: OMFFileProtocol, record: RecordInfo) -> ParsedObsoleteLib:
    """Handle LIBHED (A4H) - Obsolete Intel Library Header."""
    sub = omf.make_parser(record)

    result = ParsedObsoleteLib(record_type="LIBHED")

    if sub.bytes_remaining() > 0:
        result.data = sub.data[sub.offset:]

    return result


@omf_record(0xA6)
def handle_libnam_obsolete(omf: OMFFileProtocol, record: RecordInfo) -> ParsedObsoleteLib:
    """Handle LIBNAM (A6H) - Obsolete Intel Library Names."""
    sub = omf.make_parser(record)

    result = ParsedObsoleteLib(record_type="LIBNAM")

    while sub.bytes_remaining() > 0:
        name = sub.parse_name()
        if name:
            result.modules.append(name)

    return result


@omf_record(0xA8)
def handle_libloc_obsolete(omf: OMFFileProtocol, record: RecordInfo) -> ParsedObsoleteLib:
    """Handle LIBLOC (A8H) - Obsolete Intel Library Locations."""
    sub = omf.make_parser(record)

    result = ParsedObsoleteLib(record_type="LIBLOC")

    count = 0
    while sub.bytes_remaining() >= 4:
        location = sub.parse_numeric(4)
        result.locations.append(LibLocEntry(
            module=f"Module#{count}",
            block_num=location // 512,
            byte_offset=location % 512
        ))
        count += 1

    return result


@omf_record(0xAA)
def handle_libdic_obsolete(omf: OMFFileProtocol, record: RecordInfo) -> ParsedObsoleteLib:
    """Handle LIBDIC (AAH) - Obsolete Intel Library Dictionary."""
    sub = omf.make_parser(record)

    result = ParsedObsoleteLib(record_type="LIBDIC")

    if sub.bytes_remaining() > 0:
        result.data = sub.data[sub.offset:]

    return result
