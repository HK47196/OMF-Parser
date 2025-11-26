"""LIDATA record handler."""

from . import omf_record
from ..constants import RecordType
from ..models import ParsedLIData, ParsedLIDataBlock
from ..parsing import RecordParser
from ..protocols import OMFFileProtocol
from ..scanner import RecordInfo


def parse_lidata_blocks(
    sub: RecordParser, is_32bit: bool
) -> tuple[list[ParsedLIDataBlock], list[str]]:
    """Parse LIDATA-style iterated data blocks from a parser.

    Used by both LIDATA records and COMDAT records with iterated data flag.
    Returns tuple of (blocks list, warnings list).
    """
    blocks: list[ParsedLIDataBlock] = []
    warnings: list[str] = []
    truncated = False

    def parse_data_block(depth: int = 0) -> ParsedLIDataBlock | None:
        nonlocal truncated
        repeat_size = sub.get_lidata_repeat_count_size(is_32bit)
        min_bytes = repeat_size + 2

        if sub.bytes_remaining() < min_bytes:
            if sub.bytes_remaining() > 0 and not truncated:
                warnings.append(
                    f"Truncated data block at depth {depth}: "
                    f"need {min_bytes} bytes, have {sub.bytes_remaining()}"
                )
                truncated = True
            return None

        repeat_count = sub.parse_numeric(repeat_size)
        block_count = sub.parse_numeric(2)

        block = ParsedLIDataBlock(
            repeat_count=repeat_count,
            block_count=block_count
        )

        if block_count == 0:
            content_len = sub.read_byte()
            if content_len is None:
                warnings.append(f"Missing content length byte at depth {depth}")
                return block
            if sub.bytes_remaining() < content_len:
                warnings.append(
                    f"Truncated content at depth {depth}: "
                    f"declared {content_len} bytes, have {sub.bytes_remaining()}"
                )
                content = sub.read_bytes(sub.bytes_remaining())
            else:
                content = sub.read_bytes(content_len)
            block.content = content if content else b''
        else:
            for i in range(block_count):
                nested = parse_data_block(depth + 1)
                if nested:
                    block.nested_blocks.append(nested)
                elif not truncated:
                    warnings.append(
                        f"Missing nested block {i+1}/{block_count} at depth {depth}"
                    )

        return block

    while sub.bytes_remaining() > 0:
        block = parse_data_block(depth=0)
        if block:
            block.calculate_expanded_size()
            blocks.append(block)
        else:
            break

    return blocks, warnings


@omf_record(RecordType.LIDATA, RecordType.LIDATA32)
def handle_lidata(omf: OMFFileProtocol, record: RecordInfo) -> ParsedLIData:
    """Handle LIDATA (A2H/A3H)."""
    sub = omf.make_parser(record)
    is_32bit = (record.type == RecordType.LIDATA32)

    seg_idx = sub.parse_index()
    offset_size = sub.get_offset_field_size(is_32bit)
    offset = sub.parse_numeric(offset_size)

    result = ParsedLIData(
        is_32bit=is_32bit,
        segment=omf.get_segdef(seg_idx),
        segment_index=seg_idx,
        offset=offset
    )

    if seg_idx == 0:
        result.warnings.append("Segment index is zero (invalid per spec)")

    blocks, warnings = parse_lidata_blocks(sub, is_32bit)
    result.blocks = blocks
    result.warnings.extend(warnings)
    result.total_expanded_size = sum(b.expanded_size for b in result.blocks)

    omf.last_data_record = ('LIDATA', seg_idx, offset)

    return result
