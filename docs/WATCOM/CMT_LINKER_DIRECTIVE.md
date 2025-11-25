  1. Introduction

  1.1 Overview

  The Object Module Format (OMF) is a relocatable object file format originally developed by Intel for use with x86 processors. It was widely adopted by DOS and early Windows compilers, including Microsoft C, Borland C/C++, and Watcom C/C++.

  Within OMF, the COMENT record (record type 0x88) is a general-purpose comment record that can contain various types of metadata, directives, and auxiliary information. Each COMENT record is categorized by a class byte that determines how the record should be interpreted.

  COMENT Class 0xFE is designated as the Linker Directive class. It provides a mechanism for compilers and other tools to embed instructions directly in object files that influence linker behavior. This class is a vendor extension primarily associated with the Watcom toolchain,
  though the concept of linker directives exists in various forms across different OMF implementations.

  1.2 Purpose

  Linker directive records serve several critical functions:

  1. Optimization Control — Enable or disable specific linker optimizations on a per-segment or per-fixup basis
  2. Virtual Function Support — Communicate virtual function table definitions and references for C++ dead code elimination
  3. Debug Information — Specify source language and debug format versioning
  4. Library Management — Specify default libraries with priority levels and data packing requirements
  5. Timestamp Preservation — Record original object file timestamps when objects are stored in libraries

  ---
  2. Record Structure

  2.1 General COMENT Record Format

  A COMENT record follows the standard OMF record structure:

  ┌─────────┬─────────────┬────────────┬───────┬──────────────┬──────────┐
  │ RecType │ RecLength   │ Attrib     │ Class │ Data         │ Checksum │
  │ (1 byte)│ (2 bytes)   │ (1 byte)   │(1 byte)│ (variable)   │ (1 byte) │
  └─────────┴─────────────┴────────────┴───────┴──────────────┴──────────┘
     0x88      little-end    flags        0xFE    directive      sum=0

  | Field     | Size     | Description                                                  |
  |-----------|----------|--------------------------------------------------------------|
  | RecType   | 1 byte   | Always 0x88 for COMENT records                               |
  | RecLength | 2 bytes  | Length of remaining data (little-endian), including checksum |
  | Attrib    | 1 byte   | Attribute flags (see §2.2)                                   |
  | Class     | 1 byte   | 0xFE for linker directives                                   |
  | Data      | variable | Directive-specific payload                                   |
  | Checksum  | 1 byte   | Two's complement checksum (all bytes sum to 0)               |

  Important: The RecLength field specifies the number of bytes following the length field itself, which includes the attribute byte, class byte, directive data, AND the checksum byte.

  2.2 Attribute Byte

  The attribute byte contains two flag bits:

  | Bit | Mask | Name           | Description                                       |
  |-----|------|----------------|---------------------------------------------------|
  | 7   | 0x80 | TNP (No Purge) | Record should not be purged by librarians/linkers |
  | 6   | 0x40 | TNL (No List)  | Record should not appear in listings              |

  For linker directives, the TNP bit (0x80) is typically set to ensure the directive survives processing through library managers and other tools.

  2.3 Linker Directive Data Format

  The data portion of a class 0xFE COMENT begins with a single ASCII character that identifies the specific directive type:

  ┌───────────────┬────────────────────────────────┐
  │ Directive Code│ Directive-Specific Data        │
  │ (1 byte ASCII)│ (variable length)              │
  └───────────────┴────────────────────────────────┘

  ---
  3. Directive Types

  3.1 Summary Table

  | Code | ASCII | Name                | Description                                     |
  |------|-------|---------------------|-------------------------------------------------|
  | 0x44 | 'D'   | Source Language     | Debug version and source language identifier    |
  | 0x4C | 'L'   | Default Library     | Specify a default library with priority         |
  | 0x4F | 'O'   | Optimize Far Calls  | Enable far call optimization for a segment      |
  | 0x55 | 'U'   | Optimization Unsafe | Mark a fixup as unsafe for optimization         |
  | 0x56 | 'V'   | VF Table Definition | Define a virtual function table (lazy external) |
  | 0x50 | 'P'   | VF Pure Definition  | Virtual function table with pure virtual        |
  | 0x52 | 'R'   | VF Reference        | Reference to a virtual function                 |
  | 0x37 | '7'   | Pack Far Data       | Specify far data packing threshold              |
  | 0x46 | 'F'   | Flat Addresses      | Debug addresses use flat model                  |
  | 0x54 | 'T'   | Object Timestamp    | Original timestamp when archived in library     |

  3.2 Directive Details

  3.2.1 'D' — Source Language Directive

  Specifies the source language and debug format version for the object module.

	Format:
  ┌─────┬───────────┬───────────┬────────────────────────────┐
  │ 'D' │ Major Ver │ Minor Ver │ Language Name              │
  │ 1B  │ 1 byte    │ 1 byte    │ Raw bytes (to end of rec)  │
  └─────┴───────────┴───────────┴────────────────────────────┘

  Fields:
  - Major Version: Debug format major version number
  - Minor Version: Debug format minor version number
  - Length: Length of the language name string
  - Language Name: ASCII string identifying the source language (e.g., "C", "FORTRAN", "C++")

  Example: Debug version 1.3, language "C":
	44 01 03 43
	'D' maj min 'C'

  3.2.2 'L' — Default Library Directive

  Specifies a library that should be searched automatically during linking, with an associated priority level.

  Format:
  ┌─────┬──────────┬─────────────────────────────┐
  │ 'L' │ Priority │ Library Name                │
  │ 1B  │ 1 byte   │ Raw bytes (to end of record)│
  └─────┴──────────┴─────────────────────────────┘

  Fields:
  - Priority: ASCII digit character ('0' through '9') indicating search priority. Lower values indicate higher priority. The linker converts this by subtracting ASCII '0' (0x30).
  - Library Name: Raw ASCII string (NOT length-prefixed) extending to the end of the record data.

  Behavior: The linker adds the specified library to its search list. Libraries with lower priority values are searched first. This mechanism allows compilers to specify runtime libraries while giving user-specified libraries precedence.

  Example: Add "CLIB" with priority 5:
  4C 35 43 4C 49 42
  'L' '5' 'C' 'L' 'I' 'B'

  3.2.3 'O' — Optimize Far Calls Directive

  Instructs the linker that far call/jump optimization is safe for a specific segment.

  Format:
  ┌─────┬───────────────┐
  │ 'O' │ Segment Index │
  │ 1B  │ 1-2 bytes     │
  └─────┴───────────────┘

  Fields:
  - Segment Index: OMF index referencing a SEGDEF record (see §4 for index encoding)

  Behavior: When the linker performs far call optimization, it converts far calls (CALL seg:offset) to near calls with padding when the caller and callee are in the same segment. The typical transformation is:

  Before:  CALL FAR seg:offset     (5 bytes: 9A xx xx xx xx)
  After:   NOP                     (1 byte:  90)
           PUSH CS                 (1 byte:  0E)
           CALL NEAR offset        (3 bytes: E8 xx xx)

  This directive indicates that such optimization is safe for all fixups targeting the specified segment. It also marks the segment as containing code.

  3.2.4 'U' — Optimization Unsafe Directive

  Marks the immediately preceding fixup as unsafe for far call optimization.

  Format:
  ┌─────┐
  │ 'U' │
  │ 1B  │
  └─────┘

  Behavior: This directive must immediately follow a FIXUPP record. It sets a flag indicating that the preceding fixup should not be subjected to far call optimization, even if the containing segment is otherwise marked safe with an 'O' directive.

  This is necessary when:
  - The code performs arithmetic on the segment value
  - The call target may change at runtime
  - The fixup is used for data references, not code calls
  - The code makes assumptions about the instruction encoding

  Positional Requirement: The 'U' directive is stateful—it affects the most recently processed FIXUPP record. The linker typically sets an internal flag (FMT_UNSAFE_FIXUPP) that is checked during fixup processing.

  3.2.5 'V' — Virtual Function Table Definition

  Defines a virtual function table as a "lazy external" that may be eliminated if unreferenced.

  Format:
  ┌─────┬───────────────┬───────────────┬──────────────────────┐
  │ 'V' │ VF Table Ext  │ Default Ext   │ LNAME Indices...     │
  │ 1B  │ Index         │ Index         │                      │
  │     │ 1-2 bytes     │ 1-2 bytes     │ 1-2 bytes each       │
  └─────┴───────────────┴───────────────┴──────────────────────┘

  Fields:
  - VF Table External Index: EXTDEF index of the virtual function table symbol. This external is marked as "weak" (can be eliminated if unreferenced).
  - Default External Index: EXTDEF index of a default/fallback external symbol.
  - LNAME Indices: Variable-length list of LNAME indices. Each index references an LNAMES record entry containing the name of a virtual function in the table. The list continues to the end of the record.

  Behavior: Enables dead code elimination for C++ virtual functions. The linker tracks which virtual function tables are actually referenced. If no code references a virtual function table, the linker can eliminate both the table and all unreferenced virtual function
  implementations.

  3.2.6 'P' — Pure Virtual Function Table Definition

  Identical to 'V', but indicates the table contains one or more pure virtual functions.

  Format: Same as 'V' directive.

  Behavior: The presence of a pure virtual function affects how the linker handles undefined references within the table. Pure virtual functions may not have implementations, so the linker treats missing definitions differently.

  3.2.7 'R' — Virtual Function Reference

  Indicates that code references a virtual function, preventing its elimination.

  Format:
  ┌─────┬──────────────┬───────────────┬─────────────────────┐
  │ 'R' │ External Idx │ Type/Index    │ (Conditional)       │
  │ 1B  │ 1-2 bytes    │ 1-2 bytes     │ LNAME Index         │
  │     │              │               │ 1-2 bytes           │
  └─────┴──────────────┴───────────────┴─────────────────────┘

  Fields:
  - External Index: EXTDEF index of the virtual function table being referenced.
  - Type/Index: This field serves dual purpose:
    - If zero (0): Indicates a COMDAT reference. A third field follows containing an LNAME index.
    - If non-zero: This value is a SEGDEF index indicating the segment containing the reference.
  - LNAME Index (conditional): Only present if Type/Index was zero. Contains an LNAME index identifying the specific COMDAT function being referenced.

  Behavior: Marks a specific virtual function as used, preventing dead code elimination from removing it. The linker uses this information during its virtual function elimination pass.

  If the external symbol referenced is not yet defined, the linker marks it with a "VF_MARKED" flag for later processing.

  3.2.8 '7' — Pack Far Data Directive

  Specifies the threshold for packing far data segments.

  Format:
  ┌─────┬───────────────┐
  │ '7' │ Pack Limit    │
  │ 1B  │ 4 bytes       │
  └─────┴───────────────┘

  Fields:
  - Pack Limit: 32-bit unsigned integer (little-endian) specifying the maximum size in bytes for far data segment packing.

  Behavior: Far data segments smaller than the pack limit may be combined by the linker to reduce segment overhead. This directive is typically emitted by compilers based on command-line options.

  The linker only processes the first '7' directive encountered; subsequent directives are ignored (the LF_PACKDATA_FLAG prevents reprocessing).

  3.2.9 'F' — Flat Addresses Directive

  Indicates that debug information uses flat (32-bit linear) addresses.

  Format:
  ┌─────┐
  │ 'F' │
  │ 1B  │
  └─────┘

  Behavior: Sets a flag on the current module (MOD_FLATTEN_DBI) indicating that addresses in debug information should be interpreted as flat model addresses rather than segmented addresses. This is relevant for 32-bit protected mode code.

  3.2.10 'T' — Object Timestamp Directive

  Records the original modification timestamp of an object file when it is archived into a library.

  Format:
  ┌─────┬──────────────────┐
  │ 'T' │ Timestamp        │
  │ 1B  │ 4 bytes          │
  └─────┴──────────────────┘

  Fields:
  - Timestamp: 32-bit value representing the original file timestamp. Typically stored as a Unix-style timestamp (seconds since January 1, 1970) or DOS timestamp format.

  Behavior: When a librarian archives an object file into a library, it may insert this directive to preserve the original object file's modification time. This enables incremental build systems to correctly track dependencies even when objects are retrieved from libraries.

  ---
  4. Index Encoding

  Several directives use OMF index values to reference SEGDEF, EXTDEF, LNAMES, or other records. OMF indices use a variable-length encoding:

  Single-byte form (values 0-127):
  ┌─────────┐
  │ 0xxxxxxx│  Bit 7 = 0
  └─────────┘

  Two-byte form (values 128-32767):
  ┌─────────┬─────────┐
  │ 1xxxxxxx│ xxxxxxxx│  Bit 7 of first byte = 1
  └─────────┴─────────┘
    High bits  Low bits

  Decoding Algorithm:
  unsigned int GetIndex(const uint8_t **ptr) {
      uint8_t first = *(*ptr)++;
      if (first < 0x80) {
          return first;
      } else {
          uint8_t second = *(*ptr)++;
          return ((first & 0x7F) << 8) | second;
      }
  }

  Encoding Algorithm:
  void PutIndex(uint8_t **ptr, unsigned int index) {
      if (index < 0x80) {
          *(*ptr)++ = index;
      } else {
          *(*ptr)++ = 0x80 | (index >> 8);
          *(*ptr)++ = index & 0xFF;
      }
  }

  Index Types:
  - Segment Index (SI): References a SEGDEF record
  - External Index (EI): References an EXTDEF record
  - LNAME Index: References an entry in the LNAMES table
  - COMDAT Index (CI): References a COMDAT record

  ---
  5. Implementation Guide

  5.1 Reading COMENT 0xFE Records

  #include <stdint.h>
  #include <stdbool.h>

  #define CMT_LINKER_DIRECTIVE 0xFE

  typedef enum {
      LDIR_SOURCE_LANGUAGE = 'D',
      LDIR_DEFAULT_LIBRARY = 'L',
      LDIR_OPT_FAR_CALLS   = 'O',
      LDIR_OPT_UNSAFE      = 'U',
      LDIR_VF_TABLE_DEF    = 'V',
      LDIR_VF_PURE_DEF     = 'P',
      LDIR_VF_REFERENCE    = 'R',
      LDIR_PACKDATA        = '7',
      LDIR_FLAT_ADDRS      = 'F',
      LDIR_OBJ_TIMESTAMP   = 'T'
  } linker_directive_t;

  /* Global state for 'U' directive */
  static bool unsafe_fixup_pending = false;

  void process_linker_directive(const uint8_t *data, const uint8_t *end) {
      if (data >= end) return;

      uint8_t directive = *data++;

      switch (directive) {
      case LDIR_SOURCE_LANGUAGE: {
          uint8_t major = *data++;
          uint8_t minor = *data++;
          uint8_t len = *data++;
          /* Language name follows for 'len' bytes */
          process_source_language(major, minor, (const char *)data, len);
          break;
      }

      case LDIR_DEFAULT_LIBRARY: {
          uint8_t priority = *data++ - '0';
          size_t name_len = end - data;
          /* Library name extends to end of record (no length prefix) */
          add_default_library((const char *)data, name_len, priority);
          break;
      }

      case LDIR_OPT_FAR_CALLS: {
          unsigned int seg_idx = get_index(&data);
          mark_segment_optimizable(seg_idx);
          break;
      }

      case LDIR_OPT_UNSAFE:
          unsafe_fixup_pending = true;
          break;

      case LDIR_VF_TABLE_DEF:
      case LDIR_VF_PURE_DEF: {
          bool is_pure = (directive == LDIR_VF_PURE_DEF);
          unsigned int vf_ext_idx = get_index(&data);
          unsigned int default_ext_idx = get_index(&data);
          /* Remaining data contains LNAME indices */
          process_vf_table(vf_ext_idx, default_ext_idx,
                           data, end, is_pure);
          break;
      }

      case LDIR_VF_REFERENCE: {
          unsigned int ext_idx = get_index(&data);
          unsigned int type_idx = get_index(&data);
          if (type_idx == 0) {
              /* COMDAT reference - read LNAME index */
              unsigned int lname_idx = get_index(&data);
              process_vf_comdat_ref(ext_idx, lname_idx);
          } else {
              /* Segment reference */
              process_vf_segment_ref(ext_idx, type_idx);
          }
          break;
      }

      case LDIR_PACKDATA: {
          uint32_t pack_limit = data[0] | (data[1] << 8) |
                                (data[2] << 16) | (data[3] << 24);
          set_pack_data_limit(pack_limit);
          break;
      }

      case LDIR_FLAT_ADDRS:
          set_flat_debug_addresses(true);
          break;

      case LDIR_OBJ_TIMESTAMP: {
          uint32_t timestamp = data[0] | (data[1] << 8) |
                               (data[2] << 16) | (data[3] << 24);
          set_object_timestamp(timestamp);
          break;
      }

      default:
          /* Unknown directive - ignore for forward compatibility */
          break;
      }
  }

  /* Call this after processing each FIXUPP record */
  void check_unsafe_fixup(void) {
      if (unsafe_fixup_pending) {
          mark_last_fixup_unsafe();
          unsafe_fixup_pending = false;
      }
  }

  5.2 Writing COMENT 0xFE Records

  #define COMENT      0x88
  #define CMT_TNP     0x80

  static uint8_t record_buffer[256];
  static size_t record_pos;

  static void start_record(void) {
      record_pos = 0;
      record_buffer[record_pos++] = COMENT;
      record_pos += 2;  /* Reserve space for length */
      record_buffer[record_pos++] = CMT_TNP;
      record_buffer[record_pos++] = CMT_LINKER_DIRECTIVE;
  }

  static void add_byte(uint8_t b) {
      record_buffer[record_pos++] = b;
  }

  static void add_index(unsigned int idx) {
      if (idx < 0x80) {
          record_buffer[record_pos++] = idx;
      } else {
          record_buffer[record_pos++] = 0x80 | (idx >> 8);
          record_buffer[record_pos++] = idx & 0xFF;
      }
  }

  static void add_u32(uint32_t val) {
      record_buffer[record_pos++] = val & 0xFF;
      record_buffer[record_pos++] = (val >> 8) & 0xFF;
      record_buffer[record_pos++] = (val >> 16) & 0xFF;
      record_buffer[record_pos++] = (val >> 24) & 0xFF;
  }

  static void finish_record(FILE *out) {
      /* Fill in length (everything after length field, including checksum) */
      uint16_t length = record_pos - 3 + 1;  /* +1 for checksum */
      record_buffer[1] = length & 0xFF;
      record_buffer[2] = length >> 8;

      /* Calculate checksum */
      uint8_t checksum = 0;
      for (size_t i = 0; i < record_pos; i++) {
          checksum += record_buffer[i];
      }
      record_buffer[record_pos++] = -checksum;

      fwrite(record_buffer, 1, record_pos, out);
  }

  /* Emit 'O' directive for a segment */
  void emit_optimize_segment(FILE *out, unsigned int seg_index) {
      start_record();
      add_byte('O');
      add_index(seg_index);
      finish_record(out);
  }

  /* Emit 'U' directive (no data, just the directive byte) */
  void emit_unsafe_fixup(FILE *out) {
      start_record();
      add_byte('U');
      finish_record(out);
  }

  /* Emit 'L' directive for default library */
  void emit_default_library(FILE *out, unsigned int priority, 
                            const char *name, size_t name_len) {
      start_record();
      add_byte('L');
      add_byte('0' + priority);
      for (size_t i = 0; i < name_len; i++) {
          add_byte(name[i]);
      }
      finish_record(out);
  }

  /* Emit '7' directive for pack data limit */
  void emit_pack_data_limit(FILE *out, uint32_t limit) {
      start_record();
      add_byte('7');
      add_u32(limit);
      finish_record(out);
  }

  /* Emit 'T' directive for timestamp */
  void emit_timestamp(FILE *out, uint32_t timestamp) {
      start_record();
      add_byte('T');
      add_u32(timestamp);
      finish_record(out);
  }

  /* Emit 'F' directive for flat addresses */
  void emit_flat_addresses(FILE *out) {
      start_record();
      add_byte('F');
      finish_record(out);
  }

  5.3 Processing Sequence

  Linker directive processing typically occurs in this order:

  1. First Pass (Symbol Collection)
    - Collect all EXTDEF, PUBDEF, SEGDEF, and LNAMES records
    - Process 'D' (source language) directives for debug info setup
    - Process 'L' (default library) directives to build library search list
    - Collect 'V' and 'P' (VF table definition) directives for dead code analysis
    - Process 'O' (optimize far calls) to mark segments as optimizable
  2. Second Pass (Relocation/Optimization)
    - Process FIXUPP records
    - Check for 'U' (unsafe optimization) directives after each FIXUPP
    - Apply far call optimization where safe
    - Resolve 'R' (VF reference) directives for dead code analysis
  3. Final Pass
    - Apply '7' (pack far data) threshold to segment layout decisions
    - Use 'F' (flat addresses) flag when generating debug information
    - Preserve 'T' (timestamp) information in output or for dependency tracking

  5.4 Checksum Calculation

  All OMF records use a checksum byte that makes the sum of all record bytes (including the checksum itself) equal to zero when computed as an 8-bit value:

  uint8_t calculate_checksum(const uint8_t *record, size_t len) {
      uint8_t sum = 0;
      for (size_t i = 0; i < len; i++) {
          sum += record[i];
      }
      return (uint8_t)(-(int8_t)sum);
  }

  bool verify_checksum(const uint8_t *record, size_t len) {
      uint8_t sum = 0;
      for (size_t i = 0; i < len; i++) {
          sum += record[i];
      }
      return (sum == 0);
  }

  ---
  6. Interaction with Other Records

  6.1 FIXUPP Record Interaction

  The 'U' (optimization unsafe) directive has a special positional relationship with FIXUPP records:

  ┌──────────────────┐
  │ LEDATA/LIDATA    │  ← Data record
  └──────────────────┘
  ┌──────────────────┐
  │ FIXUPP Record    │  ← Contains relocation to potentially optimize
  └──────────────────┘
  ┌──────────────────┐
  │ COMENT 0xFE 'U'  │  ← Marks the FIXUPP as unsafe for optimization
  └──────────────────┘

  Implementations must track the "previous fixup" context. The typical approach is to set a flag when 'U' is encountered, then check and clear this flag when the next FIXUPP is processed.

  6.2 SEGDEF Interaction

  The 'O' directive references SEGDEF records by index. The segment indices used in directives follow standard OMF segment reference ordering:

  - Index 1 = First SEGDEF in the module
  - Index 2 = Second SEGDEF in the module
  - etc.

  Index 0 is reserved/invalid for segment references.

  6.3 EXTDEF/LNAMES Interaction

  The virtual function directives ('V', 'P', 'R') use both EXTDEF and LNAMES indices:

  - EXTDEF indices: Reference external symbol definitions for the VF table symbol and default symbol
  - LNAMES indices: Reference logical name strings for individual virtual function names

  This separation allows the linker to:
  1. Track external symbol references for linking
  2. Resolve function names for dead code analysis
  3. Match virtual function calls to their implementations

  6.4 Record Ordering Requirements

  For correct processing, records should appear in this general order within an object module:

  1. THEADR (module header)
  2. LNAMES (logical names)
  3. SEGDEF (segment definitions)
  4. EXTDEF (external definitions)
  5. COMENT records (including 0xFE directives)
  6. LEDATA/LIDATA (data records)
  7. FIXUPP (fixup records)
  8. COMENT 0xFE 'U' (if marking previous fixup unsafe)
  9. MODEND (module end)

  ---
  7. Complete Record Examples

  7.1 Default Library Directive

  Add "CLIB" as a default library with priority 5:

  Offset  Hex                         Description
  ------  --------------------------  -----------
  0000    88                          COMENT record type
  0001    08 00                       Length = 8 bytes
  0003    80                          Attribute = TNP (no purge)
  0004    FE                          Class = 0xFE (linker directive)
  0005    4C                          'L' = default library
  0006    35                          '5' = priority 5
  0007    43 4C 49 42                 "CLIB"
  000B    xx                          Checksum

  Raw: 88 08 00 80 FE 4C 35 43 4C 49 42 xx

  7.2 Optimize Far Calls for Segment 3

  Offset  Hex                         Description
  ------  --------------------------  -----------
  0000    88                          COMENT record type
  0001    04 00                       Length = 4 bytes
  0003    80                          Attribute = TNP
  0004    FE                          Class = linker directive
  0005    4F                          'O' = optimize far calls
  0006    03                          Segment index = 3 (single byte form)
  0007    xx                          Checksum

  Raw: 88 04 00 80 FE 4F 03 xx

  7.3 Optimize Far Calls for Segment 200

  Offset  Hex                         Description
  ------  --------------------------  -----------
  0000    88                          COMENT record type
  0001    05 00                       Length = 5 bytes
  0003    80                          Attribute = TNP
  0004    FE                          Class = linker directive
  0005    4F                          'O' = optimize far calls
  0006    80 C8                       Segment index = 200 (two byte form: 0x80|0, 0xC8)
  0008    xx                          Checksum

  Raw: 88 05 00 80 FE 4F 80 C8 xx

  7.4 Mark Fixup as Optimization-Unsafe

  Offset  Hex                         Description
  ------  --------------------------  -----------
  0000    88                          COMENT record type
  0001    04 00                       Length = 4 bytes
  0003    80                          Attribute = TNP
  0004    FE                          Class = linker directive
  0005    55                          'U' = optimization unsafe
  0006    A1                          Checksum

  Raw: 88 04 00 80 FE 55 A1

  Checksum verification:
    0x88 + 0x04 + 0x00 + 0x80 + 0xFE + 0x55 + 0xA1
  = 0x88 + 0x04 + 0x80 + 0xFE + 0x55 + 0xA1
  = 0x300
  = 0x00 (low byte)  ✓

  7.5 Pack Far Data with 64KB Limit

  Offset  Hex                         Description
  ------  --------------------------  -----------
  0000    88                          COMENT record type
  0001    08 00                       Length = 8 bytes
  0003    80                          Attribute = TNP
  0004    FE                          Class = linker directive
  0005    37                          '7' = pack data
  0006    00 00 01 00                 Pack limit = 0x00010000 (65536 bytes, little-endian)
  000A    xx                          Checksum

  Raw: 88 08 00 80 FE 37 00 00 01 00 xx

  7.6 Flat Addresses Directive

  Offset  Hex                         Description
  ------  --------------------------  -----------
  0000    88                          COMENT record type
  0001    04 00                       Length = 4 bytes
  0003    80                          Attribute = TNP
  0004    FE                          Class = linker directive
  0005    46                          'F' = flat addresses
  0006    xx                          Checksum

  Raw: 88 04 00 80 FE 46 xx

  7.7 Object Timestamp

  Offset  Hex                         Description
  ------  --------------------------  -----------
  0000    88                          COMENT record type
  0001    08 00                       Length = 8 bytes
  0003    80                          Attribute = TNP
  0004    FE                          Class = linker directive
  0005    54                          'T' = timestamp
  0006    78 56 34 12                 Timestamp = 0x12345678 (little-endian)
  000A    xx                          Checksum

  Raw: 88 08 00 80 FE 54 78 56 34 12 xx

  7.8 Source Language Directive

  Offset  Hex                         Description
  ------  --------------------------  -----------
  0000    88                          COMET record type
  0001    08 00                       Length = 8 bytes
  0003    80                          Attribute = TNP
  0004    FE                          Class = linker directive
  0005    44                          'D' = source language
  0006    01                          Major version = 1
  0007    03                          Minor version = 3
  0008    43 2B 2B                    "C++"
  000B    xx                          Checksum

  Raw: 88 08 00 80 FE 44 01 03 43 2B 2B xx

  ---
  8. Error Handling

  Implementations should handle these error conditions:

  | Condition                     | Recommended Action                                               |
  |-------------------------------|------------------------------------------------------------------|
  | Unknown directive code        | Ignore and continue (forward compatibility)                      |
  | Invalid segment index         | Report warning, skip directive                                   |
  | Invalid external index        | Report warning, skip directive                                   |
  | Malformed index encoding      | Report error, abort record processing                            |
  | Missing 'U' directive context | Ignore (no previous fixup to mark)                               |
  | Duplicate 'D' directive       | Use first occurrence or last occurrence (implementation-defined) |
  | Duplicate '7' directive       | Use first occurrence (subsequent ignored)                        |
  | Conflicting 'O' and 'U'       | 'U' takes precedence (safety)                                    |
  | Truncated record              | Report error, skip to next record                                |
  | Invalid checksum              | Report warning, process anyway or skip (implementation-defined)  |

  ---
  9. Compatibility Notes

  9.1 Microsoft vs. Watcom Extensions

  Microsoft's OMF implementation (used by LINK.EXE) defines its own set of COMENT classes and directives. While class 0xFE may exist in Microsoft's toolchain, the specific directive codes and semantics differ:

  | Aspect           | Watcom                       | Microsoft                        |
  |------------------|------------------------------|----------------------------------|
  | Class 0xFE       | Linker Directives            | May be used differently          |
  | VF Table Support | Built-in ('V', 'P', 'R')     | Via COMDAT records               |
  | Far Call Opt     | 'O' and 'U' directives       | Different mechanism              |
  | Default Library  | Class 0xFE 'L' with priority | Class 0x9F (CMT_DEFAULT_LIBRARY) |

  Note: Microsoft's CMT_DEFAULT_LIBRARY (class 0x9F) provides similar functionality to Watcom's 'L' directive but without the priority mechanism.

  9.2 Borland Extensions

  Borland's toolchain uses different COMENT classes for similar functionality:

  - Class 0xE9 (CMT_DEPENDENCY) — Dependency file tracking (similar concept to 'T' directive)
  - No direct equivalent to Watcom's VF table directives

  9.3 Recommended Practice for Tool Authors

  For maximum compatibility when writing tools that process OMF files:

  1. Preserve unknown directives — When processing object files, preserve unrecognized 0xFE directives unchanged
  2. Check class before assuming format — Different vendors use different directive encodings
  3. Handle both library mechanisms — Support both CMT_DEFAULT_LIBRARY (0x9F) and LDIR_DEFAULT_LIBRARY ('L')
  4. Graceful degradation — If VF directives are not understood, ignore them rather than failing

  For maximum compatibility when writing tools that generate OMF files:

  1. Use standard classes when possible — CMT_DEFAULT_LIBRARY (0x9F) is more widely supported than 'L'
  2. Document extensions — If using Watcom-specific directives, document this in tool output
  3. Test with multiple linkers — Verify output works with target toolchains

  ---
  10. References

  1. Intel, "8086 Object Module Formats (OMF)", Intel Order Number 121748
  2. Tool Interface Standard (TIS), "Relocatable Object Module Format Specification", Version 1.1
  3. Microsoft, "MS-DOS Programmer's Reference", Microsoft Press
  4. Watcom, "Watcom C/C++ Programmer's Guide"
  5. Open Watcom Project, Source code and documentation (https://github.com/open-watcom)

  ---
  Appendix A: Quick Reference Card

  A.1 Record Structure

  88 LL LL AA FE DD [data...] CC
  │  │     │  │  │           └── Checksum
  │  │     │  │  └── Directive code
  │  │     │  └── Class (0xFE)
  │  │     └── Attribute (0x80 = TNP)
  │  └── Length (little-endian, includes checksum)
  └── COMENT record type

  A.2 Directive Codes

  'D' (0x44) = Source Language    'L' (0x4C) = Default Library
  'O' (0x4F) = Optimize Far Calls 'U' (0x55) = Unsafe Fixup
  'V' (0x56) = VF Table Def       'P' (0x50) = VF Pure Def
  'R' (0x52) = VF Reference       '7' (0x37) = Pack Data
  'F' (0x46) = Flat Addresses     'T' (0x54) = Timestamp

  A.3 Index Encoding

  0x00-0x7F: Single byte (value = byte)
  0x80-0xFF: Two bytes (value = ((byte1 & 0x7F) << 8) | byte2)
