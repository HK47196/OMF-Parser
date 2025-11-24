## 90H or 91H PUBDEF—Public Names Definition Record

### Description

The PUBDEF record contains a list of public names. It makes items defined in this object module available to satisfy external references in other modules with which it is bound or linked.

The symbols are also available for export if so indicated in an EXPDEF comment record.

### History

Record type 91H was added for 32-bit linkers; it has a Public Offset field of 32 bits rather than 16 bits.

### Record Format

| 1              | 2                | 1 or 2                 | 1 or 2                   | 2             | 1                              | <String Length>       | 2 or 4           | 1 or 2        | 1        |
|----------------|------------------|------------------------|--------------------------|---------------|--------------------------------|-----------------------|------------------|---------------|----------|
| 90<br>or<br>91 | Record<br>Length | Base<br>Group<br>Index | Base<br>Segment<br>Index | Base<br>Frame | String<br>Length               | Public<br>Name String | Public<br>Offset | Type<br>Index | Checksum |
|                |                  |                        |                          | <conditional> | <----------repeated----------> |                       |                  |               |          |

#### Base Group, Base Segment, and Base Frame Fields

The Base Group and Base Segment fields contain indexes specifying previously defined SEGDEF and GRPDEF records. The group index may be 0, meaning that no group is associated with this PUBDEF record.

The Base Frame field is present only if the Base Segment field is 0, but the contents of the Base Frame field are ignored.

The Base Segment Index is normally nonzero and no Base Frame field is present.

According to the Intel 8086 specification, if both the segment and group indexes are 0, the Base Frame field contains a 16-bit paragraph (when viewed as a linear address); this may be used to define public symbols that are absolute. Absolute addressing is not fully supported by some linkers—it can be used for read-only access to absolute memory locations; however, writing to absolute memory locations may not work in some linkers.

#### Public Name String, Public Offset, and Type Index Fields

The Public Name String field is in *count, char* format and cannot be null. The maximum length of a Public Name is 255 bytes.

The Public Offset field is a 2- or 4-byte numeric field containing the offset of the location referred to by the public name. This offset is assumed to lie within the group, segment, or frame specified in the Base Group, Base Segment, or Base Frame fields.

The Type Index field is encoded in index format and contains either debug information or 0. The use of this field is determined by the OMF producer and typically provides type information for the referenced symbol.

### Notes

All defined functions and initialized global variables generate PUBDEF records in most compilers. No PUBDEF record will be generated, however, for instantiated inline functions in C++.

Any PUBDEF records in an object module must appear after the GRPDEF and SEGDEF records to which they refer. Because PUBDEF records are not themselves referenced by any other type of object record, they are generally placed near the end of an object module.

Record type 90H uses 16-bit encoding of the Public Offset field, but it is zero-extended to 32 bits if applied to Use32 segments.

### Examples

The following two examples show PUBDEF records created by Microsoft's macro assembler, MASM.

The first example is the record for the statement:

```
PUBLIC GAMMA
```

The PUBDEF record is:

|      | 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  | A  | B  | C  | D  | E  | F |               |
|------|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|---|---------------|
| 0000 | 90 | 0C | 00 | 00 | 01 | 05 | 47 | 41 | 4D | 4D | 41 | 02 | 00 | 00 | F9 |   | ....GAMMA.... |

Byte 00H contains 90H, indicating a PUBDEF record.

Bytes 01-02H contain 000CH, the length of the remainder of the record.

Bytes 03-04H represent the Base Group, Base Segment, and Base Frame fields. Byte 03H (the group index) contains 0, indicating that no group is associated with the name in this PUBDEF record. Byte 04H (the segment index) contains 1, a reference to the first SEGDEF record in the object module. This is the segment to which the name in this PUBDEF record refers.

Bytes 05-0AH represent the Public Name String field. Byte 05H contains 05H (the length of the name), and bytes 06-0AH contain the name itself, GAMMA.

Bytes 0B-0CH contain 0002H, the Public Offset field. The name GAMMA thus refers to the location that is offset two bytes from the beginning of the segment referenced by the Base Group, Base Segment, and Base Frame fields.

Byte 0DH is the Type Index field. The value of the Type Index field is 0, indicating that no data type is associated with the name GAMMA.

Byte 0EH contains the Checksum field, 0F9H.

The next example is the PUBDEF record for the following absolute symbol declaration:

```
ALPHA PUBLIC ALPHA  
      EQU 1234h
```

###### Relocatable Object Module Format

The PUBDEF record is:

```
0 1 2 3 4 5 6 7 8 9 A B C D E F
0000 90 0E 00 00 00 00 00 05 41 4C 50 48 41 34 12 00 ...ALPHA4...
0010 B1
```

Bytes 03-06H (the Base Group, Base Segment, and Base Frame fields) contain a group index of 0 (byte 03H) and a segment index of 0 (byte 04H). Because both the group index and segment index are 0, a frame number also appears in the Base Group, Base Segment, and Base Frame fields. In this instance, the frame number (bytes 05-06H) also happens to be 0.

Bytes 07-0CH (the Public Name String field) contain the name ALPHA, preceded by its length.

Bytes 0D-0EH (the Public Offset field) contain 1234H. This is the value associated with the symbol ALPHA in the assembler EQU directive. If ALPHA is declared in another object module with the declaration

```
EXTRN     ALPHA : ABS
```

any references to ALPHA in that object module are fixed up as absolute references to offset 1234H in frame 0. In other words, ALPHA would have the value 1234H.

Byte 0FH (the Type Index field) contains 0.

## 94H or 95H LINNUM—Line Numbers Record

### Description

The LINNUM record relates line numbers in source code to addresses in object code.

### History

Record type 95H is added for 32-bit linkers; allowing for 32-bit debugger style-specific information.

**Note:** For instantiated inline functions in Microsoft C 7.0, line numbers are output in LINSYM records with a reference to the function name instead of the segment.

### Record Format

| 1        | 2             | 1 or 2     | 1 or 2       | <variable>                          | 1        |
|----------|---------------|------------|--------------|-------------------------------------|----------|
| 94 or 95 | Record Length | Base Group | Base Segment | Debugger Style-specific Information | Checksum |

<----------repeated---------->

#### Base Group and Base Segment Fields

The Base Group and Base Segment fields contain indexes specifying previously defined GRPDEF and SEGDEF records.

### Notes

The debugger style-specific information is indicated by comment class A1.

Although the complete Intel 8086 specification allows the Base Group and Base Segment fields to refer to a group or to an absolute segment as well as to a relocatable segment, some linkers commonly restrict references in this field to relocatable segments.

The following discussion uses the Microsoft debugger style-specific information. The debugger style-specific information field in the LINNUM record is composed as follows:

| 2           | 2 or 4             |
|-------------|--------------------|
| Line Number | Line Number Offset |

<----------------repeated---------------->

For Microsoft LINK LINNUM records, the Line Number field contains a 16-bit quantity, in the range 0 through 7FFF and is, as its name indicates, a line number in the source code. The Line Number Offset field contains a 2-byte or 4-byte quantity that gives the translated code or data's start byte in the program segment defined by the SEGDEF index (4 bytes if the record type is 95H; 2 bytes for type 94H).

The Line Number and Line Number Offset fields can be repeated, so a single LINNUM record can specify multiple line numbers in the same segment.

###### Relocatable Object Module Format

Line Number 0 has a special meaning: it is used for the offset of the first byte after the end of the function. This is done so that the length of the last line (in bytes) can be determined.

The source file corresponding to a line number group is determined from the THEADR record.

Any LINNUM records in an object module must appear after the SEGDEF records to which they refer. Because LINNUM records are not themselves referenced by any other type of object record, they are generally placed near the end of an object module.

Also see the INCDEF record which is used to maintain line numbers after incremental compilation.

### Example

The following LINNUM record was generated by the Microsoft C Compiler:

|      | 0  | 1  | 2                | 3  | 4  | 5  | 6  | 7  | 8  | 9  | A  | B  | C  | D  | E  | F  |
|------|----|----|------------------|----|----|----|----|----|----|----|----|----|----|----|----|----|
| 0000 | 94 | 0F | 00               | 00 | 01 | 02 | 00 | 00 | 00 | 03 | 00 | 08 | 00 | 04 | 00 | 0F |
| 0010 | 00 | 3C | ................ |    |    |    |    |    |    |    |    |    |    |    |    |    |

Byte 00H contains 94H, indicating that this is a LINNUM record.

Bytes 01-02H contain 000FH, the length of the remainder of the record.

Bytes 03-04H represent the Base Group and Base Segment fields. Byte 03H (the Base Group field) contains 00H, as it must. Byte 04H (the Base Segment field) contains 01H, indicating that the line numbers in this LINNUM record refer to code in the segment defined in the first SEGDEF record in this object module.

Bytes 05-06H (the Line Number field) contain 0002H, and bytes 07-08H (the Line Number Offset field) contain 0000H. Together, they indicate that source-code line number 0002 corresponds to offset 0000H in the segment indicated in the Base Group and Base Segment fields.

Similarly, the two pairs of Line Number and Line Number Offset fields in bytes 09-10H specify that line number 0003 corresponds to offset 0008H and that line number 0004 corresponds to offset 000FH.

Byte 11H contains the Checksum field, 3CH.

## 96H LNAMES—List of Names Record

### Description

The LNAMES record is a list of names that can be referenced by subsequent SEGDEF and GRPDEF records in the object module.

The names are ordered by occurrence and referenced by index from subsequent records. More than one LNAMES record may appear. The names themselves are used as segment, class, group, overlay, and selector names.

### History

This record has not changed since the original Intel 8086 OMF specification.

### Record Format

| 1                                                | 2             | <---String Length---> |             | 1        |
|--------------------------------------------------|---------------|-----------------------|-------------|----------|
| 96                                               | Record Length | String Length         | Name String | Checksum |
| < ------------------repeated------------------ > |               |                       |             |          |

Each name appears in *count*, *char* format, and a null name is valid. The character set is ASCII. Names can be up to 255 characters long.

### Notes

*Any LNAMES records in an object module must appear before the records that refer to them. Because it does not refer to any other type of object record, an LNAMES record usually appears near the start of an object module.*

*Previous versions limited the name string length to 254 characters.*

### Example

The following LNAMES record contains the segment and class names specified in all three of the following full-segment definitions:

```
_TEXT SEGMENT byte public 'CODE'  
_DATA SEGMENT word public 'DATA'  
_STACK SEGMENT para public 'STACK'
```

The LNAMES record is:

|      | 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  | A  | B  | C  | D  | E  | F  |                   |
|------|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|-------------------|
| 0000 | 96 | 25 | 00 | 00 | 04 | 43 | 4F | 44 | 45 | 04 | 44 | 41 | 54 | 41 | 05 | 53 | .%...CODE.DATA.S. |
| 0010 | 54 | 41 | 43 | 4B | 05 | 5F | 44 | 41 | 54 | 41 | 06 | 5F | 53 | 54 | 41 | 43 | TACK._DATA._STAC  |
| 0020 | 4B | 05 | 5F | 54 | 45 | 58 | 54 | 8B |    |    |    |    |    |    |    |    | K._TEXT.          |

Byte 00H contains 96H, indicating that this is an LNAMES record.

Bytes 01-02H contain 0025H, the length of the remainder of the record.

Byte 03H contains 00H, a zero-length name.

###### Relocatable Object Module Format

Byte 04H contains 04H, the length of the class name CODE, which is found in bytes 05-08H. Bytes 09-26H contain the class names DATA and STACK and the segment names \_DATA, \_STACK, and \_TEXT, each preceded by 1 byte that gives its length.

Byte 27H contains the Checksum field, 8BH.

## 98H or 99H SEGDEF—Segment Definition Record

### Description

The SEGDEF record describes a logical segment in an object module. It defines the segment's name, length, and alignment, and the way the segment can be combined with other logical segments at bind, link, or load time.

Object records that follow a SEGDEF record can refer to it to identify a particular segment. The SEGDEF records are ordered by occurrence, and are referenced by segment indexes (starting from 1) in subsequent records.

### History

Record type 99H was added for 32-bit linkers: the Segment Length field is 32 bits rather than 16 bits. There is one newly implemented alignment type (page alignment), the B bit flag of the ACBP byte indicates a segment of 4 GB, and the P bit flag of the ACBP byte is the Use16/Use32 flag.

Starting with version 2.4, Microsoft LINK ignores the Overlay Name Index field. In versions 2.4 and later, command-line parameters to Microsoft LINK, rather than information contained in object modules, determine the creation of run-time overlays.

The length does not include COMDAT records. If selected, their size is added.

### Record Format

| 1        | 2             | <variable>         | 2 or 4         | 1 or 2             | 1 or 2           | 1 or 2             | 1        |
|----------|---------------|--------------------|----------------|--------------------|------------------|--------------------|----------|
| 98 or 99 | Record Length | Segment Attributes | Segment Length | Segment Name Index | Class Name Index | Overlay Name Index | Checksum |

#### Segment Attributes Field

The Segment Attributes field is a variable-length field; its layout is:

| <---3 bits--> | <---3 bits--> | <---1 bit--> | <---1 bit--> | <---2 bytes----> | <----1 byte----> |
|---------------|---------------|--------------|--------------|------------------|------------------|
| A             | C             | B            | P            | Frame Number     | Offset           |
|               |               |              |              | <conditional>    | <conditional>    |

The fields have the following meanings:

##### A Alignment

A 3-bit field that specifies the alignment required when this program segment is placed within a logical segment. Its values are:

- 0 Absolute segment.
- 1 Relocatable, byte aligned.
- 2 Relocatable, word (2-byte, 16-bit) aligned.
- 3 Relocatable, paragraph (16-byte) aligned.

###### Relocatable Object Module Format

4 Relocatable, aligned on a page boundary. (The original Intel 8086 specification defines a page to be 256 bytes. The IBM implementation of OMF uses a 4096-byte or 4K page size).

5 Relocatable, aligned on a double word (4-byte) boundary.

6 Not supported.

7 Not defined.

The new values for 32-bit linkers are A=4 and A=5. Double word alignment is expected to be useful as 32-bit memory paths become more prevalent. Page-align is useful for certain hardware-defined items (such as page tables) and error avoidance.

**Note:** If A=0, the conditional Frame Number and Offset fields are present and indicate the starting address of the absolute segment. Microsoft LINK ignores the Offset field.

**Conflict:** The original Intel 8086 specification included additional segment-alignment values not supported by Microsoft; alignment 5 now conflicts with the following Microsoft LINK extensions:

5 "unnamed absolute portion of memory address space"

6 "load-time locatable (LTL), paragraph aligned if not part of any group"

##### C Combination

This 3-bit field describes how the linker can combine the segment with other segments. Under MS-DOS, segments with the same name and class can be combined in two ways: they can be concatenated to form one logical segment, or they can be overlapped. In the latter case, they have either the same starting address or the same ending address, and they describe a common area in memory. Values for the C field are:

0 **Private.** Do not combine with any other program segment.

1 **Reserved.**

2 **Public.** Combine by appending at an offset that meets the alignment requirement.

3 **Reserved.**

4 Same as C=2 (public).

5 **Stack.** Combine as for C=2. This combine type forces byte alignment.

6 **Common.** Combine by overlay using maximum size.

7 Same as C=2 (public).

**Conflict:** The original Intel 8086 specification lists C=1 as Common, not C=6.

##### B Big

Used as the high-order bit of the Segment Length field. If this bit is set, the segment length value must be 0. If the record type is 98H and this bit is set, the segment is exactly 64K long. If the record type is 99H and this bit is set, the segment is exactly  $2^{32}$  bytes or 4 GB long.

**P** This bit corresponds to the bit field for segment descriptors, known as the B bit for data segments and the D bit for code segments in Intel documentation.

If 0, then the segment is no larger than 64K (if data), and 16-bit addressing and operands are the default (if code). This is a Use16 segment.

If nonzero, then the segment may be larger than 64K (if data), and 32-bit addressing and operands are the default (if code). This is a Use32 segment.

**Note:** *This is the only method for defining Use32 segments in the TIS OMF.*

#### Segment Length Field

The Segment Length field is a 2- or 4-byte numeric quantity and specifies the number of bytes in this program segment. For record type 98H, the length can be from 0 to 64K; if a segment is exactly 64K, the segment length should be 0, and the B field in the ACBP byte should be 1. For record type 99H, the length can be from 0 to 4 GB; if a segment is exactly 4 GB in size, the segment length should be 0 and the B field in the ACBP byte should be 1.

#### Segment Name Index, Class Name Index, Overlay Name Index Fields

The three name indexes (Segment Name Index, Class Name Index, and Overlay Name Index) refer to names that appeared in previous LNAMES record(s). The linker ignores the Overlay Name Index field. The full name of a segment consists of the segment and class names, and segments in different object modules are normally combined according to the A and C values if their full names are identical. These indexes must be nonzero, although the name itself may be null.

The Segment Name Index field identifies the segment with a name. The name need not be unique—other segments of the same name will be concatenated onto the first segment with that name. The name may have been assigned by the programmer, or it may have been generated by a compiler.

The Class Name Index field identifies the segment with a class name (such as CODE, FAR\_DATA, or STACK). The linker places segments with the same class name into a contiguous area of memory in the run-time memory map.

The Overlay Name Index field identifies the segment with a run-time overlay. It is ignored by many linkers.

### Notes

Many linkers impose a limit of 255 SEGDEF records per object module.

Certain name/class combinations are reserved for debug information and have special significance to the linker, such as \$\$TYPES and \$\$SYMBOLS. See Appendix 1 for more information.

**Conflicts:** The TIS-defined OMF has Use16/Use32 stored as the P bit of the ACBP field. The P bit does not specify the access for the segment. For Microsoft LINK the access is specified in the .DEF file.

### Examples

The following examples of Microsoft assembler SEGMENT directives show the resulting values for the A field in the corresponding SEGDEF object record:

```
aseg SEGMENT at 400h ; A = 0
bseg SEGMENT byte public 'CODE' ; A = 1
cseg SEGMENT para stack 'STACK' ; A = 3
```

The following examples of assembler SEGMENT directives show the resulting values for the C field in the corresponding SEGDEF object record:

```
aseg SEGMENT at 400H ; C = 0
bseg SEGMENT public 'DATA' ; C = 2
cseg SEGMENT stack 'STACK' ; C = 5
dseg SEGMENT common 'COMMON' ; C = 6
```

In this first example, the segment is byte aligned:

```
     0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
0000 98 07 00 28 11 00 07 02 01 1E                  ....(.....
```

Byte 00H contains 98H, indicating that this is a SEGDEF record.

Bytes 01-02H contain 0007H, the length of the remainder of the record.

Byte 03H contains 28H (00101000B), the ACBP byte. Bits 7-5 (the A field) contain 1 (001B), indicating that this segment is relocatable and byte aligned. Bits 4-2 (the C field) contain 2 (010B), which represents a public combine type. (When this object module is linked, this segment will be concatenated with all other segments with the same name.) Bit 1 (the B field) is 0, indicating that this segment is smaller than 64K. Bit 0 (the P field) is ignored and should be 0, as it is here.

Bytes 04-05H contain 0011H, the size of the segment in bytes.

Bytes 06-08H index the list of names defined in the module's LNAMES record. Byte 06H (the Segment Name Index field) contains 07H, so the name of this segment is the seventh name in the LNAMES record. Byte 07H (the Class Name Index field) contains 02H, so the segment's class name is the second name in the LNAMES record. Byte 08H (the Overlay Name Index field) contains 1, a reference to the first name in the LNAMES record. (This name is usually null, as MS-DOS ignores it anyway.)

Byte 09H contains the Checksum field, 1EH.

The second SEGDEF record declares a word-aligned segment. It differs only slightly from the first.

```
     0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
0000 98 07 00 48 0F 00 05 03 01 01                  H......
```

Bits 7-5 (the A field) of byte 03H (the ACBP byte) contain 2 (010B), indicating that this segment is relocatable and word aligned.

Bytes 04-05H contain the size of the segment, 000FH.

Byte 06H (the Segment Name Index field) contains 05H, which refers to the fifth name in the previous LNAMES record.

Byte 07H (the Class Name Index field) contains 03H, a reference to the third name in the LNAMES record.

## 9AH GRPDEF—Group Definition Record

### Description

This record causes the program segments identified by SEGDEF records to be collected together (grouped). For OS/2, the segments are combined into a logical segment that is to be addressed through a single selector. For MS-DOS, the segments are combined within the same 64K frame in the run-time memory map.

### History

The special group name "FLAT" has been added for 32-bit linkers.

### Record Format

| 1  | 2             | 1 or 2           | 1        | 1 or 2             | 1        |
|----|---------------|------------------|----------|--------------------|----------|
| 9A | Record Length | Group Name Index | FF Index | Segment Definition | Checksum |

<---------- repeated ---------->

#### Group Name Field

The Group Name field contains an index into a previously defined LNAMES name and must be nonzero.

Groups from different object modules are combined if their names are identical.

#### Group Components

The group's components are segments, specified as indexes into previously defined SEGDEF records.

The first byte of each group component is a type field for the remainder of the component. Certain linkers require a type value of FFH and always assume that the component contains a segment index value. See the "Notes" section below for other types defined by Intel.

The component fields are usually repeated so that all the segments constituting a group can be included in one GRPDEF record.

### Notes

*Most linkers impose a limit of 31 GRPDEF records in a single object module and limit the total number of group definitions across all object modules to 31.*

*This record is frequently followed by a THREAD FIXUPP record.*

*A common grouping using the Group Definition Record would be to group the default data segments.*

*Most linkers do special handling of the pseudo-group name FLAT. All address references to this group are made as offsets from the Virtual Zero Address, which is the start of the memory image of the executable.*

###### Relocatable Object Module Format

The additional group component types defined by the original Intel 8086 specification and the fields that follow them are:

| <b>FE</b> | External Index                                           |
|-----------|----------------------------------------------------------|
| <b>FD</b> | Segment Name Index, Class Name Index, Overlay Name Index |
| <b>FB</b> | LTL Data field, Maximum Group Length, Group Length       |
| <b>FA</b> | Frame Number, Offset                                     |

None of these types are supported by Microsoft LINK or IBM LINK386.

### Example

The example of a GRPDEF record below corresponds to the following assembler directive:

```
tgroup GROUP seg1, seg2, seg3
```

The GRPDEF record is:

```
      0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
0000 9A 08 00 06 FF 01 FF 02 FF 03 55 ....U
```

Byte 00H contains 9AH, indicating that this is a GRPDEF record.

Bytes 01-02H contain 0008H, the length of the remainder of the record.

Byte 03H contains 06H, the Group Name Index field. In this instance, the index number refers to the sixth name in the previous LNAMES record in the object module. That name is the name of the group of segments defined in the remainder of the record.

Bytes 04-05H contain the first of three group component descriptor fields. Byte 04H contains the required 0FFH, indicating that the subsequent field is a segment index. Byte 05H contains 01H, a segment index that refers to the first SEGDEF record in the object module. This SEGDEF record declared the first of three segments in the group.

Bytes 06-07H represent the second group component descriptor, this one referring to the second SEGDEF record in the object module.

Similarly, bytes 08-09H are a group component descriptor field that references the third SEGDEF record.

Byte 0AH contains the Checksum field, 55H.

## 9CH or 9DH FIXUPP—Fixup Record

### Description

The FIXUPP record contains information that allows the linker to resolve (fix up) and eventually relocate references between object modules. FIXUPP records describe the LOCATION of each address value to be fixed up, the TARGET address to which the fixup refers, and the FRAME relative to which the address computation is performed.

### History

Record type 9DH was added for 32-bit linkers; it has a Target Displacement field of 32 bits rather than 16 bits, and the Location field of the Locat word has been extended to 4 bits (using the previously unused higher order S bit) to allow new LOCATION values of 9, 11, and 13.

### Record Format

| 1           | 2                | <---------------- from Record Length------------------> | 1        |
|-------------|------------------|---------------------------------------------------------|----------|
| 9C<br>or 9D | Record<br>Length | THREAD subrecord or<br>FIXUP subrecord                  | Checksum |
|             |                  | <---------------- repeated ------------------>          |          |

Each subrecord in a FIXUPP object record either defines a thread for subsequent use, or refers to a data location in the nearest previous LEDATA or LIDATA record. The high-order bit of the subrecord determines the subrecord type: if the high-order bit is 0, the subrecord is a THREAD subrecord; if the high-order bit is 1, the subrecord is a FIXUP subrecord. Subrecords of different types can be mixed within one object record.

Information that determines how to resolve a reference can be specified explicitly in a FIXUP subrecord, or it can be specified within a FIXUP subrecord by a reference to a previous THREAD subrecord. A THREAD subrecord describes only the method to be used by the linker to refer to a particular target or frame. Because the same THREAD subrecord can be referenced in several subsequent FIXUP subrecords, a FIXUPP object record that uses THREAD subrecords may be smaller than one in which THREAD subrecords are not used.

THREAD subrecords can be referenced in the same object record in which they appear and also in subsequent FIXUPP object records.

#### THREAD Subrecord

There are four FRAME threads and four TARGET threads; not all need be defined, and they can be redefined by later THREAD subrecords in the same or later FIXUPP object records. The FRAME threads are used to specify the Frame Datum field in a later FIXUP subrecord; the TARGET threads are used to specify the Target Datum field in a later FIXUP subrecord.

A THREAD subrecord does not require that a previous LEDATA or LIDATA record occur.

The layout of the THREAD subrecord is as follows:

| <---------------- 1 byte ------------------> |   |   |        |          | <---------------- 1 or 2 bytes ------------------> |
|----------------------------------------------|---|---|--------|----------|----------------------------------------------------|
| 0                                            | D | 0 | Method | Thred    | Index                                              |
| 1                                            | 1 | 1 | 3      | 2 (bits) | <---------------- conditional ------------------>  |

where:

**0** The high-order bit is 0 to indicate that this is a THREAD subrecord.

**D** Is 0 for a TARGET thread, 1 for a FRAME thread.

**Method** Is a 3-bit field.

For TARGET threads, only the lower two bits of the field are used; the high-order bit of the method is derived from the P bit in the Fix Data field of FIXUP subrecords that refer to this thread. (The full list of methods is given here for completeness.) This field determines the kind of index required to specify the Target Datum field.

**T0** Specified by a SEGDEF index.

**T1** Specified by a GRPDEF index.

**T2** Specified by a EXTDEF index.

**T3** Specified by an explicit frame number (not supported by Microsoft LINK or IBM LINK386).

**T4** Specified by a SEGDEF index only; the displacement in the FIXUP subrecord is assumed to be 0.

**T5** Specified by a GRPDEF index only; the displacement in the FIXUP subrecord is assumed to be 0.

**T6** Specified by a EXTDEF index only; the displacement in the FIXUP subrecord is assumed to be 0.

The index type specified by the TARGET thread method is encoded in the Index field.

For FRAME threads, the Method field determines the Frame Datum field of subsequent FIXUP subrecords that refer to this thread. Values for the Method field are:

**F0** The FRAME is specified by a SEGDEF index.

**F1** The FRAME is specified by a GRPDEF index.

**F2** The FRAME is specified by a EXTDEF index. Microsoft LINK and IBM LINK386 determine the FRAME from the external name's corresponding PUBDEF record in another object module, which specifies either a logical segment or a group.

**F3** Invalid. (The FRAME is identified by an explicit frame number; this is not supported by any current linker.)

**F4** The FRAME is determined by the segment index of the previous LEDATA or LIDATA record (that is, the segment in which the location is defined).

**F5** The FRAME is determined by the TARGET's segment, group, or external index.

**F6** Invalid.

**Note:** The Index field is present for FRAME methods F0, F1, and F2 only.

**Thred** A 2-bit field that determines the thread number (0 through 3, for the four threads of each kind).

**Index** A conditional field that contains an index value that refers to a previous SEGDEF, GRPDEF, or EXTDEF record. The field is present only if the thread method is 0, 1, or 2. (If method 3 were supported by the linker, the Index field would contain an explicit frame number.)

#### FIXUP Subrecord

A FIXUP subrecord gives the how/what/why/where/who information required to resolve or relocate a reference when program segments are combined or placed within logical segments. It applies to the nearest previous LEDATA or LIDATA record, which must be defined before the FIXUP subrecord. The FIXUP subrecord is as follows:

| 2     | 1             | 1 or 2        | 1 or 2        | 2 or 4              |
|-------|---------------|---------------|---------------|---------------------|
| Locat | Fix Data      | Frame Datum   | Target Datum  | Target Displacement |
|       | <conditional> | <conditional> | <conditional> |                     |

where the Locat field has an unusual format. Contrary to the usual byte order in Intel data structures, the most significant bits of the Locat field are found in the low-order byte, rather than the high-order byte, as follows:

| < low-order byte > |   |          | < high-order byte > |
|--------------------|---|----------|---------------------|
| 1                  | M | Location | Data Record Offset  |
| 1                  | 1 | 4        | 10 (bits)           |

where:

**1** The high-order bit of the low-order byte is set to indicate a FIXUP subrecord.

**M** Is the mode; M=1 for segment-relative fixups, and M=0 for self-relative fixups.

**Location** Is a 4-bit field that determines what type of LOCATION is to be fixed up:

**0** Low-order byte (8-bit displacement or low byte of 16-bit offset).

**1** 16-bit offset.

**2** 16-bit base—logical segment base (selector).

**3** 32-bit Long pointer (16-bit base:16-bit offset).

**4** High-order byte (high byte of 16-bit offset). Microsoft LINK and IBM LINK386 do not support this type.

**5** 16-bit loader-resolved offset, treated as Location=1.

**Conflict:** The PharLap implementation of OMF uses Location=5 to indicate a 32-bit offset, where IBM and Microsoft use Location=9.

6 Not defined, reserved.

**Conflict:** The PharLap implementation of OMF uses Location=6 to indicate a 48-bit pointer (16-bit base:32-bit offset), where IBM and Microsoft use Location=11.

7 Not defined, reserved.

8 Not defined, reserved.

9 32-bit offset.

10 Not defined, reserved.

11 48-bit pointer (16-bit base:32-bit offset).

12 Not defined, reserved.

13 32-bit loader-resolved offset, treated as Location=9 by the linker.

**Data Record Offset**
:   Indicates the position of the LOCATION to be fixed up in the LEDATA or LIDATA record immediately preceding the FIXUPP record. This offset indicates either a byte in the Data Bytes field of an LEDATA record or a data byte in the Content field of a Data Block field in an LIDATA record.

The Fix Data bit layout is

| F | Frame | T | P | Targt    |
|---|-------|---|---|----------|
| 1 | 3     | 1 | 1 | 2 (bits) |

and is interpreted as follows:

**F**
:   If F=1, the FRAME is given by a FRAME thread whose number is in the Frame field (modulo 4). There is no Frame Datum field in the subrecord.

    If F=0, the FRAME method (in the range F0 to F5) is explicitly defined in this FIXUP subrecord. The method is stored in the Frame field.

**Frame**
:   A 3-bit numeric field, interpreted according to the F bit. The Frame Datum field is present and is an index field for FRAME methods F0, F1, and F2 only.

**T**
:   If T=1, the TARGET is defined by a TARGET thread whose thread number is given in the 2-bit Targt field. The Targt field contains a number between 0 and 3 that refers to a previous THREAD subrecord containing the TARGET method. The P bit, combined with the two low-order bits of the Method field in the THREAD subrecord, determines the TARGET method.

    If T=0, the TARGET is specified explicitly in this FIXUP subrecord. In this case, the P bit and the Targt field can be considered a 3-bit field analogous to the Frame field.

| <b>P</b>     | Determines whether the Target Displacement field is present.<br>If P=1, there is no Target Displacement field.<br>If P=0, the Target Displacement field is present. It is a 4-byte field if the record type is 9DH; it is a 2-byte field otherwise. |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <b>Targt</b> | A 2-bit numeric field, which gives the lower two bits of the TARGET method (if T=0) or gives the TARGET thread number (if T=1).                                                                                                                     |

##### Frame Datum, Target Datum, and Target Displacement Fields

The Frame Datum field is an index field that refers to a previous SEGDEF, GRPDEF, or EXTDEF record, depending on the FRAME method.

Similarly, the Target Datum field contains a segment index, a group index, or an external name index, depending on the TARGET method.

The Target Displacement field, a 16-bit or 32-bit field, is present only if the P bit in the Fix Data field is set to 0, in which case the Target Displacement field contains the offset used in methods 0, 1, and 2 of specifying a TARGET.

### Notes

*FIXUPP records are used to fix references in the immediately preceding LEDATA, LIDATA, or COMDAT record.*

*The Frame field is the translator's way of telling the linker the contents of the segment register used for the reference; the TARGET is the item being referenced whose address was not completely resolved by the translator. In protected mode, the only legal segment register values are selectors; every segment and group of segments is mapped through some selector and addressed by an offset within the underlying memory defined by that selector.*

### Examples

For good examples of the usage of the FIXUP record, consult *The MS-DOS Encyclopedia*.
