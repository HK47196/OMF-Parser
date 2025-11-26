"""Output formatters for parsed OMF data."""

from enum import Enum
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .file import OMFFile
    from .models import ParsedComentContent

from .models import (
    ParseResult, ParsedRecord, ParsedOMFFile,
    ParsedTheadr, ParsedLNames, ParsedSegDef, ParsedGrpDef,
    ParsedPubDef, ParsedExtDef, ParsedCExtDef, ParsedModEnd,
    ParsedLinNum, ParsedVerNum, ParsedVendExt, ParsedLocSym, ParsedTypDef,
    ParsedLEData, ParsedLIData, ParsedLIDataBlock,
    ParsedFixupp, ParsedThread, ParsedFixup,
    ParsedComDef, ParsedComDat, ParsedBackpatch, ParsedNamedBackpatch,
    ParsedLinSym, ParsedAlias,
    ParsedLibHdr, ParsedLibEnd, ParsedLibDict, ParsedExtDict,
    ParsedRheadr, ParsedRegInt, ParsedReDataPeData, ParsedRiDataPiData,
    ParsedOvlDef, ParsedEndRec, ParsedBlkDef, ParsedBlkEnd,
    ParsedDebSym, ParsedObsoleteLib,
    ParsedComent
)
from .parsing import format_hex_with_ascii


def _bytes_to_hex(data: bytes | None) -> str | None:
    """Convert bytes to hex string with ASCII preview."""
    if data is None:
        return None
    return format_hex_with_ascii(data)


class HumanFormatter:
    """Format parsed OMF data as human-readable text."""

    def format_file_header(self, omf: "OMFFile") -> str:
        """Format file header information."""
        lines = [
            "=" * 60,
            f"OMF Analysis: {omf.filepath}",
            "=" * 60,
            f"File Size: {len(omf.data) if omf.data else 0} bytes"
        ]

        if omf.is_library:
            lines.append("File Type: OMF Library (.LIB)")
        else:
            lines.append("File Type: OMF Object Module (.OBJ)")

        if omf.mixed_variants:
            lines.append(f"Variants: {', '.join(sorted(omf.seen_variants))} (mixed)")
        else:
            lines.append(f"Variant: {omf.variant.name}")
        if omf.features:
            lines.append(f"Features: {', '.join(sorted(omf.features))}")
        lines.append("")

        return "\n".join(lines)

    def format_record_header(self, result: ParseResult) -> str:
        """Format a record header line."""
        if result.checksum is not None:
            if result.checksum == 0:
                status = "Skipped (0)"
            elif result.checksum_valid:
                status = "Valid"
            else:
                status = "Invalid"
            return f"[{result.offset:06X}] {result.record_name:<14} Len={result.length:<5} Chk={result.checksum:02X} ({status})"
        else:
            return f"[{result.offset:06X}] {result.record_name:<14} Len={result.length}"

    def format_result(self, result: ParseResult) -> str:
        """Format a single parse result."""
        lines = [self.format_record_header(result)]

        if result.error:
            lines.append(f"  [!] Error: {result.error}")
            if result.raw_content:
                preview = result.raw_content[:32]
                lines.append(f"      Raw: {_bytes_to_hex(preview)}")
        elif result.parsed:
            content = self.format_parsed(result.parsed)
            if content:
                lines.append(content)

        return "\n".join(lines)

    def format_parsed(self, parsed: ParsedRecord) -> str:
        """Format a parsed record."""
        if parsed is None:
            return ""

        formatter_method = f"_format_{type(parsed).__name__}"
        if hasattr(self, formatter_method):
            result: str = getattr(self, formatter_method)(parsed)
            return result

        return f"  {type(parsed).__name__}: (no formatter)"

    def _format_ParsedTheadr(self, p: ParsedTheadr) -> str:
        return f"  {p.record_name} Module: '{p.module_name}'"

    def _format_ParsedLNames(self, p: ParsedLNames) -> str:
        lines = [f"  {p.record_name}: Added indices {p.start_index} to {p.end_index}"]
        for idx, name, is_reserved in p.names:
            marker = " [RESERVED]" if is_reserved else ""
            lines.append(f"    [{idx}] '{name}'{marker}")
        return "\n".join(lines)

    def _format_ParsedSegDef(self, p: ParsedSegDef) -> str:
        lines = [
            f"  ACBP: 0x{p.acbp:02X}",
            f"    Alignment: {p.alignment.label}",
            f"    Combine: {p.combine.label}",
            f"    Big: {p.big} (segment is {'64K/4GB' if p.big else 'smaller'})",
            f"    Use32: {p.use32} ({'Use32' if p.use32 else 'Use16'})"
        ]

        if p.absolute_frame is not None:
            lines.append(f"    Absolute Frame: 0x{p.absolute_frame:04X}, Offset: 0x{p.absolute_offset:02X}")

        lines.append(f"    Length: {p.length} (0x{p.length:X})")
        lines.append(f"    Segment Name: {p.segment_name}")
        lines.append(f"    Class Name: {p.class_name}")
        lines.append(f"    Overlay Name: {p.overlay_name}")

        if p.access_byte is not None:
            lines.append(f"    Access: 0x{p.access_byte:02X} ({p.access})")

        return "\n".join(lines)

    def _format_ParsedGrpDef(self, p: ParsedGrpDef) -> str:
        lines = [f"  Group Name: {p.name}"]
        if p.is_flat:
            lines.append("    [Special] FLAT pseudo-group - Virtual Zero Address")
        for comp in p.components:
            lines.append(f"    Component: {comp}")
        for warn in p.warnings:
            lines.append(f"    [!] WARNING: {warn}")
        return "\n".join(lines)

    def _format_ParsedPubDef(self, p: ParsedPubDef) -> str:
        local = "Local " if p.is_local else ""
        bits = "32-bit" if p.is_32bit else "16-bit"
        lines = [
            f"  {local}Public Definitions ({bits}):",
            f"    Base Group: {p.base_group}",
            f"    Base Segment: {p.base_segment}"
        ]
        if p.absolute_frame is not None:
            lines.append(f"    Absolute Frame: 0x{p.absolute_frame:04X}")
        if p.frame_note:
            lines.append(f"    [Note] {p.frame_note}")
        for sym in p.symbols:
            lines.append(f"    Symbol: '{sym.name}' Offset=0x{sym.offset:X} Type={sym.type_index}")
        return "\n".join(lines)

    def _format_ParsedExtDef(self, p: ParsedExtDef) -> str:
        local = "Local " if p.is_local else ""
        lines = [f"  {local}External Definitions:"]
        for ext in p.externals:
            lines.append(f"    [{ext.index}] '{ext.name}' Type={ext.type_index}")
        return "\n".join(lines)

    def _format_ParsedCExtDef(self, p: ParsedCExtDef) -> str:
        lines = ["  COMDAT External Definitions:"]
        for ext in p.externals:
            lines.append(f"    [{ext.index}] {ext.name} Type={ext.type_index}")
        return "\n".join(lines)

    def _format_ParsedModEnd(self, p: ParsedModEnd) -> str:
        lines = [
            f"  Module Type: 0x{p.mod_type:02X}",
            f"    Main Module: {p.is_main}",
            f"    Has Start Address: {p.has_start}",
            f"    Relocatable Start: {p.is_relocatable}"
        ]
        for warn in p.warnings:
            lines.append(f"    [!] WARNING: {warn}")
        if p.start_address:
            lines.append("  Start Address:")
            sa = p.start_address
            if sa.frame_datum is not None:
                lines.append(f"    Frame Method: {sa.frame_method}, Datum: {sa.frame_datum}")
            else:
                lines.append(f"    Frame Method: {sa.frame_method}")
            lines.append(f"    Target Method: {sa.target_method}, Datum: {sa.target_datum}")
            if sa.target_displacement is not None:
                lines.append(f"    Target Displacement: 0x{sa.target_displacement:X}")
        return "\n".join(lines)

    def _format_ParsedLinNum(self, p: ParsedLinNum) -> str:
        lines = [
            f"  Base Group: {p.base_group}",
            f"  Base Segment: {p.base_segment}",
            "  Line Number Entries:"
        ]
        for entry in p.entries:
            if entry.is_end_of_function:
                lines.append(f"    Line 0 (end of function): Offset=0x{entry.offset:X}")
            else:
                lines.append(f"    Line {entry.line}: Offset=0x{entry.offset:X}")
        return "\n".join(lines)

    def _format_ParsedVerNum(self, p: ParsedVerNum) -> str:
        lines = [f"  OMF Version: {p.version}"]
        if p.tis_base:
            lines.append(f"    TIS Base Version: {p.tis_base}")
            lines.append(f"    Vendor Number: {p.vendor_num}")
            lines.append(f"    Vendor Version: {p.vendor_ver}")
        for warn in p.warnings:
            lines.append(f"    [!] WARNING: {warn}")
        return "\n".join(lines)

    def _format_ParsedVendExt(self, p: ParsedVendExt) -> str:
        lines = []
        if p.vendor_name:
            lines.append(f"  Vendor Number: {p.vendor_num} ({p.vendor_name})")
        else:
            lines.append(f"  Vendor Number: {p.vendor_num}")
        for warn in p.warnings:
            lines.append(f"  [!] WARNING: {warn}")
        if p.extension_data:
            lines.append(f"  Extension Data: {_bytes_to_hex(p.extension_data)}")
        return "\n".join(lines)

    def _format_ParsedLocSym(self, p: ParsedLocSym) -> str:
        lines = [
            "  [Obsolete] Local Symbols (same format as PUBDEF)",
            f"    Base Group: {p.base_group}",
            f"    Base Segment: {p.base_segment}"
        ]
        if p.absolute_frame is not None:
            lines.append(f"    Absolute Frame: 0x{p.absolute_frame:04X}")
        if p.frame_note:
            lines.append(f"    [Note] {p.frame_note}")
        for sym in p.symbols:
            lines.append(f"    '{sym.name}' Offset=0x{sym.offset:X} Type={sym.type_index}")
        return "\n".join(lines)

    def _format_ParsedTypDef(self, p: ParsedTypDef) -> str:
        lines = ["  [Obsolete TYPDEF]"]
        if p.name:
            lines.append(f"  Name (ignored): '{p.name}'")
        lines.append(f"  EN Byte: {p.en_byte}")
        lines.append(f"  Format: {p.format}")

        for leaf in p.leaves:
            if hasattr(leaf, 'leaf_index') and leaf.leaf_index is not None:
                lines.append(f"  Leaf {leaf.leaf_index}:")
                indent = "    "
            else:
                indent = "  "

            if leaf.type == 'NEAR':
                lines.append(f"{indent}NEAR Variable")
                lines.append(f"{indent}  Type: {leaf.var_type}")
                lines.append(f"{indent}  Size: {leaf.size_bits} bits ({leaf.size_bytes} bytes)")
            elif leaf.type == 'FAR':
                lines.append(f"{indent}FAR Variable (Array)")
                lines.append(f"{indent}  Num Elements: {leaf.num_elements}")
                lines.append(f"{indent}  Element Type: {leaf.element_type}")
            else:
                lines.append(f"{indent}Unknown Leaf Type: 0x{leaf.leaf_type:02X}")
                if hasattr(leaf, 'remaining') and leaf.remaining:
                    lines.append(f"{indent}  Remaining: {_bytes_to_hex(leaf.remaining)}")

        return "\n".join(lines)

    def _format_ParsedLEData(self, p: ParsedLEData) -> str:
        lines = [
            f"  Segment: {p.segment}",
            f"  Offset: 0x{p.offset:X}",
            f"  Data Length: {p.data_length} bytes"
        ]
        if p.data_preview:
            lines.append(f"  Data Preview: {_bytes_to_hex(p.data_preview)}")
        return "\n".join(lines)

    def _format_ParsedLIData(self, p: ParsedLIData) -> str:
        lines = [
            f"  Segment: {p.segment}",
            f"  Offset: 0x{p.offset:X}",
            f"  Total Expanded Size: {p.total_expanded_size} bytes",
            "  Iterated Data Blocks:"
        ]

        def format_block(block: ParsedLIDataBlock, indent: int) -> None:
            prefix = " " * indent
            if block.block_count == 0:
                content_str = _bytes_to_hex(block.content) if block.content else "(empty)"
                size_str = f" -> {block.expanded_size} bytes" if block.expanded_size > 0 else ""
                lines.append(f"{prefix}Repeat {block.repeat_count}x: {content_str}{size_str}")
            else:
                size_str = f" -> {block.expanded_size} bytes" if block.expanded_size > 0 else ""
                lines.append(f"{prefix}Repeat {block.repeat_count}x ({block.block_count} nested blocks):{size_str}")
                for nested in block.nested_blocks:
                    format_block(nested, indent + 2)

        for block in p.blocks:
            format_block(block, 4)

        for warn in p.warnings:
            lines.append(f"  [!] WARNING: {warn}")

        return "\n".join(lines)

    def _format_ParsedFixupp(self, p: ParsedFixupp) -> str:
        lines = ["  Fixup Subrecords:"]
        for sub in p.subrecords:
            if isinstance(sub, ParsedThread):
                kind_str = sub.kind.value if isinstance(sub.kind, Enum) else sub.kind
                out = f"    THREAD {kind_str}#{sub.thread_num} Method={sub.method.label}"
                if sub.index is not None:
                    label = "FrameNum" if sub.method.int_val == 3 else "Index"
                    out += f" {label}={sub.index}"
                lines.append(out)
                for warn in sub.warnings:
                    lines.append(f"    [!] WARNING: {warn}")
            elif isinstance(sub, ParsedFixup):
                lines.append(f"    FIXUP @{sub.data_offset:03X}")
                mode_str = sub.mode.value if isinstance(sub.mode, Enum) else sub.mode
                lines.append(f"      Location: {sub.location.label}, Mode: {mode_str}")
                frame_line = f"      Frame: Method={sub.frame_method.label} ({sub.frame_source})"
                if sub.frame_datum is not None:
                    frame_line += f" Datum={sub.frame_datum}"
                lines.append(frame_line)
                target_line = f"      Target: Method={sub.target_method.label} ({sub.target_source})"
                if sub.target_datum is not None:
                    target_line += f" Datum={sub.target_datum}"
                lines.append(target_line)
                if sub.displacement is not None:
                    lines.append(f"      Displacement: 0x{sub.displacement:X}")
        return "\n".join(lines)

    def _format_ParsedComDef(self, p: ParsedComDef) -> str:
        local = "Local " if p.is_local else ""
        lines = [f"  {local}Communal Definitions:"]
        for defn in p.definitions:
            if defn.kind == 'FAR':
                lines.append(f"    '{defn.name}' FAR: {defn.num_elements} x {defn.element_size} = {defn.total_size} bytes")
            elif defn.kind == 'NEAR':
                lines.append(f"    '{defn.name}' NEAR: {defn.size} bytes")
            elif defn.kind == 'Borland':
                lines.append(f"    '{defn.name}' Borland SegIdx={defn.seg_index}: {defn.length} bytes")
            else:
                lines.append(f"    '{defn.name}' DataType=0x{defn.data_type:02X}: {getattr(defn, 'length', '?')} bytes")
        return "\n".join(lines)

    def _format_ParsedComDat(self, p: ParsedComDat) -> str:
        lines = [
            f"  Flags: 0x{p.flags:02X}",
            f"    Continuation: {p.continuation}",
            f"    Iterated Data: {p.iterated}",
            f"    Local (LCOMDAT): {p.local}",
            f"    Data in Code Seg: {p.data_in_code}",
            f"  Selection: {p.selection.label}",
            f"  Allocation: {p.allocation.label}",
            f"  Alignment: {p.alignment.label}",
            f"  Enum Offset: 0x{p.enum_offset:X}",
            f"  Type Index: {p.type_index}"
        ]
        if p.base_group is not None:
            lines.append(f"  Base Group: {p.base_group}")
            lines.append(f"  Base Segment: {p.base_segment}")
        if p.absolute_frame is not None:
            lines.append(f"  Absolute Frame: 0x{p.absolute_frame:04X}")
        lines.append(f"  Symbol: '{p.symbol}'")
        lines.append(f"  Data Length: {p.data_length} bytes")

        if p.iterated and p.iterated_blocks:
            lines.append(f"  Iterated Expanded Size: {p.iterated_expanded_size} bytes")
            lines.append("  Iterated Data Blocks:")

            def format_block(block: ParsedLIDataBlock, indent: int) -> None:
                prefix = " " * indent
                if block.block_count == 0:
                    content_str = _bytes_to_hex(block.content) if block.content else "(empty)"
                    size_str = f" -> {block.expanded_size} bytes" if block.expanded_size > 0 else ""
                    lines.append(f"{prefix}Repeat {block.repeat_count}x: {content_str}{size_str}")
                else:
                    size_str = f" -> {block.expanded_size} bytes" if block.expanded_size > 0 else ""
                    lines.append(f"{prefix}Repeat {block.repeat_count}x ({block.block_count} nested blocks):{size_str}")
                    for nested in block.nested_blocks:
                        format_block(nested, indent + 2)

            for block in p.iterated_blocks:
                format_block(block, 4)

        return "\n".join(lines)

    def _format_ParsedBackpatch(self, p: ParsedBackpatch) -> str:
        lines = ["  Backpatch Records:"]
        for warn in p.warnings:
            lines.append(f"    [!] Warning: {warn}")
        for rec in p.records:
            lines.append(f"    Segment: {rec.segment}")
            lines.append(f"    Location Type: {rec.location.label}")
            lines.append(f"    Offset: 0x{rec.offset:X}")
            lines.append(f"    Value: 0x{rec.value:X}")
        return "\n".join(lines)

    def _format_ParsedNamedBackpatch(self, p: ParsedNamedBackpatch) -> str:
        lines = ["  Named Backpatch Records:"]
        for rec in p.records:
            lines.append(f"    Symbol: '{rec.symbol}'")
            lines.append(f"    Location Type: {rec.location.label}")
            lines.append(f"    Offset: 0x{rec.offset:X}")
            lines.append(f"    Value: 0x{rec.value:X}")
        return "\n".join(lines)

    def _format_ParsedLinSym(self, p: ParsedLinSym) -> str:
        lines = [
            f"  Flags: Continuation={p.continuation}",
            f"  Symbol: '{p.symbol}'",
            "  Line Number Entries:"
        ]
        for entry in p.entries:
            if entry.is_end_of_function:
                lines.append(f"    Line 0 (end of function): Offset=0x{entry.offset:X}")
            else:
                lines.append(f"    Line {entry.line}: Offset=0x{entry.offset:X}")
        return "\n".join(lines)

    def _format_ParsedAlias(self, p: ParsedAlias) -> str:
        lines = ["  Alias Definitions:"]
        for alias in p.aliases:
            lines.append(f"    '{alias.alias}' -> '{alias.substitute}'")
        return "\n".join(lines)

    def _format_ParsedLibHdr(self, p: ParsedLibHdr) -> str:
        lines = [
            f"  Page Size: {p.page_size} bytes",
            f"  Dictionary Offset: 0x{p.dict_offset:08X}",
            f"  Dictionary Blocks: {p.dict_blocks}",
            f"  Flags: 0x{p.flags:02X}" + (" [Case Sensitive]" if p.case_sensitive else "")
        ]
        return "\n".join(lines)

    def _format_ParsedLibEnd(self, p: ParsedLibEnd) -> str:
        return "  End of Library Modules."

    def _format_ParsedLibDict(self, p: ParsedLibDict) -> str:
        lines = []
        for entry in p.entries:
            lines.append(f"  [{entry.block}:{entry.bucket:02}] '{entry.symbol}' -> Page {entry.page}")
        lines.append(f"  Total Dictionary Entries: {p.total_entries}")
        return "\n".join(lines)

    def _format_ParsedExtDict(self, p: ParsedExtDict) -> str:
        lines = [
            f"  Length: {p.length} bytes",
            f"  Number of Modules: {p.num_modules}"
        ]
        for mod in p.modules:
            lines.append(f"    Module {mod.index}: Page={mod.page}, DepOffset={mod.dep_offset}")
        return "\n".join(lines)

    def _format_ParsedRheadr(self, p: ParsedRheadr) -> str:
        lines = [
            "  [Obsolete] R-Module Header",
            "    Identifies a module processed by LINK-86/LOCATE-86"
        ]
        if p.name:
            lines.append(f"    Name: {p.name}")
        if p.attributes:
            lines.append(f"    Attributes: {_bytes_to_hex(p.attributes)}")
        return "\n".join(lines)

    def _format_ParsedRegInt(self, p: ParsedRegInt) -> str:
        lines = [
            "  [Obsolete] Register Initialization",
            "    Provides initial values for 8086 registers"
        ]
        for reg in p.registers:
            lines.append(f"    {reg.reg_name}: 0x{reg.value:04X}")
        return "\n".join(lines)

    def _format_ParsedReDataPeData(self, p: ParsedReDataPeData) -> str:
        lines = [f"  [Obsolete] {p.record_type} {'(Relocatable)' if p.record_type == 'REDATA' else '(Physical)'} Enumerated Data"]
        if p.segment:
            lines.append(f"    Segment: {p.segment}")
        if p.frame is not None:
            lines.append(f"    Frame Number: 0x{p.frame:04X}")
        lines.append(f"    Offset: 0x{p.offset:04X}")
        if p.physical_address is not None:
            lines.append(f"    Physical Address: 0x{p.physical_address:06X}")
        lines.append(f"    Data Length: {p.data_length} bytes")
        if p.data_preview:
            lines.append(f"    Data Preview: {_bytes_to_hex(p.data_preview)}")
        return "\n".join(lines)

    def _format_ParsedRiDataPiData(self, p: ParsedRiDataPiData) -> str:
        lines = [f"  [Obsolete] {p.record_type} {'(Relocatable)' if p.record_type == 'RIDATA' else '(Physical)'} Iterated Data"]
        if p.segment:
            lines.append(f"    Segment: {p.segment}")
        if p.frame is not None:
            lines.append(f"    Frame Number: 0x{p.frame:04X}")
        lines.append(f"    Offset: 0x{p.offset:04X}")
        if p.physical_address is not None:
            lines.append(f"    Physical Address: 0x{p.physical_address:06X}")
        lines.append("    (Iterated data follows)")
        if p.remaining_bytes > 0:
            lines.append(f"    Remaining Data: {p.remaining_bytes} bytes")
        return "\n".join(lines)

    def _format_ParsedOvlDef(self, p: ParsedOvlDef) -> str:
        lines = [
            "  [Obsolete] Overlay Definition",
            f"    Overlay Name: '{p.overlay_name}'"
        ]
        if p.attribute is not None:
            lines.append(f"    Overlay Attribute: 0x{p.attribute:04X}")
        if p.file_location is not None:
            lines.append(f"    File Location: 0x{p.file_location:08X}")
        if p.additional_data:
            lines.append(f"    Additional Data: {_bytes_to_hex(p.additional_data)}")
        return "\n".join(lines)

    def _format_ParsedEndRec(self, p: ParsedEndRec) -> str:
        return "  [Obsolete] End Record\n    Denotes end of a set of records (block or overlay)"

    def _format_ParsedBlkDef(self, p: ParsedBlkDef) -> str:
        lines = [
            "  [Obsolete] Block Definition",
            "    Debug info for procedure/block scope",
            f"    Base Group: {p.base_group}",
            f"    Base Segment: {p.base_segment}"
        ]
        if p.frame is not None:
            lines.append(f"    Frame Number: 0x{p.frame:04X}")
        lines.append(f"    Block Name: '{p.block_name}'")
        lines.append(f"    Offset: 0x{p.offset:04X}")
        if p.debug_length is not None:
            lines.append(f"    Debug Info Length: {p.debug_length} bytes")
            if p.debug_data:
                lines.append(f"    Debug Data: {_bytes_to_hex(p.debug_data)}")
        return "\n".join(lines)

    def _format_ParsedBlkEnd(self, p: ParsedBlkEnd) -> str:
        return "  [Obsolete] Block End\n    Closes a BLKDEF scope"

    def _format_ParsedDebSym(self, p: ParsedDebSym) -> str:
        lines = [
            "  [Obsolete] Debug Symbols",
            "    Local symbols including stack and based symbols"
        ]
        if p.data:
            lines.append(f"    Data: {_bytes_to_hex(p.data)}")
        return "\n".join(lines)

    def _format_ParsedObsoleteLib(self, p: ParsedObsoleteLib) -> str:
        type_descs = {
            "LIBHED": "[Obsolete Intel] Library Header\n    Note: Conflicts with MS EXESTR comment class",
            "LIBNAM": "[Obsolete Intel] Library Module Names\n    Lists module names in sequence of appearance",
            "LIBLOC": "[Obsolete Intel] Library Module Locations",
            "LIBDIC": "[Obsolete Intel] Library Dictionary\n    Public symbols grouped by defining module"
        }
        lines = [f"  {type_descs.get(p.record_type, p.record_type)}"]
        for mod in p.modules:
            lines.append(f"    Module: {mod}")
        for loc in p.locations:
            lines.append(f"    {loc.module}: Block {loc.block_num}, Offset {loc.byte_offset}")
        if p.data:
            lines.append(f"    Data: {_bytes_to_hex(p.data)}")
        return "\n".join(lines)

    def _format_ParsedComent(self, p: ParsedComent) -> str:
        lines = [
            f"  Comment Class: {p.class_name} (0x{p.comment_class:02X})",
            f"  Flags: NoPurge={int(p.no_purge)}, NoList={int(p.no_list)}"
        ]
        for warn in p.warnings:
            lines.append(f"  [!] WARNING: {warn}")
        if p.content:
            content_lines = self._format_coment_content(p.content)
            if content_lines:
                lines.append(content_lines)
        elif p.raw_data:
            lines.append(f"  Data: {_bytes_to_hex(p.raw_data)}")
        return "\n".join(lines)

    def _format_coment_content(self, content: Any) -> str:
        """Format COMENT content objects."""
        name = type(content).__name__

        simple_attrs = {
            'ComentTranslator': ('Translator', 'translator'),
            'ComentCopyright': ('Copyright', 'copyright'),
            'ComentLibSpec': ('Library', 'library'),
            'ComentLibMod': ('Library Module', 'module_name'),
            'ComentExeStr': ('Exe String', 'exe_string'),
            'ComentDefaultLibrary': ('Default Library', 'library'),
            'ComentComment': ('Comment', 'comment'),
            'ComentCompiler': ('Compiler', 'compiler'),
            'ComentDate': ('Date', 'date'),
            'ComentTimestamp': ('Timestamp', 'timestamp'),
            'ComentUser': ('User', 'user'),
            'ComentDependencyFile': ('Dependency', 'dependency'),
            'ComentCmdLine': ('Command Line', 'cmdline'),
        }

        if name in simple_attrs:
            label, attr = simple_attrs[name]
            return f"  {label}: {getattr(content, attr)}"

        if name in ['ComentDosseg', 'ComentIncErr', 'ComentNoPad',
                    'A0ProtectedMemory', 'A0BigEndian', 'A0PreComp']:
            messages = {
                'ComentDosseg': "  DOSSEG: Use DOS segment ordering convention",
                'ComentIncErr': "  Incremental Compilation Error - forces full recompile",
                'ComentNoPad': "  NOPAD: Do not pad segments",
                'A0ProtectedMemory': "    DLL uses protected memory (_loadds)",
                'A0BigEndian': "    Target is big-endian architecture",
                'A0PreComp': "    $$TYPES should use sstPreComp instead of sstTypes"
            }
            return messages.get(name, "")

        if name == 'ComentDosVersion':
            if content.major is not None:
                return f"  [Obsolete] MS-DOS Version\n    Version: {content.major}.{content.minor or 0}"
            return "  [Obsolete] MS-DOS Version"

        if name == 'ComentProcModel':
            lines = [
                f"  Processor: {content.processor}",
                f"  Memory Model: {content.mem_model}",
                f"  Floating Point: {content.fp_mode}",
            ]
            if content.pic:
                lines.append("  Position Independent: Yes")
            return "\n".join(lines)

        if name == 'ComentNewOmf':
            lines = ["  New OMF Extension marker"]
            if content.data:
                lines.append(f"  Data: {_bytes_to_hex(content.data)}")
            return "\n".join(lines)

        if name == 'ComentLinkPass':
            lines = ["  Link Pass Separator"]
            if content.pass_num is not None:
                lines.append(f"  Pass: {content.pass_num}")
            return "\n".join(lines)

        if name == 'ComentWkExt':
            lines = ["  Weak Extern definitions:"]
            for entry in content.entries:
                lines.append(f"    Weak Ext#{entry.weak_extdef_index} -> Default Ext#{entry.default_resolution_index}")
            return "\n".join(lines)

        if name == 'ComentLzExt':
            lines = ["  Lazy Extern definitions:"]
            for entry in content.entries:
                lines.append(f"    Lazy Ext#{entry.lazy_extdef_index} -> Default Ext#{entry.default_resolution_index}")
            return "\n".join(lines)

        if name == 'ComentEasyOmf':
            lines = ["  Easy OMF-386: 32-bit extensions enabled"]
            if content.marker:
                lines.append(f"  Marker: {content.marker}")
            for warn in content.warnings:
                lines.append(f"    [!] {warn}")
            return "\n".join(lines)

        if name == 'Coment32BitLinker':
            lines = ["  32-bit linker extension"]
            if content.data:
                lines.append(f"  Data: {_bytes_to_hex(content.data)}")
            return "\n".join(lines)

        if name == 'ComentDisasmDirective':
            lines = [f"  Subtype: '{content.subtype}' ({content.subtype_name})"]
            for warn in content.warnings:
                lines.append(f"    [!] WARNING: {warn}")
            if content.segment_index > 0:
                lines.append(f"    Segment Index: {content.segment_index}")
                if content.segment_name:
                    lines.append(f"    Segment: {content.segment_name}")
            else:
                lines.append("    Target: COMDAT")
                if content.lname_index is not None:
                    lines.append(f"    LNAME Index: {content.lname_index}")
                if content.comdat_name:
                    lines.append(f"    COMDAT Name: {content.comdat_name}")
            lines.append(f"    Data Region: 0x{content.start_offset:X} - 0x{content.end_offset:X} ({content.region_size} bytes)")
            return "\n".join(lines)

        if name == 'ComentLinkerDirective':
            lines = [f"  Directive: '{content.directive_code}' ({content.directive_name})"]
            for warn in content.warnings:
                lines.append(f"    [!] WARNING: {warn}")
            if content.content:
                ld_content = self._format_linker_directive_content(content.content)
                if ld_content:
                    lines.append(ld_content)
            return "\n".join(lines)

        if name == 'ComentOmfExtensions':
            lines = [f"  A0 Subtype: {content.subtype_name}"]
            for warn in content.warnings:
                lines.append(f"    [!] {warn}")
            if content.content:
                a0_content = self._format_a0_content(content.content)
                if a0_content:
                    lines.append(a0_content)
            return "\n".join(lines)

        return f"  {name}: (no formatter)"

    def _format_a0_content(self, content: Any) -> str:
        """Format A0 subtype content."""
        name = type(content).__name__

        if name == 'A0ImpDef':
            lines = [
                f"    Internal Name: {content.internal_name}",
                f"    Module Name: {content.module_name}"
            ]
            if content.by_ordinal and content.ordinal is not None:
                lines.append(f"    Ordinal: {content.ordinal}")
            elif content.entry_name is not None:
                lines.append(f"    Entry Name: {content.entry_name}")
            else:
                lines.append("    Entry: (same as internal)")
            return "\n".join(lines)

        if name == 'A0ExpDef':
            lines = [
                f"    Exported Name: {content.exported_name}",
                f"    Internal Name: {content.internal_name}" if content.internal_name != content.exported_name else "    Internal Name: (same as exported)",
                f"    By Ordinal: {content.by_ordinal}, Resident: {content.resident}, NoData: {content.no_data}, Parms: {content.parm_count}"
            ]
            if content.ordinal is not None:
                lines.append(f"    Export Ordinal: {content.ordinal}")
            return "\n".join(lines)

        if name == 'A0IncDef':
            return f"    EXTDEF Delta: {content.extdef_delta}\n    LINNUM Delta: {content.linnum_delta}"

        if name == 'A0LnkDir':
            lines = [f"    Bit Flags: 0x{content.bit_flags:02X}"]
            for meaning in content.flags_meanings:
                lines.append(f"      - {meaning}")
            lines.append(f"    Pseudocode Version: {content.pcode_version}")
            lines.append(f"    CodeView Version: {content.cv_version}")
            return "\n".join(lines)

        return ""

    def _format_linker_directive_content(self, content: Any) -> str:
        """Format Watcom linker directive content."""
        name = type(content).__name__

        if name == 'LinkerDirSourceLang':
            return f"    Debug Version: {content.major_version}.{content.minor_version}\n    Language: {content.language}"

        if name == 'LinkerDirDefaultLib':
            return f"    Priority: {content.priority}\n    Library: {content.library_name}"

        if name == 'LinkerDirOptFarCalls':
            lines = [f"    Segment Index: {content.segment_index}"]
            if content.segment_name:
                lines.append(f"    Segment: {content.segment_name}")
            return "\n".join(lines)

        if name == 'LinkerDirOptUnsafe':
            return "    (Marks preceding FIXUPP as unsafe for optimization)"

        if name == 'LinkerDirVFTableDef':
            lines = []
            if content.is_pure:
                lines.append("    [Pure Virtual Table]")
            lines.append(f"    VF Table External: [{content.vf_table_ext_index}] {content.vf_table_symbol or ''}")
            lines.append(f"    Default External: [{content.default_ext_index}] {content.default_symbol or ''}")
            if content.function_names:
                lines.append("    Virtual Functions:")
                for idx, fname in zip(content.lname_indices, content.function_names):
                    lines.append(f"      [{idx}] {fname}")
            return "\n".join(lines)

        if name == 'LinkerDirVFReference':
            lines = [f"    External Index: {content.ext_index}"]
            if content.ext_symbol:
                lines.append(f"    External: {content.ext_symbol}")
            if content.is_comdat:
                lines.append("    Reference Type: COMDAT")
                if content.lname_index is not None:
                    lines.append(f"    LNAME Index: {content.lname_index}")
                if content.comdat_name:
                    lines.append(f"    COMDAT Name: {content.comdat_name}")
            else:
                lines.append("    Reference Type: Segment")
                if content.segment_index is not None:
                    lines.append(f"    Segment Index: {content.segment_index}")
                if content.segment_name:
                    lines.append(f"    Segment: {content.segment_name}")
            return "\n".join(lines)

        if name == 'LinkerDirPackData':
            return f"    Pack Limit: {content.pack_limit} bytes (0x{content.pack_limit:08X})"

        if name == 'LinkerDirFlatAddrs':
            return "    (Debug addresses use flat model)"

        if name == 'LinkerDirTimestamp':
            lines = [f"    Timestamp: 0x{content.timestamp:08X}"]
            if content.timestamp_readable:
                lines.append(f"    Date/Time: {content.timestamp_readable}")
            return "\n".join(lines)

        return ""

    def format_summary(self, omf: "OMFFile") -> str:
        """Format the end-of-parse summary."""
        lines = [
            "",
            "=" * 60,
            f"Total Records: {len(omf.records)}"
        ]

        all_warnings = []
        all_errors = []
        for result in omf.parsed_records:
            if result.error:
                all_errors.append(result.error)
            if result.parsed:
                all_warnings.extend(self._collect_warnings(result.parsed))

        if all_warnings or all_errors:
            lines.append("=" * 60)
            lines.append("SUMMARY:")

            if all_errors:
                lines.append(f"\nErrors ({len(all_errors)}):")
                for error in all_errors:
                    lines.append(f"  {error}")

            if all_warnings:
                lines.append(f"\nWarnings ({len(all_warnings)}):")
                for warning in all_warnings:
                    lines.append(f"  {warning}")

        lines.append("=" * 60)

        return "\n".join(lines)

    def _collect_warnings(self, parsed: ParsedRecord) -> list[str]:
        """Collect warnings from a parsed record and its nested content."""
        warnings: list[str] = []
        if hasattr(parsed, 'warnings'):
            warnings.extend(parsed.warnings)
        if hasattr(parsed, 'content') and parsed.content and hasattr(parsed.content, 'warnings'):
            warnings.extend(parsed.content.warnings)
        if hasattr(parsed, 'subrecords'):
            for sub in parsed.subrecords:
                if hasattr(sub, 'warnings'):
                    warnings.extend(sub.warnings)
        return warnings


class JSONFormatter:
    """Format parsed OMF data as JSON."""

    def __init__(self, indent: int = 2):
        self.indent = indent

    def format_file(self, omf: "OMFFile", include_raw: bool = False) -> str:
        """Format entire parsed file as JSON."""
        all_warnings: list[str] = []
        all_errors: list[str] = []
        for result in omf.parsed_records:
            if result.error:
                all_errors.append(result.error)
            if result.parsed:
                all_warnings.extend(self._collect_warnings(result.parsed))

        parsed_file = ParsedOMFFile(
            filepath=omf.filepath,
            file_size=len(omf.data) if omf.data else 0,
            is_library=omf.is_library,
            variant=omf.variant.name,
            mixed_variants=omf.mixed_variants,
            seen_variants=sorted(omf.seen_variants) if omf.mixed_variants else None,
            features=sorted(omf.features),
            records=omf.parsed_records,
            warnings=all_warnings,
            errors=all_errors
        )

        exclude = None if include_raw else {'records': {'__all__': {'raw_content'}}}
        return parsed_file.model_dump_json(
            indent=self.indent,
            by_alias=True,
            exclude_none=True,
            exclude=exclude
        )

    def _collect_warnings(self, parsed: ParsedRecord) -> list[str]:
        """Collect warnings from a parsed record and its nested content."""
        warnings: list[str] = []
        if hasattr(parsed, 'warnings'):
            warnings.extend(parsed.warnings)
        if hasattr(parsed, 'content') and parsed.content and hasattr(parsed.content, 'warnings'):
            warnings.extend(parsed.content.warnings)
        if hasattr(parsed, 'subrecords'):
            for sub in parsed.subrecords:
                if hasattr(sub, 'warnings'):
                    warnings.extend(sub.warnings)
        return warnings
