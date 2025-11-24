## The Object Record Format

### Record Format

All object records conform to the following format:

|             |               | <------------------Record Length in Bytes------------------> |               |
|-------------|---------------|--------------------------------------------------------------|---------------|
| 1           | 2             | <variable>                                                   | 1             |
| Record Type | Record Length | Record Contents                                              | Checksum or 0 |

The Record Type field is a 1-byte field containing the hexadecimal number that identifies the type of object record. The format is determined by the least significant bit of the Record type field. An odd Record Type indicates that certain numeric fields within the record contain 32-bit values; an even Record Type indicates that those fields contain 16-bit values. The affected fields are described with each record. Note that this principle does not govern the Use32/Use16 segment attribute (which is set in the ACBP byte of SEGDEF records); it simply specifies the size of certain numeric fields within the record. It is possible to use 16-bit OMF records to generate 32-bit segments, or vice versa.

The Record Length field is a 2-byte field that gives the length of the remainder of the object record in bytes (excluding the bytes in the Record Type and Record Length fields). The record length is stored with the low-order byte first. An entire record occupies 3 bytes plus the number of bytes in the Record Length field.

The Record Contents field varies in size and format, depending on the record type.

The Checksum field is a 1-byte field that contains the negative sum (modulo 256) of all other bytes in the record. In other words, the checksum byte is calculated so that the low-order byte of the sum of all the bytes in the record, including the checksum byte, equals 0. Overflow is ignored. Some compilers write a 0 byte rather than computing the checksum, so either form should be accepted by programs that process object modules.

**Note:** The maximum size of the entire record (unless otherwise noted for specific record types) is 1024 bytes.

## Frequent Object Record Subfields

The contents of each record are determined by the record type, but certain subfields appear frequently enough to be explained separately. The format of such fields is below.

### Names

A name string is encoded as an 8-bit unsigned count followed by a string of count characters, refered to as *count, char* format. The character set is usually some ASCII subset. A null name is specified by a single byte of 0 (indicating a string of length 0).

### Indexed References

Certain items are ordered by occurrence and are referenced by index. The first occurrence of the item has index number 1. Index fields may contain 0 (indicating that they are not present) or values from 1 through 7FFF. The index number field in an object record can be either 1 or 2 bytes long. If the number is in the range 0–7FH, the high-order bit (bit 7) is 0 and the low-order bits contain the index number, so the field is only 1 byte long. If the index number is in the range 80–7FFFH, the field is 2 bytes long. The high-order bit of the first byte in the field is set to 1, and the high-order byte of the index number (which must be in the range 0–7FH) fits in the remaining 7 bits. The low-order byte of the index number is specified in the second byte of the field. The code to decode an index is:

```
if (first_byte & 0x80)
index_word = (first_byte & 7F) * 0x100 + second_byte;
else
index_word = first_byte;
```

### Type Indexes

Type Index fields occupy 1 or 2 bytes and occur in PUBDEF, LPUBDEF, COMDEF, LCOMDEF, EXTDEF, and LEXTDEF records. These type index fields were used in old versions of the OMF to reference TYPDEF records. This usage is obsolete. This field is usually left empty (encoded as 1 byte with value 0). However some linkers may use this for debug information or other purposes.

### Ordered Collections

Certain records and record groups are ordered so that the records may be referred to with indexes (the format of indexes is described in the "Indexed References" section). The same format is used whether an index refers to names, logical segments, or other items.

The overall ordering is obtained from the order of the records within the file together with the ordering of repeated fields within these records. Such ordered collections are referenced by index, counting from 1 (index 0 indicates unknown or not specified).

For example, there may be many LNAMES records within a module, and each of those records may contain many names. The names are indexed starting at 1 for the first name in the first LNAMES record encountered while reading the file, 2 for the second name in the first record, and so forth, with the highest index for the last name in the last LNAMES record encountered.

The ordered collections are:

| <b>Names</b>            | Ordered by occurrence of LNAMES records and names within each. Referenced as a name index.                                                                 |
|-------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <b>Logical Segments</b> | Ordered by occurrence of SEGDEF records in file. Referenced as a segment index.                                                                            |
| <b>Groups</b>           | Ordered by occurrence of GRPDEF records in file. Referenced as a group index.                                                                              |
| <b>External Symbols</b> | Ordered by occurrence of EXTDEF, COMDEF, LEXTDEF, and LCOMDEF records and symbols within each. Referenced as an external name index (in FIXUP subrecords). |

### Numeric 2-Byte and 4-Byte Fields

Words and double words (16- and 32-bit quantities, respectively) are stored in little endian byte order (lowest address is least significant).

Certain records, notably SEGDEF, PUBDEF, LPUBDEF, LINNUM, LEDATA, LIDATA, FIXUPP, and MODEND, contain size, offset, and displacement values that may be 32-bit quantities for Use32 segments. The encoding is as follows:

- When the least-significant bit of the record type byte is set (that is, the record type is an odd number), the numeric fields are 4 bytes.
- When the least-significant bit of the record type byte is clear, the fields occupy 2 bytes. The values are zero-extended when applied to Use32 segments.

*Note: See the description of SEGDEF records for an explanation of Use16/Use32 segments.*

## Order of Records

The sequence in which the types of object records appear in an object module is fairly flexible in some respects. Several record types are optional, and if the type of information they carry is unnecessary, they are omitted from the object module. In addition, most object record types can occur more than once in the same object module. And because object records are variable in length, it is often possible to choose between combining information into one large record or breaking it down into several smaller records of the same type.

An important constraint on the order in which object records appear is the need for some types of object records to refer to information contained in other records. Because the linker processes the records sequentially, object records containing such information must precede the records that refer to the information. For example, two types of object records, SEGDEF and GRPDEF, refer to the names contained in an LNAMES record. Thus, an LNAMES record must appear before any SEGDEF or GRPDEF records that refer to it so that the names in the LNAMES record are known to the linker by the time it processes the SEGDEF or GRPDEF records.

The record order is chosen so that the number of linker passes through an object module are minimized. Most linkers make two passes through the object modules: the first pass may be cut short by the presence of the Link Pass Separator COMENT record; the second pass processes all records.

For greatest linking speed, all symbolic information should occur at the start of the object module. This order is recommended but not mandatory. The general ordering is:

### Identifier Record(s)

THEADR or LHEADR record

**Note:** *This must be the first record.*

### Records Processed by Pass 1

The following records may occur in any order but they *must* precede the Link Pass Separator if it is present:

- COMENT records identifying object format and extensions
- COMENT records other than Link Pass Separator comment
- LNAMES or LLNAMES records providing ordered name list
- SEGDEF records providing ordered list of program segments
- GRPDEF records providing ordered list of logical segments
- TYPDEF records (obsolete)
- ALIAS records
- PUBDEF records locating and naming public symbols
- LPUBDEF records locating and naming private symbols
- COMDEF, LCOMDEF, EXTDEF, LEXTDEF, and CEXTDEF records

**Note:** *This group of records is indexed together, so external name index fields in FIXUPP records may refer to any of the record types listed.*

### Link Pass Separator (Optional)

COMENT class A2 record is used to indicate that Pass 1 of the linker is complete. When this record is encountered, many linkers stop their first pass over the object file. Records preceding the link pass separator define the symbolic information for the file.

For greater linking speed, all LIDATA, LEDATA, FIXUPP, BAKPAT, INCDEF, and LINNUM records should come after the A2 COMENT record, but this is not required. Pass 2 should begin again at the start of the object module so that these records are processed in Pass 2 regardless of where they are placed in the object module.

### Records Ignored by Pass 1 and Processed by Pass 2

The following records may come before or after the Link Pass Separator:

- LIDATA, LEDATA, or COMDAT records followed by applicable FIXUPP records

- FIXUPP records containing only THREAD subrecords

- BAKPAT and NBKPAT FIXUPP records

- COMENT class A0, subrecord type 03 (INCDEF) records containing incremental compilation information for FIXUPP and LINNUM records

- LINNUM and LINSYM records providing line number and program code or data association

### Terminator

MODEND record indicating end of module with optional start address
