## Record Specifics

The following is a list of record types that have been implemented and are described within the body of this document. Details of each implemented record (form and content) are presented in the following sections. The records are listed sequentially by hex value. Conflicts between various OMFs that overlap in their use of record types or fields are marked. For information on obsolete records, please refer to Appendix 3.

### Currently Implemented Records

| 80H     | THEADR  | Translator Header Record                                                                                                                                                                                                    |
|---------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 82H     | LHEADR  | Library Module Header Record                                                                                                                                                                                                |
| 88H     | COMENT  | Comment Record (Including all comment class extensions)                                                                                                                                                                     |
| 8AH/8BH | MODEND  | Module End Record                                                                                                                                                                                                           |
| 8CH     | EXTDEF  | External Names Definition Record                                                                                                                                                                                            |
| 90H/91H | PUBDEF  | Public Names Definition Record                                                                                                                                                                                              |
| 94H/95H | LINNUM  | Line Numbers Record                                                                                                                                                                                                         |
| 96H     | LNAMES  | List of Names Record                                                                                                                                                                                                        |
| 98H/99H | SEGDEF  | Segment Definition Record                                                                                                                                                                                                   |
| 9AH     | GRPDEF  | Group Definition Record                                                                                                                                                                                                     |
| 9CH/9DH | FIXUPP  | Fixup Record                                                                                                                                                                                                                |
| A0H/A1H | LEDATA  | Logical Enumerated Data Record                                                                                                                                                                                              |
| A2H/A3H | LIDATA  | Logical Iterated Data Record                                                                                                                                                                                                |
| B0H     | COMDEF  | Communal Names Definition Record                                                                                                                                                                                            |
| B2H/B3H | BAKPAT  | Backpatch Record                                                                                                                                                                                                            |
| B4H     | LEXTDEF | Local External Names Definition Record                                                                                                                                                                                      |
| B6H/B7H | LPUBDEF | Local Public Names Definition Record                                                                                                                                                                                        |
| B8H     | LCOMDEF | Local Communal Names Definition Record                                                                                                                                                                                      |
| BCH     | CEXTDEF | COMDAT External Names Definition Record                                                                                                                                                                                     |
| C2H/C3H | COMDAT  | Initialized Communal Data Record                                                                                                                                                                                            |
| C4H/C5H | LINSYM  | Symbol Line Numbers Record                                                                                                                                                                                                  |
| C6H     | ALIAS   | Alias Definition Record                                                                                                                                                                                                     |
| C8H/C9H | NBKPAT  | Named Backpatch Record                                                                                                                                                                                                      |
| CAH     | LLNAMES | Local Logical Names Definition Record                                                                                                                                                                                       |
| CCH     | VERNUM  | OMF Version Number Record                                                                                                                                                                                                   |
| CEH     | VENDEXT | Vendor-specific OMF Extension Record                                                                                                                                                                                        |
| F0H     |         | Library Header Record<br>Although this is not actually an OMF record type, the presence of a record with F0H as the first byte indicates that the module is a library. The format of a library file is given in Appendix 2. |
| F1H     |         | Library End Record                                                                                                                                                                                                          |

## 80H THEADR—Translator Header Record

### Description

The THEADR record contains the name of the object module. This name identifies an object module within an object library or in messages produced by the linker.

### History

Unchanged from the original Intel 8086 specification.

### Record Format

| 1  | 2             | 1             | <-------String Length------> | 1        |
|----|---------------|---------------|------------------------------|----------|
| 80 | Record Length | String Length | Name String                  | Checksum |

The String Length byte gives the number of characters in the name string; the name string itself is ASCII. This name is usually that of the file that contains a program's source code (if supplied by the language translator), or may be specified directly by the programmer (for example, TITLE pseudo-operand or assembler NAME directive).

### Notes

*The name string is always present; a null name is allowed but not recommended (because it doesn't provide much information for a debugging program).*

*The name string indicates the full path and filename of the file that contained the source code for the module.*

*This record, or an LHEADR record must occur as the first object record. More than one header record is allowed (as a result of an object bind, or if the source arose from multiple files as a result of include processing).*

### Example

The following THEADR record was generated by the Microsoft C Compiler:

|      | 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  | A  | B  | C | D | E | F |             |
|------|----|----|----|----|----|----|----|----|----|----|----|----|---|---|---|---|-------------|
| 0000 | 80 | 09 | 00 | 07 | 68 | 65 | 6C | 6C | 6F | 2E | 63 | CB |   |   |   |   | ...hello.c. |

Byte 00H contains 80H, indicating a THEADR record.

Bytes 01-02H contain 0009H, the length of the remainder of the record.

Bytes 03-0AH contain the T-module name. Byte 03H contains 07H, the length of the name, and bytes 04H through 0AH contain the name itself (HELLO.C).

Byte 0BH contains the Checksum field, 0CBH.

## 82H LHEADR—Library Module Header Record

### Description

This record is very similar to the THEADR record. It is used to indicate the name of a module within a library file (which has an internal organization different from that of an object module).

### History

This record type was defined in the original Intel 8086 specification with the same format but with a different purpose, so its use for libraries should be considered a Microsoft extension.

### Record Format

| 1  | 2             | 1             | <-------String Length------> | 1        |
|----|---------------|---------------|------------------------------|----------|
| 82 | Record Length | String Length | Name String                  | Checksum |

**Note:** The THEADR, and LHEADR records are handled identically. See Appendix 2 for a complete description of these library file format.

## 88H COMENT—Comment Record

### Description

The COMENT record contains a character string that may represent a plain text comment, a symbol meaningful to a program accessing the object module, or even binary-encoded identification data. An object module can contain any number of COMENT records.

### History

Before the VENDEXT record was added for TIS, the COMENT record was the primary way of extending the OMF. These extensions were added or changed for 32-bit linkers and continue to be supported in this standard. The comment classes that have been added or changed are 9D, A0, A1, A2, A4, AA, B0, and B1.

Comment class A2 was added for Microsoft C version 5.0. Histories for comment classes A0, A3, A4, A6, A7, and A8 are given later in this section.

68000 and big-endian comments were added for Microsoft C version 7.0.

### Record Format

The comment records are actually a group of items, classified by comment class.

| 1  | 2             | 1            | 1             | <---------Record Length Minus 3-------> | 1        |
|----|---------------|--------------|---------------|-----------------------------------------|----------|
| 88 | Record Length | Comment Type | Comment Class | Commentary Byte String (optional)       | Checksum |

#### Comment Type

The Comment Type field is bit significant; its layout is

| <-----------------1 byte -----------------> |    |   |   |   |   |   |   |
|---------------------------------------------|----|---|---|---|---|---|---|
| NP                                          | NL | 0 | 0 | 0 | 0 | 0 | 0 |

where

**NP** (no purge bit) is set if the comment is to be preserved by utility programs that manipulate object modules. This bit can protect an important comment, such as a copyright message, from deletion.

**NL** (no list bit) is set if the comment is not to be displayed by utility programs that list the contents of object modules. This bit can hide a comment.

The remaining bits are unused and should be set to 0.

#### Comment Class and Commentary Byte String

The Comment Class field is an 8-bit numeric field that conveys information by its value (accompanied by a null byte string) or indicates the information to be found in the accompanying byte string. The byte string's length is determined from the record length, not by an initial count byte.

The values that have been defined (including obsolete values) are the following:

| 0                       | <b>Translator</b>                                                  | Translator; it may name the source language or translator. We recommend that the translator name and version, plus the optimization level used for compilation, be recorded here. Other compiler or assembler options can be included, although current practice seems to be to place these under comment class 9D.                                                                                                                                                                                                                                                                                                                                                                          |                      |                                                                   |          |                                |                         |                                              |                   |                                                                    |
|-------------------------|--------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|-------------------------------------------------------------------|----------|--------------------------------|-------------------------|----------------------------------------------|-------------------|--------------------------------------------------------------------|
| 1                       | <b>Intel copyright</b>                                             | Ignored.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |                      |                                                                   |          |                                |                         |                                              |                   |                                                                    |
| 2 – 9B                  | <b>Intel reserved</b>                                              | These values are reserved for Intel products. Values from 9C through FF are ignored by Intel products.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |                      |                                                                   |          |                                |                         |                                              |                   |                                                                    |
| 81                      | <b>Library specifier—obsolete</b>                                  | Replaced by comment class 9F; contents are identical to 9F.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |                      |                                                                   |          |                                |                         |                                              |                   |                                                                    |
| 9C                      | <b>MS-DOS version—obsolete</b>                                     | The commentary byte string field is a 2 byte string that specifies the MS-DOS version number. This comment class is not supported by Microsoft LINK.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                      |                                                                   |          |                                |                         |                                              |                   |                                                                    |
| 9D                      | <b>Memory model</b>                                                | This information is currently generated by the Microsoft C compiler for use by the XENIX linker; it is ignored by the MS-DOS and OS/2 versions of Microsoft LINK. The byte string consists of from one to three ASCII characters and indicates the following:<br><table><tbody><tr><td><b>0, 1, 2, or 3</b></td><td>8086, 80186, 80286, or 80386 instructions generated, respectively</td></tr><tr><td><b>O</b></td><td>Optimization performed on code</td></tr><tr><td><b>s, m, c, l, or h</b></td><td>Small, medium, compact, large, or huge model</td></tr><tr><td><b>A, B, C, D</b></td><td>68000, 68010, 68020, or 68030 instructions generated, respectively</td></tr></tbody></table> | <b>0, 1, 2, or 3</b> | 8086, 80186, 80286, or 80386 instructions generated, respectively | <b>O</b> | Optimization performed on code | <b>s, m, c, l, or h</b> | Small, medium, compact, large, or huge model | <b>A, B, C, D</b> | 68000, 68010, 68020, or 68030 instructions generated, respectively |
| <b>0, 1, 2, or 3</b>    | 8086, 80186, 80286, or 80386 instructions generated, respectively  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |                      |                                                                   |          |                                |                         |                                              |                   |                                                                    |
| <b>O</b>                | Optimization performed on code                                     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |                      |                                                                   |          |                                |                         |                                              |                   |                                                                    |
| <b>s, m, c, l, or h</b> | Small, medium, compact, large, or huge model                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |                      |                                                                   |          |                                |                         |                                              |                   |                                                                    |
| <b>A, B, C, D</b>       | 68000, 68010, 68020, or 68030 instructions generated, respectively |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |                      |                                                                   |          |                                |                         |                                              |                   |                                                                    |
| 9E                      | <b>DOSSEG</b>                                                      | Sets Microsoft LINK's DOSSEG switch. The byte string is null. This record is included in the startup module in each language library. It directs the linker to use the standardized segment ordering, according to the naming conventions documented with MS-DOS, OS/2, and accompanying language products.                                                                                                                                                                                                                                                                                                                                                                                  |                      |                                                                   |          |                                |                         |                                              |                   |                                                                    |
| 9F                      | <b>Default library search name</b>                                 | The byte string contains a library filename (without a lead count byte and without an extension), which is searched in order to resolve external references within the object module. The default library search can be overridden with LINK's /NODEFAULTLIBRARYSEARCH switch.                                                                                                                                                                                                                                                                                                                                                                                                               |                      |                                                                   |          |                                |                         |                                              |                   |                                                                    |

| A0        | OMF extensions           | This class consists of a set of records, identified by subtype (first byte of commentary string). Values supported by some linkers are:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|-----------|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 01        | IMPDEF                   | Import definition record. See the IMPDEF section for a complete description.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 02        | EXPDEF                   | Export definition record. See the EXPDEF section for a complete description.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 03        | INCDEF                   | Incremental compilation record. See the INCDEF section for a complete description.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 04        | Protected memory library | 32-bit linkers only; relevant only to 32-bit dynamic-link libraries (DLLs). This comment record is inserted in an object module by the compiler when it encounters the <code>_loadds</code> construct in the source code for a DLL. The linker then sets a flag in the header of the executable file (DLL) to indicate that the DLL should be loaded in such a way that its shared data is protected from corruption. The <code>_loadds</code> keyword tells the compiler to emit modified function prolog code, which loads the DS segment register. (Normal functions don't need this.)<br>When the flag is set in the .EXE header, the loader loads the selector of a protected memory area into DS while performing run-time fixups (relocations). All other DLLs and applications get the regular DGROUP selector, which doesn't allow access to the protected memory area set up by the operating system. |
| 05        | LNKDIR                   | Microsoft C++ linker directives record. See the LNKDIR section for a complete description.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 06        | Big-endian               | The target for this OMF is a big-endian machine, as opposed to little-endian. "Big-endian" describes an architecture for which the most significant byte of a multibyte value has the smallest address. "Little-endian" describes an architecture for which the least significant byte of a multibyte value has the smallest address.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 07        | PRECOMP                  | When the Microsoft symbol and type information for this object file is emitted, the directory entry for <code>\$\$TYPES</code> is to be emitted as <code>sstPreComp</code> instead of <code>sstTypes</code> .                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| 08-<br>FF |                          | Reserved.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |

**Note:** The presence of any unrecognized subtype causes the linker to generate a fatal error.

| A1 | "New OMF" extension | <p>This comment class is now used solely to indicate the version of the symbolic debug information. If this comment class is not present, the version of the debug information produced is defined by the linker. For example, Microsoft LINK defaults to the oldest format of Microsoft symbol and type information.</p> <p>This comment class was previously used to indicate that the obsolete method of communal representation through TYPDEF and EXTDEF pairs was not used and that COMDEF records were used instead. In current linkers, COMDEF records are always enabled, even without this comment record present.</p> <p>The byte string is currently empty, but the planned future contents will be a version number (8-bit numeric field) followed by an ASCII character string indicating the symbol style. Values will be:</p> <ul><li>n,'C','V' Microsoft symbol and type style</li><li>n,'D','X' AIX style</li><li>n,'H','L' IBM PM Debugger style</li></ul> |
|----|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| A2 | Link Pass Separator | <p>This record conveys information to the linker about the organization of the file. The value of the first byte of the commentary string specifies the comment subtype. Currently, a single subtype is defined:</p> <dl><dt>01</dt><dd>Indicates the start of records generated from Pass 2 of the linker. Additional bytes may follow, with their number determined by the Record Length field, but they will be ignored by the linker.</dd></dl> <p>See the "Order of Records" section for information on which records must come before and after this comment.</p> <p><b>Warning:</b> <i>It is assumed that this comment will not be present in a module whose MODEND record contains a program starting address.</i></p> <p><i>Note: This comment class may become obsolete with the advent of COMDAT records.</i></p>                                                                                                                                                  |
| A3 | LIBMOD              | Library module comment record. Ignored by the linker; used only by the librarian. See the LIBMOD section for a complete description.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| A4 | EXESTR              | Executable string. See the EXESTR section for a complete description.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| A6 | INCERR              | Incremental compilation error. See the INCERR section for a complete description.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| A7 | NOPAD               | No segment padding. See the NOPAD section for a complete description.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| A8 | WKEXT               | Weak Extern record. See the WKEXT section for a complete description.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| A9 | LZEXT               | Lazy Extern record. See the LZEXT section for a complete description.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| DA | Comment             | For random comment.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| DB | Compiler            | For pragma comment(compiler); version number.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| DC | Date                | For pragma comment(date stamp).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| DD | Timestamp           | For pragma comment(timestamp).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| DF | User                | For pragma comment(user). Sometimes used for copyright notices.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |

| E9      | Dependency file (Borland)       | Used to show the include files that were used to build this .OBJ file.                                                                                                                              |
|---------|---------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| FF      | Command line (Microsoft QuickC) | Shows the compiler options chosen. May be obsolete. This record is also used by Phoenix Technology Ltd. for library comments.                                                                       |
| C0H-FFH | -                               | Comment classes within this range that are not otherwise used are reserved for user-defined comment classes. In general, the VENDEXT record replaces the need for new user-defined comment classes. |

### Notes

Microsoft LIB ignores the Comment Type field.

A COMENT record can appear almost anywhere in an object module. Only two restrictions apply:

- A COMENT record cannot be placed between a FIXUPP record and the LEDATA or LIDATA record to which it refers.
- A COMENT record cannot be the first or last record in an object module. (The first record must always be THEADR or LHEADR and the last must always be MODEND.)

### Examples

The following three examples are typical COMENT records taken from an object module generated by the Microsoft C Compiler.

This first example is a language-translator comment:

```
    0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
0000 88 07 00 00 4D 53 20 43 6E                     ....MS Cn
```

Byte 00H contains 88H, indicating that this is a COMENT record.

Bytes 01-02H contain 0007H, the length of the remainder of the record.

Byte 03H (the Comment Type field) contains 00H. Bit 7 (no purge) is set to 0, indicating that this COMENT record may be purged from the object module by a utility program that manipulates object modules. Bit 6 (no list) is set to 0, indicating that this comment need not be excluded from any listing of the module's contents. The remaining bits are all 0.

Byte 04H (the Comment Class field) contains 00H, indicating that this COMENT record contains the name of the language translator that generated the object module.

Bytes 05H through 08H contain the name of the language translator, Microsoft C.

Byte 09H contains the Checksum field, 6EH.

The second example contains the name of an object library to be searched by default when Microsoft LINK processes the object module containing this COMENT record:

```
    0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
0000 88 09 00 00 9F 53 4C 49 42 46 50 10            ....SLIBFP
```

###### Relocatable Object Module Format

Byte 04H (the Comment Class field) contains 9FH, indicating that this record contains the name of a library for LINK to use to resolve external references.

Bytes 05-0AH contain the library name, SLIBFP. In this example, the name refers to the Microsoft C Compiler's floating-point function library, SLIBFP.LIB.

The last example indicates that Microsoft LINK should write the most recent format of Microsoft symbol and type information to the executable file.

|      | 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9 | A | B | C | D | E | F |         |
|------|----|----|----|----|----|----|----|----|----|---|---|---|---|---|---|---|---------|
| 0000 | 88 | 06 | 00 | 00 | A1 | 01 | 43 | 56 | 37 |   |   |   |   |   |   |   | ....CV7 |

Byte 04H indicates the comment class, 0A1H.

Bytes 05-07H, which contain the comment string, are ignored by LINK.

## 88H IMPDEF—Import Definition Record (Comment Class A0, Subtype 01)Description

This record describes the imported names for a module.

### History

This comment class and subtype is a Microsoft extension added for OS/2 and Windows.

### Record Format

One import symbol is described; the subrecord format is

| 1  | 1            | <variable>    | <variable>  | 2 or <variable> |
|----|--------------|---------------|-------------|-----------------|
| 01 | Ordinal Flag | Internal Name | Module Name | Entry Ident     |

where:

**01** Identifies the subtype as an IMPDEF. It determines the form of the Entry Ident field.

**Ordinal Flag** Is a byte; if 0, the import is identified by name. If nonzero, it is identified by ordinal. It determines the form of the Entry Ident field.

**Internal Name** Is in *count, char* string format and is the name used within this module for the import symbol. This name will occur again in an EXTDEF record.

**Module Name** Is in *count, char* string format and is the name of the module (a DLL) that supplies an export symbol matching this import.

**Entry Ident** Is an ordinal or the name used by the exporting module for the symbol, depending upon the Ordinal Flag.

If this field is an ordinal (Ordinal Flag is nonzero), it is a 16-bit word. If this is a name and the first byte of the name is 0, then the exported name is the same as the imported name (in the Internal Name field). Otherwise, it is the imported name in *count, char* string format (as exported by Module Name).

**Note:** IMPDEF records are created by an import library utility, *IMPLIB*, which builds an "import library" from a module definition file or DLL.

## 88H EXPDEF—Export Definition Record (Comment Class A0, Subtype 02)

### Description

This record describes the exported names for a module.

### History

This comment class and subtype is a Microsoft extension added for Microsoft C version 5.1.

### Record Format

One exported entry point is described; the subrecord format is

| 1  | 1             | <variable>    | <variable>    | 2              |
|----|---------------|---------------|---------------|----------------|
| 02 | Exported Flag | Exported Name | Internal Name | Export Ordinal |
|    |               |               |               | <conditional>  |

where:

**02** Identifies the subtype as an EXPDEF.

**Exported Flag** Is a bit-significant 8-bit field with the following format:

| <pre>&lt;-------------------------------- 1 byte --------------------------------&gt;</pre> |               |         |                                                               |
|---------------------------------------------------------------------------------------------|---------------|---------|---------------------------------------------------------------|
| Ordinal Bit                                                                                 | Resident Name | No Data | Parm Count                                                    |
| 1                                                                                           | 1             | 1       | <pre>&lt;----------------- 5 bits -----------------&gt;</pre> |

**Ordinal Bit** Is set if the item is exported by ordinal; in this case the Export Ordinal field is present.

**Resident Name** Is set if the exported name is to be kept resident by the system loader; this is an optimization for frequently used items imported by name.

**No Data** Is set if the entry point does not use initialized data (either instanced or global).

**Parm Count** Is the number of parameter words. The Parm Count field is set to 0 for all but callgates to 16-bit segments.

**Exported Name** Is in *count, char* string format. Name to be used when the entry point is imported by name.

**Internal Name** Is in *count, char* string format. If the name length is 0, the internal name is the same as the Exported Name field. Otherwise, it is the name by which the entry point is known within this module. This name will appear as a PUBDEF or LPUBDEF name.

**Export Ordinal** Is present if the Ordinal Bit field is set; it is a 16-bit numeric field whose value is the ordinal used (must be nonzero).

**Note:** *EXPDEFs are produced by many compilers when the keyword `_export` is used in a source file.*

## 88H INCDEF—Incremental Compilation Record (Comment Class A0, Subtype 03)

### Description

This record is used for incremental compilation. Every FIXUPP and LINNUM record following an INCDEF record will adjust all external index values and line number values by the appropriate delta. The deltas are cumulative if there is more than one INCDEF record per module.

### History

This comment class subtype is a Microsoft extension added for Microsoft QuickC version 2.0.

### Record Format

The subrecord format is:

| 1  | 2               | 2               | <variable> |
|----|-----------------|-----------------|------------|
| 03 | EXTDEF<br>Delta | LINNUM<br>Delta | Padding    |

The EXTDEF Delta and LINNUM Delta fields are signed.

Padding (zeros) is added by Microsoft QuickC to allow for expansion of the object module during incremental compilation and linking.

**Note:** Negative deltas are allowed.

## 88H LNKDIR—Microsoft C++ Directives Record (Comment Class A0, Subtype 05)

### Description

This record is used by the compiler to pass directives and flags to the linker.

### History

This comment class and subtype is a Microsoft extension added for Microsoft C 7.0.

### Record Format

The subrecord format is:

| 1  | 1         | 1                  | 1                |
|----|-----------|--------------------|------------------|
| 05 | Bit Flags | Pseudocode Version | CodeView Version |

#### Bit Flags Field

The format of the Bit Flags byte is:

| 8  | 1 | 1 | 1 | 1 | 1 | 1       | 1                       | 1 (bits) |
|----|---|---|---|---|---|---------|-------------------------|----------|
| 05 | 0 | 0 | 0 | 0 | 0 | Run MPC | Omit CodeView \$PUBLICS | New .EXE |

The low-order bit, if set, indicates that the linker should output the new .EXE format; this flag is ignored for all but linking of pseudocode (p-code) applications. (Pseudocode requires a segmented executable.)

The second low-order bit indicates that the linker should not output the \$PUBLICS subsection of the Microsoft symbol and type (CodeView) information.

The third low-order bit indicates the need to run the Microsoft Make Pseudocode Utility (MPC) over the object file to enable creation of an executable file.

#### Pseudocode Version Field

This is a one-byte field indicating the pseudocode interpreter version number.

#### CodeView Version Field

This is a one-byte field indicating the CodeView version number.

**Note:** The presence of this record in an object module will indicate the presence of global symbols records. The linker will not emit a \$PUBLICS section for those modules with this comment record and a \$SYMBOLS section.

## 88H LIBMOD—Library Module Name Record (Comment Class A3)

### Description

The LIBMOD comment record is used only by the librarian not by the linker. It gives the name of an object module within a library, allowing the librarian to preserve the source filename in the THEADR record and still identify the module names that make up the library. Since the module name is the base name of the .OBJ file that was built into the library, it may be completely different from the final library name.

### History

This comment class and subtype is a Microsoft extension added for LIB version 3.07 in version 5.0 of its macro assembler (MASM).

### Record Format

The subrecord format is:

| 1  | <variable>  |
|----|-------------|
| A3 | Module Name |

The record contains only the ASCII string of the module name, in *count, char* format. The module name has no path and no extension, just the base of the module name.

### Notes

*Microsoft LIB adds a LIBMOD record when an .OBJ file is added to a library and strips the LIBMOD record when an .OBJ file is removed from a library, so typically this record exists only in .LIB files.*

*There will be one LIBMOD record in the library file for each object module that was combined to build the library.*

*IBM LINK386 ignores LIBMOD comment records.*

## 88H EXESTR—Executable String Record (Comment Class A4)

### Description

The EXESTR comment record implements these ANSI and XENIX/UNIX features in Microsoft C:

```
#pragma comment(exestr, <char-sequence>)  
#ident string
```

### History

This comment class and subtype is a Microsoft extension added for Microsoft C 5.1.

### Record Format

The subrecord format is:

| 1  | <variable>     |
|----|----------------|
| A4 | Arbitrary Text |

The linker will copy the text in the Arbitrary Text field byte for byte to the end of the executable file. The text will not be included in the program load image.

### Notes

*If Microsoft symbol and type information is present, the text will not be at the end of the file but somewhere before so as not to interfere with the Microsoft symbol and type information signature.*

*There is no limit to the number of EXESTR comment records.*

## 88H INCERR—Incremental Compilation Error (Comment Class A6)

### Description

This comment record will cause the linker to terminate with a fatal error similar to "invalid object—error encountered during incremental compilation."

This behavior is useful when an incremental compilation fails and the user tries to link manually. The object module cannot be deleted, in order to preserve the base for the next incremental compilation.

### History

This comment class and subtype is a Microsoft extension added for Microsoft QuickC 2.0.

### Record Format

The subrecord format is:

| 1  |           |
|----|-----------|
| A6 | No Fields |

## 88H NOPAD—No Segment Padding (Comment Class A7)

### Description

This comment record identifies a set of segments that are to be excluded from the padding imposed with the /PADDATA or /PADCODE options.

### History

This comment class and subtype is a Microsoft extension added for COBOL. It was added to Microsoft LINK to support MicroFocus COBOL version 1.2; it was added permanently in LINK version 5.11 to support Microsoft COBOL version 3.0.

### Record Format

The subrecord format is:

| 1  | 1 or 2                                       |
|----|----------------------------------------------|
| A7 | SEGDEF Index                                 |
|    | <-----------------repeated-----------------> |

The SEGDEF Index field is the standard OMF index type of 1 or 2 bytes. It may be repeated.

**Note:** IBM LINK386 ignores NOPAD comment records.

## 88H WKEXT—Weak Extern Record (Comment Class A8)

### Description

This record marks a set of external names as "weak," and for every weak extern, the record associates another external name to use as the default resolution.

### History

This comment class and subtype is a Microsoft extension added for Microsoft Basic version 7.0. There is no construct in Microsoft Basic that produces it, but the record type is manually inserted into Microsoft Basic library modules.

The first user-accessible construct to produce a weak extern was added for Microsoft MASM version 6.0.

See the following "Notes" section for details on how and why this record is used in Microsoft's Basic and MASM.

### Record Format

The subrecord format is:

| 1  | 1 or 2            | 1 or 2                          |
|----|-------------------|---------------------------------|
| A8 | Weak EXTDEF Index | Default Resolution EXTDEF Index |

<----------------repeated------------------>

The Weak EXTDEF Index field is the 1- or 2-byte index to the EXTDEF of the extern that is weak.

The Default Resolution EXTDEF Index field is the 1- or 2-byte index to the EXTDEF of the extern that will be used to resolve the extern if no "stronger" link is found to resolve it.

### Notes

*There are two ways to cancel the "weakness" of a weak extern; both result in the extern becoming a "strong" extern (the same as an EXTDEF). They are:*

- *If a PUBDEF for the weak extern is linked in*
- *If an EXTDEF for the weak extern is found in another module (including libraries)*

*If a weak extern becomes strong, then it must be resolved with a matching PUBDEF, just like a regular EXTDEF. If a weak extern has not become strong by the end of the linking process, then the default resolution is used.*

*If two weak externs for the same symbol in different modules have differing default resolutions, many linkers will emit a warning.*

*Weak externs do not query libraries for resolution; if an extern is still weak when libraries are searched, it stays weak and gets the default resolution. However, if a library module is linked in for other reasons (say, to resolve strong externs) and there are EXTDEFS for symbols that were weak, the symbols become strong.*

### Example

Assume that there is a weak extern for "var" with a default resolution name of "con". If there is a PUBDEF for "var" in some library module that would not otherwise be linked in, then the library module is not linked in, and any references to "var" are resolved to "con". However, if the library module is linked in for other reasons—for example, to resolve references to a strong extern named "bletch"— then "var" will be resolved by the PUBDEF from the library, not to the default resolution "con".

WKEXTs are best understood by explaining why they were added in the first place. The minimum BASIC run-time library in the past consisted of a large amount of code that was always linked in, even for the smallest program. Most of this code was never called directly by the user, but it was called indirectly from other routines in other libraries, so it had to be linked in to resolve the external references.

For instance, the floating-point library was linked in even if the user's program did not use floating-point operations, because the PRINT library routine contained calls to the floating-point library for support to print floating-point numbers.

The solution was to make the function calls between the libraries into weak externals, with the default resolution set to a small stub routine. If the user never used a language construct or feature that needed the additional library support, then no strong extern would be generated by the compiler and the default resolution (to the stub routine) would be used. However, if the user accessed the library's routines or used constructs that required the library's support, a strong extern would be generated by the compiler to cancel the effect of the weak extern, and the library module would be linked in. This required that the compiler know a lot about which libraries are needed for which constructs, but the resulting executable was much smaller.

#### Note:

*The construct in Microsoft MASM 6.0 that produces a weak extern is*

*EXTERN var(con): byte*

*which makes "con" the default resolution for weak extern "var".*

## 88H LZEXT—Lazy Extern Record (Comment Class A9)

### Description

This record marks a set of external names as "lazy," and for every lazy extern, the record associates another external name to use as the default resolution.

### History

This comment class and subtype is a Microsoft extension added for Microsoft C 7.0, but was not implemented in the Microsoft C 7.0 linker.

### Record Format

The subrecord format is:

| 1  | 1 or 2            | 1 or 2                          |
|----|-------------------|---------------------------------|
| A9 | Lazy EXTDEF Index | Default Resolution EXTDEF Index |

<----------------repeated------------------>

The Lazy EXTDEF Index field is the 1- or 2-byte index to the EXTDEF of the extern that is lazy.

The Default Resolution EXTDEF Index field is the 1- or 2-byte index to the EXTDEF of the extern that will be used to resolve the extern if no "stronger" link is found to resolve it.

### Notes

*There are two ways to cancel the "laziness" of a lazy extern; both result in the extern becoming a "strong" extern (the same as an EXTDEF.) They are:*

- *If a PUBDEF for the lazy extern is linked in*
- *If an EXTDEF for the lazy extern is found in another module (including libraries)*

*If a lazy extern becomes strong, it must be resolved with a matching PUBDEF, just like a regular EXTDEF. If a lazy extern has not become strong by the end of the linking process, then the default resolution is used.*

*If two weak externs for the same symbol in different modules have differing default resolutions, many linkers will emit a warning.*

*Unlike weak externs, lazy externs do query libraries for resolution; if an extern is still lazy when libraries are searched, it stays lazy and gets the default resolution.*

*IBM LINK386 ignores LZEXT comment records.*

## 8AH or 8BH MODEND—Module End Record

### Description

The MODEND record denotes the end of an object module. It also indicates whether the object module contains the main routine in a program, and it can optionally contain a reference to a program's entry point.

### History

Record type 8BH is was added for 32-bit linkers; it has a Target Displacement field of 32 bits rather than 16 bytes.

### Record Format

| 1              | 2                | 1              | 1        | 1 or 2         | 1 or 2          | 2 or 4                 | 1        |
|----------------|------------------|----------------|----------|----------------|-----------------|------------------------|----------|
| 8A<br>or<br>8B | Record<br>Length | Module<br>Type | End Data | Frame<br>Datum | Target<br>Datum | Target<br>Displacement | Checksum |

<----------------Start Address subfield, conditional------------------>

where:

#### Module Type Field

The Module Type byte is bit significant; its layout is

| MATTR<br>Main               | Start | Segment<br>Bit | 0 | 0 | 0 | 0 | X |
|-----------------------------|-------|----------------|---|---|---|---|---|
| <----------2 bits---------> |       |                |   |   |   |   |   |

where:

**MATTR** Is a 2-bit field.

**Main** Is set if the module is a main program module.

**Start** Is set if the module contains a start address; if this bit is set, the field starting with the End Data byte is present and specifies the start address.

**Segment Bit** Is reserved. Only 0 is supported by MS-DOS and OS/2.

**X** Is set if the Start Address subfield contains a relocatable address reference that the linker must fix up. (The original Intel 8086 specification allows this bit to be 0, to indicate that the start address is an absolute physical address that is stored as a 16-bit frame number and 16-bit offset, but this capability is not supported by certain linkers. This bit should always be set; however, the value will be ignored.)

#### Start Address

The Start Address subfield is present only if the Start bit in the Module Type byte is set. Its format is identical to the Fix Data, Frame Datum, Target Datum, and Target Displacement fields in a FIXUP subrecord of a FIXUPP record. Bit 2 of the End Data field, which corresponds to the P bit in a Fix Data field, must be 0. The Target Displacement field (if present) is a 4-byte field if the record type is 8BH and a 2-byte field otherwise. This value provides the initial contents of CS:(E)IP.

If overlays are used, the start address must be given in the MODEND record of the root module.

### Notes

*A MODEND record can appear only as the last record in an object module.*

*It is assumed that the Link Pass Separator comment record (COMENT A2, subtype 01) will not be present in a module whose MODEND record contains a program starting address. If there are overlays, the linker needs to see the starting address on Pass 1 to define the symbol \$\$MAIN.*

### Example

Consider the MODEND record of a simple HELLO.ASM program:

|      | 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  | A | B | C | D | E | F |
|------|----|----|----|----|----|----|----|----|----|----|---|---|---|---|---|---|
| 0000 | 8A | 07 | 00 | C1 | 00 | 01 | 01 | 00 | 00 | AC | . | . | . | . | . | . |

Byte 00H contains 8AH, indicating a MODEND record.

Bytes 01-02H contain 0007H, the length of the remainder of the record.

Byte 03H contains 0C1H (11000001B). Bit 7 is set to 1, indicating that this module is the main module of the program. Bit 6 is set to 1, indicating that a Start Address subfield is present. Bit 0 is set to 1, indicating that the address referenced in the Start Address subfield must be fixed up by the linker.

Byte 04H (End Data in the Start Address subfield) contains 00H. As in a FIXUPP record, bit 7 indicates that the frame for this fixup is specified explicitly, and bits 6 through 4 indicate that a SEGDEF index specifies the frame. Bit 3 indicates that the target reference is also specified explicitly, and bits 2 through 0 indicate that a SEGDEF index also specifies the target.

Byte 05H (Frame Datum in the Start Address subfield) contains 01H. This is a reference to the first SEGDEF record in the module, which in this example corresponds to the\_TEXT segment. This reference tells the linker that the start address lies in the\_TEXT segment of the module.

Byte 06H (Target Datum in the Start Address subfield) contains 01H. This also is a reference to the first SEGDEF record in the object module, which corresponds to the \_TEXT segment. For example, Microsoft LINK uses the following Target Displacement field to determine where in the \_TEXT segment the address lies.

Bytes 07-08H (Target Displacement in the Start Address subfield) contain 0000H. This is the offset (in bytes) of the start address.

Byte 09H contains the Checksum field, 0ACH.

## 8CH EXTDEF—External Names Definition Record

### Description

The EXTDEF record contains a list of symbolic external references—that is, references to symbols defined in other object modules. The linker resolves external references by matching the symbols declared in EXTDEF records with symbols declared in PUBDEF records.

### History

In the Intel specification and older linkers, the Type Index field was used as an index into TYPDEF records. This is no longer true; the field now encodes Microsoft symbol and type information (see Appendix 1 for details.) Many linkers ignore the old style TYPDEF.

### Record Format

| 1  | 2             | 1             | <String Length>      | 1 or 2     | 1        |
|----|---------------|---------------|----------------------|------------|----------|
| 8C | Record Length | String Length | External Name String | Type Index | Checksum |

This record provides a list of unresolved references, identified by name and with optional associated type information. The external names are ordered by occurrence jointly with the COMDEF and LEXTDEF records, and referenced by an index in other records (FIXUPP records); the name may not be null. Indexes start from 1.

String Length is a 1-byte field containing the length of the name field that follows it.

The Type Index field is encoded as an index field and contains debug information.

### Notes

*For Microsoft compilers, all referenced functions of global scope and all referenced variables explicitly declared "extern" will generate an EXTDEF record.*

*Many linkers impose a limit of 1023 external names and restrict the name length to a value between 1 and 7FH.*

*Any EXTDEF records in an object module must appear before the FIXUPP records that reference them.*

*Resolution of an external reference is by name match (case sensitive) and symbol type match. The search looks for a matching name in the following sequence:*

1. *Searches PUBDEF and COMDEF records.*
2. *If linking a segmented executable, searches imported names (IMPDEF).*
3. *If linking a segmented executable and not a DLL, searches for an exported name (EXPDEF) with the same name—a self-imported alias.*
4. *Searches for the symbol name among undefined symbols. If the reference is to a weak extern, the default resolution is used. If the reference is to a strong extern, it's an undefined external, and the linker generates an error.*

All external references must be resolved at link time (using the above search order). Even though the linker produces an executable file for an unsuccessful link session, an error bit is set in the header that prevents the loader from running the executable.

### Example

Consider this EXTDEF record generated by the Microsoft C Compiler:

```
0 1 2 3 4 5 6 7 8 9 A B C D E F
0000 8C 25 00 0A 5F 5F 61 63 72 74 75 73 65 64 00 05    .%._acrtused..
0010 5F 6D 61 69 6E 00 05 5F 70 75 74 73 00 08 5F 5F    _main.puts..__
0020 63 68 6B 73 74 6B 00 A5                                            chkstk..
```

Byte 00H contains 8CH, indicating that this is an EXTDEF record.

Bytes 01-02H contain 0025H, the length of the remainder of the record.

Bytes 03-26H contain a list of external references. The first reference starts in byte 03H, which contains 0AH, the length of the name `_acrtused`. The name itself follows in bytes 04-0DH. Byte 0EH contains 00H, which indicates that the symbol's type is not defined by any TYPDEF record in this object module. Bytes 0F-26H contain similar references to the external symbols `_main`, `_puts`, and `_chkstk`.

Byte 27H contains the Checksum field, 0A5H.
