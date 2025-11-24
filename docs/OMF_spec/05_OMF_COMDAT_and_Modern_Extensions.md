## C2H or C3H COMDAT—Initialized Communal Data Record

### Description

The purpose of the COMDAT record is to combine logical blocks of code and data that may be duplicated across a number of compiled modules.

### History

The record is an extension to the original set of 8086 object record types. It was added for Microsoft C 7.0.

### Record Format

| 1        | 2             | 1     | 1          | 1     | 2 or 4                 | 1 or 2     | 1 or 2      | 1 or 2 <sup>[1]</sup>            | 1          | 1        |
|----------|---------------|-------|------------|-------|------------------------|------------|-------------|----------------------------------|------------|----------|
| C2 or C3 | Record Length | Flags | Attributes | Align | Enumerated Data Offset | Type Index | Public Base | Public Name <var> <sup>[2]</sup> | Data       | Checksum |
|          |               |       |            |       |                        |            |             |                                  | <repeated> |          |

#### Flags Field

This field contains the following defined bits:

| <b>01H</b> | Continuation bit. If clear, this COMDAT record establishes a new instance of the COMDAT variable; otherwise, the data is a continuation of the previous COMDAT of the symbol. |
|------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <b>02H</b> | Iterated data bit. If clear, the Data field contains enumerated data; otherwise, the Data field contains iterated data, as in an LIDATA record.                               |
| <b>04H</b> | Local bit (effectively an "LCOMDAT"). This is used in preference to LLNAMES.                                                                                                  |
| <b>08H</b> | Data in code segment. If the application is overlaid, this COMDAT must be forced into the root text. Also, do not apply FARCALLTRANSLATION to this COMDAT.                    |

*Note: This flag bit is not supported by IBM LINK386.*

#### Attributes Field

This field contains two 4-bit fields: the Selection Criteria to be used and the Allocation Type, which is an ordinal specifying the type of allocation to be performed. Values are:

##### Selection Criteria (High-Order 4 Bits):

| Bit        | Selection Criteria |                                                                                                  |
|------------|--------------------|--------------------------------------------------------------------------------------------------|
| <b>00H</b> | No match           | Only one instance of this COMDAT allowed.                                                        |
| <b>10H</b> | Pick Any           | Pick any instance of this COMDAT.                                                                |
| <b>20H</b> | Same Size          | Pick any instance, but instances must have the same length or the linker will generate an error. |

| 30H       | Exact Match | Pick any instance, but checksums of the instances must match or the linker will generate an error. Fixups are ignored. |
|-----------|-------------|------------------------------------------------------------------------------------------------------------------------|
| 40H – F0H | Reserved.   |                                                                                                                        |

##### Allocation Type (Low-Order 4 bits):

| Bit       | Allocation |                                                                                                   |
|-----------|------------|---------------------------------------------------------------------------------------------------|
| 00H       | Explicit   | Allocate in the segment specified in the ensuing Base Group, Base Segment, and Base Frame fields. |
| 01H       | Far Code   | Allocate as CODE16. The linker will create segments to contain all COMDATs of this type.          |
| 02H       | Far Data   | Allocate as DATA16. The linker will create segments to contain all COMDATs of this type.          |
| 03H       | Code32     | Allocate as CODE32. The linker will create segments to contain all COMDATs of this type.          |
| 04H       | Data32     | Allocate as DATA32. The linker will create segments to contain all COMDATs of this type.          |
| 05H - 0FH | Reserved.  |                                                                                                   |

#### Align Field

These codes are based on the ones used by the SEGDEF record:

| 0 | Use value from SEGDEF                                                                                                  |
|---|------------------------------------------------------------------------------------------------------------------------|
| 1 | Byte aligned                                                                                                           |
| 2 | Word aligned                                                                                                           |
| 3 | Paragraph (16 byte) aligned                                                                                            |
| 4 | Page aligned. (The original Intel specification uses 256-byte pages, the IBM OMF implementation uses 4096-byte pages.) |
| 5 | Double word (4 byte) aligned                                                                                           |
| 6 | Not defined                                                                                                            |
| 7 | Not defined                                                                                                            |

#### Enumerated Data Offset Field

This field specifies an offset relative to the beginning location of the symbol specified in the Public Name Index field and defines the relative location of the first byte of the Data field. Successive data bytes in the Data field occupy higher locations of memory. This works very much like the Enumerated Data Offset field in an LEDATA record, but instead of an offset relative to a segment, this is relative to the beginning of the COMDAT symbol.

#### Type Index Field

The Type Index field is encoded in index format; it contains either debug information or an old-style TYPDEF index. If this index is 0, there is no associated type data. Old-style TYPDEF indexes are ignored by most linkers. Linkers do not perform type checking.

#### Public Base Field

This field is conditional and is identical to the public base fields (Base Group, Base Segment, and Base Frame) stored in the PUBDEF record. This field is present only if the Allocation Type field specifies Explicit allocation.

#### Public Name Field

[1] Microsoft LINK recognizes this field as a regular logical name index (1 or 2 bytes).

[2] IBM LINK386 recognizes this field as a regular length-prefixed name.

#### Data Field

The Data field provides up to 1024 consecutive bytes of data. If there are fixups, they must be emitted in a FIXUPP record that follows the COMDAT record. The data can be either enumerated or iterated, depending on the Flags field.

### Notes

*Record type C3H has an Enumerated Data Offset field of 32 bits.*

*While creating addressing frames, most linkers add the COMDAT data to the appropriate logical segments, adjusting their sizes. At that time, the offset at which the data that goes inside the logical segment is calculated. Next, the linker creates physical segments from adjusted logical segments and reports any 64K boundary overflows.*

*If the allocation type is not explicit, COMDAT code and data is accumulated by the linker and broken into segments, so that the total can exceed 64K.*

*In Pass 2, only the selected occurrence of COMDAT data will be stored in virtual memory, fixed, and later written into the .EXE file.*

*COMDATs are allocated in the order of their appearance in the .OBJ files if no explicit ordering is given.*

*A COMDAT record cannot be continued across modules. A COMDAT record can be duplicated in a single module.*

*If any COMDAT record on a given symbol has the local bit set, all COMDAT records on that symbol have that bit set.*

## C4H or C5H LINSYM—Symbol Line Numbers Record

### Description

This record will be used to output line numbers for functions specified through COMDAT records. Each LINSYM record is associated with a preceding COMDAT record.

### History

This record is an extension to the original set of 8086 object record types. It was added for Microsoft C 7.0.

### Record Format

| 1              | 2                | 1     | 1 or 2 [1]<br><var> [2]        | 2              | 2 or 4                   | 1        |
|----------------|------------------|-------|--------------------------------|----------------|--------------------------|----------|
| C4<br>or<br>C5 | Record<br>Length | Flags | Public<br>Name                 | Line<br>Number | Line<br>Number<br>Offset | Checksum |
|                |                  |       | <----------repeated----------> |                |                          |          |

#### Flags Field

This field contains one defined bit:

**01H** Continuation bit. If clear, this COMDAT record establishes a new instance of the COMDAT variable; otherwise, the data is a continuation of the previous COMDAT of the symbol.

#### Public Name Field

[1] Microsoft LINK recognizes this field as a regular logical name index indicating the name of the base of the LINSYM record.

[2] IBM LINK386 recognizes this field as a length-preceded name indicating the name of the base of the LINSYM record.

#### Line Number Field

An unsigned number in the range 0 to 65,535.

#### Line Number Offset Field

The offset relative to the base specified by the symbol name base. The size of this field depends on the record type.

### Notes

*Record type C5H is identical to C4H except that the Line Number Offset field is 4 bytes instead of 2.*

*This record is used to output line numbers for functions specified through COMDAT records. Often, the residing segment as well as the relative offsets of such functions is unknown at compile time, in that the linker is the final arbiter of such information. For such cases, most compilers will generate this record to specify the line number/offset pairs relative to a symbolic name.*

###### Relocatable Object Module Format

*This record will also be used to discard duplicate LINNUM information. If the linker encounters two or more LINSYM records with matching symbolic names (corresponding to multiple COMDAT records with the same name), the linker will keep the one that corresponds to the retained COMDAT.*

*LINSYM records must follow the COMDATs to which they refer. A LINSYM on a given symbol refers to the most recent COMDAT on the same symbol. LINSYMs inherit the "localness" of their COMDATs.*

## C6H ALIAS—Alias Definition Record

### Description

This record has been introduced to support link-time aliasing, a method by which compilers or assemblers may direct the linker to substitute all references to one symbol for another.

### History

The record is an extension to the original set of 8086 object record types for FORTRAN version 5.1 (Microsoft LINK version 5.13).

### Record Format

| 1  | 2             | <variable>                     | <variable>      | 1        |
|----|---------------|--------------------------------|-----------------|----------|
| C6 | Record Length | Alias Name                     | Substitute Name | Checksum |
|    |               | <----------repeated----------> |                 |          |

#### Alias Name Field

A regular length-preceded name of the alias symbol.

#### Substitute Name Field

A regular length-preceded name of the substitute symbol.

### Notes

*This record consists of two symbolic names: the alias symbol and the substitute symbol. The alias symbol behaves very much like a PUBDEF in that it must be unique. If a PUBDEF of an alias symbol is encountered later, the PUBDEF overrides the alias. If another ALIAS record with a different substitute symbol is encountered, a warning is emitted by most linkers, and the second substitute symbol is used.*

*When attempting to satisfy an external reference, if an ALIAS record whose alias symbol matches is found, the linker will halt the search for alias symbol definitions and will attempt to satisfy the reference with the substitute symbol.*

*All ALIAS records must appear before the Link Pass 2 record.*

## C8H or C9H NBKPAT—Named Backpatch Record

### Description

The Named Backpatch record is similar to a BAKPAT record, except that it refers to a COMDAT record by logical name index rather than an LIDATA or LEDATA record. NBKPAT records must immediately follow the COMDAT/FIXUPP block to which they refer.

### History

This record is an extension to the original set of 8086 object record types. It was added for Microsoft C 7.0.

### Record Format

| 1           | 2                | 1                | 1 or 2 <sup>[1]</sup><br><var> <sup>[2]</sup> | 2 or 4 | 2 or 4 | 1        |
|-------------|------------------|------------------|-----------------------------------------------|--------|--------|----------|
| C8<br>or C9 | Record<br>Length | Location<br>Type | Public<br>Name                                | Offset | Value  | Checksum |
|             |                  |                  | <-------repeated-------->                     |        |        |          |

#### Location Type Field

*Type of location to be patched; the only valid values are:*

| 0 | 8-bit byte                               |
|---|------------------------------------------|
| 1 | 16-bit word                              |
| 2 | 32-bit double word, record type C9H only |

#### Public Name Field

[1] Microsoft LINK recognizes this field as a regular logical name index of the COMDAT record to be back patched.

[2] IBM LINK386 recognizes this field as a length-preceded name of the COMDAT record to be back patched.

#### Offset and Value Fields

These fields are 32 bits for record type C8H, 16 bits for C9H.

The Offset field specifies the location to be patched, as an offset into the COMDAT.

The associated Value field is added to the location being patched (unsigned addition, ignoring overflow). The Value field is a fixed length (16 bits or 32 bits, depending on the record type) to make object module processing easier.

## CAH LLNAMES—Local Logical Names Definition Record

### Description

The LLNAMES record is a list of local names that can be referenced by subsequent SEGDEF and GRPDEF records in the object module.

The names are ordered by their occurrence, with the names in LNAMES records and referenced by index from subsequent records. More than one LNAMES and LLNAMES record may appear. The names themselves are used as segment, class, group, overlay, COMDAT, and selector names.

### History

This record is an extension to the original set of 8086 object record types. It was added for Microsoft C 7.0.

### Record Format

| 1  | 2             | 1                                            | <----String Length-----> | 1        |
|----|---------------|----------------------------------------------|--------------------------|----------|
| CA | Record Length | String Length                                | Name String              | Checksum |
|    |               | <-----------------repeated-----------------> |                          |          |

Each name appears in *count, char* format, and a null name is valid. The character set is ASCII. Names can be up to 255 characters long.

### Notes

*Any LLNAMES records in an object module must appear before the records that refer to them.*

*Previous versions limited the name string length to 254 characters.*

## CCH VERNUM - OMF Version Number Record

### Description

The VERNUM record contains the version number of the object format generated. The version number is used to identify what version of the TIS-sponsored OMF was generated.

### History

This is a new record that was approved by the Tool Interface Standards (TIS) Committee, an open industry standards body.

### Record Format

| 1  | 2             | 1              | <---String Length---> | 1        |
|----|---------------|----------------|-----------------------|----------|
| CC | Record Length | Version Length | Version String        | Checksum |

The version string consists of 3 numbers separated by periods (.) as follows:

<TIS Version Base>.<Vendor Number>.<Version>

The TIS Version Base is the base version of the OMF being used. This number is provided by the TIS Committee. The Vendor Number is assigned by TIS to allow extensions specific to a vendor. Finally, the Version is the Vendor-specific version. A Vendor Number or Version of zero (0) is reserved for TIS. For example, a version string of 1.0.0 indicates a TIS compliant version of the OMF without vendor additions.

## CEH VENDEXT - Vendor-specific OMF Extension Record

### Description

The VENDEXT record allows vendor-specific extensions to the OMF. All vendor-specific extensions use this record.

### History

This is a new record that was approved by the Tool Interface Standards (TIS) Committee, an open industry standards body.

### Record Format

| 1  | 2             | 2             | <from record length> | 1        |
|----|---------------|---------------|----------------------|----------|
| CE | Record Length | Vendor Number | Extension Bytes      | Checksum |

The Vendor Number is assigned by the TIS Committee. Zero (0) is reserved. The Extension Bytes provide OMF extension information.
