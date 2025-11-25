OMF COMENT Class 0xFD: Disassembler Directive Record

  Technical Specification (Corrected)

  1. Overview

  The COMENT record in the Intel Object Module Format (OMF) provides a mechanism for embedding metadata and directives within object files. Class 0xFD (decimal 253), known as the Disassembler Directive (DISASM_DIRECTIVE), is a specialized comment class designed to communicate
  information to disassemblers about non-executable regions within code segments.

  2. Purpose

  Code segments in object files may contain data that should not be interpreted as machine instructions. Common examples include:

  - Switch statement scan/jump tables - Computed goto targets
  - Floating-point constants embedded inline in code
  - String literals placed in code segments
  - Lookup tables and constant data arrays

  Without explicit marking, disassemblers will attempt to decode this data as executable instructions, producing meaningless or misleading output. The DISASM_DIRECTIVE record provides bounds information that allows disassemblers to skip these regions.

  3. Record Structure

  3.1 COMENT Record Header

  All COMENT records follow the standard OMF record format:

  +--------+--------+--------+--------+--------+----...----+--------+
  | Record |  Record Length  |  Attr  | Class  |   Data    | Chksum |
  |  Type  |   (2 bytes LE)  |  Byte  |  Byte  |           |        |
  +--------+--------+--------+--------+--------+----...----+--------+
     0x88      Low     High     0x80    0xFD      varies      1 byte

  | Field         | Size    | Value     | Description                                                                   |
  |---------------|---------|-----------|-------------------------------------------------------------------------------|
  | Record Type   | 1 byte  | 0x88      | COMENT record identifier                                                      |
  | Record Length | 2 bytes | varies    | Little-endian count of all bytes following this field, including the checksum |
  | Attribute     | 1 byte  | 0x80      | No-purge (NP) bit set, no list (NL) bit clear                                 |
  | Class         | 1 byte  | 0xFD      | Disassembler directive class                                                  |
  | Data          | varies  | see below | Directive-specific data                                                       |
  | Checksum      | 1 byte  | computed  | Two's complement sum of all bytes (including record type) should equal zero   |

  3.2 Attribute Byte

  The attribute byte uses the following bit fields:

  Bit 7 (0x80): NP - No Purge. When set, record should not be stripped by librarians.
  Bit 6 (0x40): NL - No List. When set, record should not appear in listings.
  Bits 0-5:     Reserved (must be zero)

  For DISASM_DIRECTIVE records, the attribute is 0x80 (no purge, can list).

  4. Directive Subtypes

  The first byte of the data field identifies the directive subtype:

  | Subtype            | Character | Hex Value | Description                        |
  |--------------------|-----------|-----------|------------------------------------|
  | DDIR_SCAN_TABLE    | 's'       | 0x73      | 16-bit offset scan table directive |
  | DDIR_SCAN_TABLE_32 | 'S'       | 0x53      | 32-bit offset scan table directive |

  4.1 DDIR_SCAN_TABLE (0x73 / 's')

  Used for 16-bit or real-mode code where segment offsets fit in 2 bytes.

  +--------+---------------+---------------+------------+------------+
  | Type   | Segment Index | LNAME Index   | Start Ofs  | End Offset |
  | 's'    | (OMF Index)   | (OMF Index)   | (2 bytes)  | (2 bytes)  |
  +--------+---------------+---------------+------------+------------+
    1 byte    1-2 bytes      0 or 1-2*       2 bytes      2 bytes

  4.2 DDIR_SCAN_TABLE_32 (0x53 / 'S')

  Used for 32-bit protected mode code or EasyOMF/Microsoft 386 object files.

  +--------+---------------+---------------+------------+------------+
  | Type   | Segment Index | LNAME Index   | Start Ofs  | End Offset |
  | 'S'    | (OMF Index)   | (OMF Index)   | (4 bytes)  | (4 bytes)  |
  +--------+---------------+---------------+------------+------------+
    1 byte    1-2 bytes      0 or 1-2*       4 bytes      4 bytes

   The LNAME Index field is only present when Segment Index is zero.

  5. Field Descriptions

  5.1 OMF Index Encoding

  OMF uses a variable-length encoding for index values to save space:

  Single-byte encoding (values 0-127):
  +--------+
  |  0-127 |
  +--------+
    1 byte
  If the value is in the range 0x00-0x7F, it is stored directly as a single byte.

  Two-byte encoding (values 128-32767):
  +----------------+----------+
  | 1 | high 7bits | low 8bits|
  +----------------+----------+
       byte 1         byte 2
  If the value exceeds 127:
  - Byte 1: (value >> 8) | 0x80 — The high-order 7 bits with bit 7 set to indicate two-byte format
  - Byte 2: value & 0xFF — The low-order 8 bits

  Decoding algorithm:
  if (byte1 & 0x80) {
      index = ((byte1 & 0x7F) << 8) | byte2;    // two-byte form
  } else {
      index = byte1;                             // single-byte form
  }

  5.2 Segment Index

  An OMF index value identifying the segment containing the data region:

  - Non-zero value: References a SEGDEF record by 1-based index
  - Zero value: Indicates the region belongs to a COMDAT symbol; the LNAME Index field follows

  5.3 LNAME Index (Conditional)

  Present only when Segment Index is zero. This OMF index references an LNAME that identifies the COMDAT (communal data) symbol containing the data region.

  When Segment Index is non-zero, this field is absent from the record. Implementations parsing this record must check the Segment Index value before attempting to access an LNAME Index.

  5.4 Start Offset

  The beginning byte offset of the data region within the segment or COMDAT. Encoded as:
  - 2 bytes (unsigned, little-endian) for DDIR_SCAN_TABLE
  - 4 bytes (unsigned, little-endian) for DDIR_SCAN_TABLE_32

  5.5 End Offset

  The byte offset immediately after the last byte of the data region (exclusive upper bound). The data region spans the half-open interval [Start, End).

  Encoded as:
  - 2 bytes (unsigned, little-endian) for DDIR_SCAN_TABLE
  - 4 bytes (unsigned, little-endian) for DDIR_SCAN_TABLE_32

  Example: If Start=0x100 and End=0x120, the data region covers bytes 0x100 through 0x11F inclusive (32 bytes).

  6. Implementation Guidelines

  6.1 Generating DISASM_DIRECTIVE Records

  When generating object files, emit a DISASM_DIRECTIVE record whenever placing non-executable data within a code segment:

  1. Determine offset size needed:
     - If start_offset > 0xFFFF OR end_offset > 0xFFFF:
         Use DDIR_SCAN_TABLE_32 ('S', 4-byte offsets)
     - Otherwise:
         Use DDIR_SCAN_TABLE ('s', 2-byte offsets)

  2. Build the data payload:
     a. Write directive subtype byte ('s' or 'S')
     b. Write segment index using OMF index encoding
     c. If segment index is 0, write LNAME index using OMF index encoding
     d. Write start offset (2 or 4 bytes, little-endian)
     e. Write end offset (2 or 4 bytes, little-endian)

  3. Build the complete record:
     a. Record type: 0x88
     b. Record length: attr(1) + class(1) + data_length + checksum(1)
     c. Attribute: 0x80
     d. Class: 0xFD
     e. Data payload from step 2
     f. Checksum: negate the sum of all preceding bytes (mod 256)

  6.2 Parsing DISASM_DIRECTIVE Records

  1. Verify record type is COMENT (0x88)
  2. Read record length (2 bytes, little-endian)
  3. Read attribute byte (typically 0x80)
  4. Read class byte; if not 0xFD, handle as different comment class
  5. Read first data byte to determine subtype:
     - 's' (0x73): 16-bit offsets, wordsize = 2
     - 'S' (0x53): 32-bit offsets, wordsize = 4
     - Other: Unknown directive; skip or report error
  6. Read segment index (OMF index, 1-2 bytes)
  7. Initialize LNAME index to undefined/zero
  8. If segment index is 0:
     a. Read LNAME index (OMF index, 1-2 bytes)
     b. If LNAME index is also 0, report error (invalid record)
  9. Read start offset (wordsize bytes, little-endian)
  10. Read end offset (wordsize bytes, little-endian)
  11. Verify checksum if desired
  12. Store the parsed scan table entry for later use

  6.3 Using DISASM_DIRECTIVE Information

  Disassemblers and analysis tools should:

  1. Collect all DISASM_DIRECTIVE records during initial object file parsing
  2. Build a data region map keyed by segment index or COMDAT name
  3. Merge adjacent or overlapping regions for efficiency
  4. During disassembly, check each address against the map before decoding
  5. Within data regions, output raw bytes using directives such as DB, DW, DD, or equivalent
  6. Resume instruction decoding at addresses >= end offset

  7. Example Records

  7.1 Example: 16-bit Scan Table in Segment 3

  Marking bytes 0x0100-0x011F (32 bytes) in segment 3 as data:

  Offset  Hex     Description
  ------  ------  -----------
  0000    88      Record type: COMENT
  0001    09 00   Record length: 9 bytes (LE)
  0003    80      Attribute: NP=1, NL=0
  0004    FD      Class: DISASM_DIRECTIVE
  0005    73      Subtype: 's' (DDIR_SCAN_TABLE)
  0006    03      Segment index: 3 (single-byte encoding)
  0007    00 01   Start offset: 0x0100 (LE)
  0009    20 01   End offset: 0x0120 (LE)
  000B    XX      Checksum

  Record length calculation: 1 (attr) + 1 (class) + 1 (subtype) + 1 (seg) + 2 (start) + 2 (end) + 1 (checksum) = 9 bytes

  7.2 Example: 32-bit Scan Table in Segment 3

  Same region using 32-bit format:

  Offset  Hex           Description
  ------  ------------  -----------
  0000    88            Record type: COMENT
  0001    0D 00         Record length: 13 bytes (LE)
  0003    80            Attribute: NP=1, NL=0
  0004    FD            Class: DISASM_DIRECTIVE
  0005    53            Subtype: 'S' (DDIR_SCAN_TABLE_32)
  0006    03            Segment index: 3 (single-byte encoding)
  0007    00 01 00 00   Start offset: 0x00000100 (LE)
  000B    20 01 00 00   End offset: 0x00000120 (LE)
  000F    XX            Checksum

  Record length calculation: 1 + 1 + 1 + 1 + 4 + 4 + 1 = 13 bytes

  7.3 Example: Scan Table in COMDAT

  Marking bytes 0x0000-0x0040 in COMDAT referenced by LNAME index 5:

  Offset  Hex           Description
  ------  ------------  -----------
  0000    88            Record type: COMENT
  0001    0E 00         Record length: 14 bytes (LE)
  0003    80            Attribute: NP=1, NL=0
  0004    FD            Class: DISASM_DIRECTIVE
  0005    53            Subtype: 'S' (DDIR_SCAN_TABLE_32)
  0006    00            Segment index: 0 (indicates COMDAT follows)
  0007    05            LNAME index: 5 (single-byte encoding)
  0008    00 00 00 00   Start offset: 0x00000000 (LE)
  000C    40 00 00 00   End offset: 0x00000040 (LE)
  0010    XX            Checksum

  7.4 Example: Two-Byte Segment Index

  If the segment index is 200 (0xC8), it requires two-byte encoding:

  Segment index 200:
    - Byte 1: (200 >> 8) | 0x80 = 0 | 0x80 = 0x80
    - Byte 2: 200 & 0xFF = 0xC8

  Encoded as: 80 C8

  If the segment index is 300 (0x012C):
    - Byte 1: (300 >> 8) | 0x80 = 1 | 0x80 = 0x81
    - Byte 2: 300 & 0xFF = 0x2C

  Encoded as: 81 2C

  8. Compatibility Notes

  - Non-critical record: Tools that don't understand this directive can safely ignore it without affecting correctness—only disassembly quality suffers
  - Order independence: May appear anywhere in the object file after the referenced SEGDEF or LNAME records are defined
  - Multiple records: Multiple DISASM_DIRECTIVE records may exist; each defines a separate data region
  - Overlapping regions: Implementations should handle overlapping or adjacent regions gracefully by merging them
  - Librarian behavior: The NP (no-purge) attribute bit ensures librarians preserve this record when extracting modules

  9. Related OMF Comment Classes

  | Class | Name             | Purpose                                 |
  |-------|------------------|-----------------------------------------|
  | 0x00  | LANGUAGE_TRANS   | Language translator identification      |
  | 0x9F  | DEFAULT_LIBRARY  | Specify default library for linking     |
  | 0xA1  | MS_OMF           | Microsoft OMF extensions flag           |
  | 0xA8  | WKEXT            | Weak external definitions               |
  | 0xA9  | LZEXT            | Lazy external definitions               |
  | 0xAA  | EASY_OMF         | Phar Lap EasyOMF signature              |
  | 0xE9  | DEPENDENCY       | Borland file dependency record          |
  | 0xFD  | DISASM_DIRECTIVE | Disassembler directives (this document) |
  | 0xFE  | LINKER_DIRECTIVE | Linker-specific directives              |
  | 0xFF  | SOURCE_NAME      | Source filename for debugging           |
