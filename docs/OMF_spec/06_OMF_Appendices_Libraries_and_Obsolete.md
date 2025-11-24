## Appendix 1: Microsoft Symbol and Type Extensions

Microsoft symbol and type information is stored on a per-module basis in specially-named logical segments. These segments are defined in the usual way (SEGDEF records), but the linker handles them specially, and they do not end up as segments in the .EXE file. These segment names are reserved:

| Segment Name | Class Name | Combine Type |
|--------------|------------|--------------|
| \$\$TYPES    | DEBTYP     | Private      |
| \$\$SYMBOLS  | DEBSYM     | Private      |

The segment \$\$IMPORT should also be considered a reserved name, although it is not used anymore. This segment was not part of any object files but was emitted by the linker to get the loader to automatically do fixups for Microsoft symbol and type information. The linker emitted a standard set of imports, not just ones referenced by the program being linked. Use of this segment may be revisited in the future.

Microsoft symbol and type information-specific data is stored in LEDATA records for the \$\$TYPES and \$\$SYMBOLS segments, in various proprietary formats. The \$\$TYPES segment contains information on user-defined variable types; \$\$SYMBOLS contains information about nonpublic symbols: stack, local, procedure, block start, constant, and register symbols and code labels.

For instantiated functions in Microsoft C 7.0, symbol information for Microsoft symbol and type information will be output in COMDAT records that refer to segment \$\$SYMBOLS and have decorated names based on the function names. Type information will still go into the \$\$TYPES segment in LEDATA records.

All OMF records that specify a Type Index field, including EXTDEF, PUBDEF, and COMDEF records, use Microsoft symbol and type information values. Because many types are common, Type Index values in the range 0 through 511 (1FFH) are reserved for a set of predefined primitive types. Indexes in the range 512 through 32767 (200H-7FFFH) index into the set of type definitions in the module's \$\$TYPES segment, offset by 512. Thus 512 is the first new type, 513 the second, and so on.

## Appendix 2: Library File Format

The first record in the library is a header that looks like any other object module format record.

**Note:** Libraries under MS-DOS are always multiples of 512-byte blocks.

### Library Header Record (n bytes)

| 1          | 2                                 | 4                 | 2                         | 1     | <n - 10> |
|------------|-----------------------------------|-------------------|---------------------------|-------|----------|
| Type (F0H) | Record Length (Page Size Minus 3) | Dictionary Offset | Dictionary Size in Blocks | Flags | Padding  |

The first byte of the record identifies the record's type, and the next two bytes specify the number of bytes remaining in the record. Note that this word field is byte-swapped (that is, the low-order byte precedes the high-order byte). The record type for this library header is F0H (240 decimal).

The Record Length field specifies the page size within the library. Modules in a library always start at the beginning of a page. Page size is determined by adding three to the value in the Record Length field (thus the header record always occupies exactly one page). Legal values for the page size are given by  $2^n$ , where *n* is greater than or equal to 4 and less than or equal to 15.

The four bytes immediately following the Record Length field are a byte-swapped long integer specifying the byte offset within the library of the first byte of the first block of the dictionary.

The next two bytes are a byte-swapped word field that specifies the number of blocks in the dictionary.

Note: the MS-DOS Library Manager cannot create a library whose dictionary would require more than 251 512-byte pages.

The next byte contains flags describing the library. The current flag definition is:

0x01 = case sensitive (applies to both regular and extended dictionaries)

All other values are reserved for future use and should be 0.

The remaining bytes in the library header record are not significant. This record deviates from the typical OMF record in that the last byte is not used as a checksum on the rest of the record.

Immediately following the header is the first object module in the library. It, in turn, is succeeded by all other object modules in the library. Each module is in object module format (that is, it starts with a LHEADR record and ends with a MODEND record). Individual modules are aligned so as to begin at the beginning of a new page. If, as is commonly the case, a module does not occupy a number of bytes that is exactly a multiple of the page size, then its last block will be padded with as many null bytes as are required to fill it.

Following the last object module in the library is a record that serves as a marker between the object modules and the dictionary. It also resembles an OMF record.

### Library End Record (marks end of objects and beginning of dictionary)

| 1          | 2             | <n>     |
|------------|---------------|---------|
| Type (F1H) | Record Length | Padding |

###### Relocatable Object Module Format

The record's Type field contains F1H (241 decimal), and its Record Length field is set so that the dictionary begins on a 512-byte boundary. The record contains no further useful information; the remaining bytes are insignificant. As with the library header, the last byte is not a checksum.

### Dictionary

The remaining blocks in the library compose the dictionary. The number of blocks in the dictionary is given in the library header. The dictionary provides rapid searching for a name using a two-level hashing scheme.

Due to the hashing algorithm, the number of dictionary blocks must be a prime number, and within each block is a prime number of buckets. Whereas a librarian can choose the prime number less than 255 for the dictionary blocks, the number of buckets within a block is fixed at 37.

To search for a name within the blocks, two hashing indices and two hash deltas are computed. A block index and block delta controls how to go from one block to the other, and a bucket index and bucket delta controls how to search buckets within a block. Each bucket within a block corresponds to a single string.

A block is 512 bytes long and the first 37 bytes correspond to the 37 buckets. To find the string corresponding to a bucket, multiply the value stored in the byte by two and use that as an index into the block. At this location in the block lies an unsigned byte value for the string length, followed by the string characters (not 0-terminated), which in turn is followed by a two-byte little-endian-format module number in which the module in the library defining this string can be found. Thus, all strings start at even locations in the block.

Byte 38 in a block records the free space left for storing strings in the block, and is an index of the same format as the bucket indices; that is, multiply the bucket index by two to find the next available slot in the block. If byte 38 has the value 255, there is no space left.

#### Dictionary Record (length is the dictionary size in 512-byte blocks)

| 37   | 1     | <variable> | 2            | <conditional> |
|------|-------|------------|--------------|---------------|
| HTAB | FFLAG | Name       | Block Number | Align Byte    |

< -------------------------- repeated -------------------------->

Entries consist of the following: the first byte is the length of the symbol to follow, the following bytes are the text of the symbol, and the last two bytes are a byte-swapped word field that specifies the page number (counting the library header as page 0) at which the module defining the symbol begins.

All entries may have at most one trailing null byte in order to align the next entry on a word boundary.

Module names are stored in the LHEADR record of each module.

### Extended Dictionary

The extended dictionary is optional and indicates dependencies between modules in the library. Versions of LIB earlier than 3.09 do not create an extended dictionary. The extended dictionary is placed at the end of the library.

The dictionary is preceded by these values:

BYTE =0xF2 Extended Dictionary header

WORD length of extended dictionary in bytes excluding first three bytes

Start of extended dictionary:

WORD number of modules in library = N

Module table, indexed by module number, with N + 1 fixed-length entries:

WORD module page number

WORD offset from start of extended dictionary to list of required modules

Last entry is null.

### Dictionary Hashing Algorithm

Pseudocode for creating a library and inserting names into a dictionary is listed below.

```
typedef unsigned short hash_value;
typedef struct {
    hash_value block_x, block_d, bucket_x, bucket_d;
} hash;
typedef unsigned char block[512];
unsigned short nblocks = choose some prime number such that it is
    likely that all the names will fit in those blocks (the value must be
    greater than 1 and less than 255);
const int nbuckets = 37;
const int freespace = nbuckets+1;
MORE BLOCKS: ;
// Allocate storage for the dictionary:
block *blocks = malloc(nblocks*sizeof(block));
// Zero out each block.
memset(blocks,0,nblocks*sizeof(block));
// Initialize freespace pointers.
for (int i = 0; i < nblocks; i++)
    blocks[i][freespace] = freespace/2;

for N <- each name you want to insert in the library do {
    int length_of_string = strlen(N); // # of characters.
    // Hash the name, producing the four values (see below
    // for hashing algorithm):
    hash h = compute_hash(N, nblocks);
    hash_value start_block = h.block_x, start_bucket = h.bucket_x;
    // Space required:
    // 1 for len byte; string text; 2 bytes for module number;
    // 1 possible byte for pad.
    int space_required=1+length_of_string+2;
    if (space_required % 2) space_required++; // Make sure even.
NEXT BLOCK: ;
// Obtain pointer to block:
unsigned char *bp = blocks[h.block_x];
boolean success = FALSE;
do {
    if (bp[h.bucket_x] == 0) {
        if (512-bp[freespace]*2 < space_required) break;
        // Found space.
        bp[h.bucket_x] = bp[freespace];
        int store_at = 2*bp[h.bucket_x];
        bp[store_at] = length_of_string;
        bp[store_at+1..store_at+length_of_string] = string characters;
        int mod_location = store_at+length_of_string;
        // Put in the module page number, LSB format.
        bp[mod_location] = module_page_number % 256;
        bp[mod_location+1] = module_page_number / 256;
        bp[freespace] += space_required/2;
        // In case we are right at the end of the block,
        // set block to full.
        if (bp[freespace] == 0) bp[freespace] = 0xff;
        success = TRUE;}
```

```
break;
}
h.bucket_x = (h.bucket_x+h.bucket_d) % nbuckets;
} while (h.bucket_x != start_bucket);
if (!success) {
    // If we got here, we found no bucket. Go to the next block.
    h.block_x = (h.block_x + h.block_d) % nblocks;
    if (h.block_x == start_block) {
        // We got back to the start block; there is no space
        // anywhere. So increase the number of blocks to the
        // next prime number and start all over with all names.
        do nblocks++; while (nblocks is not prime);
        free(blocks);
        goto MORE_BLOCKS;
    }
    // Whenever you can't fit a string in a block, you must mark
    // the block as full, even though there may be enough space
    // to handle a smaller string. This is because the linker,
    // after failing to find a string in a block, will decide
    // the string is undefined if the block has any space left.
    bp[freespace] = 0xff;
    goto NEXT_BLOCK;
}
}
```

The order of applying the deltas to advance the hash indices is critical, due to the behavior of the linker. For example, it would not be correct to check a block to see if there is enough space to store a string before checking the block's buckets, because this is not the way the linker functions. The linker does not restart at bucket 0 when it moves to a new block. It resumes at the bucket last used in the previous block. Thus, the librarian must move through the buckets, even though there is not enough room for the string, so that the final bucket index is the same one the linker arrives at when it finishes searching the block.

The algorithm to compute the four hash indices is listed below.

```
hash compute_hash(const unsigned char* name, int blocks) {
    int len = strlen(name);
    const unsigned char *pb = name, *pe = name+len;
    const int blank = 0x20; // ASCII blank.
    hash value
    // Left-to-right scan:
    block_x = len | blank, bucket_d = block_x,
    // Right-to-left scan:
    block_d = 0, bucket_x = 0;
    #define rotr(x,bits) ((x << 16-bits) | (x >> bits))
    #define rotl(x,bits) ((x << bits) | (x >> 16-bits))
    while (1) {
        // blank -> convert to LC.
        unsigned short cback = *--pe | blank;
        bucket_x = rotr(bucket_x,2) ^ cback;
        block_d = rotl(block_d,2) ^ cback;
        if (--len == 0) break;
        unsigned short cfront = *pb++ | blank;
        block_x = rotl(block_x,2) ^ cfront;
        bucket_d = rotr(bucket_d,2) ^ cfront;
    }
    hash h;
    h.block_x = block_x % blocks;
    h.block_d = _max(block_d % blocks,1);
    h.bucket_x = bucket_x % nbuckets;
    h.bucket_d = _max(bucket_d % nbuckets,1);
    return h;
}
```

## Appendix 3: Obsolete Records and Obsolete Features of Existing Records

This appendix contains a complete list of records that have been defined in the past but are not part of the TIS OMF. These record types are followed by a descriptive paragraph from the original Intel 8086 specification. When linkers encounter these records, they are free to process them, ignore them, or generate an error.

### Obsolete Records

| 6EH | RHEADR | <b>R-Module Header Record</b>             | This record serves to identify a module that has been processed (output) by Microsoft LINK-86/LOCATE-86. It also specifies the module attributes and gives information on memory usage and need.                                                                                                               |
|-----|--------|-------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 70H | REGINT | <b>Register Initialization Record</b>     | This record provides information about the 8086 register/register-pairs: CS and IP, SS and SP, DS and ES. The purpose of this information is for a loader to set the necessary registers for initiation of execution.                                                                                          |
| 72H | REDATA | <b>Relocatable Enumerated Data Record</b> | This record provides contiguous data from which a portion of an 8086 memory image may eventually be constructed. The data may be loaded directly by an 8086 loader, with perhaps some base fixups. The record may also be called a Load-Time Locatable (LTL) Enumerated Data Record.                           |
| 74H | RIDATA | <b>Relocatable Iterated Data Record</b>   | This record provides contiguous data from which a portion of an 8086 memory image may eventually be constructed. The data may be loaded directly by an 8086 loader, but data bytes within the record may require expansion. The record may also be called a Load-Time Locatable (LTL) Iterated Data Record.    |
| 76H | OVLDEF | <b>Overlay Definition Record</b>          | This record provides the overlay's name, its location in the object file, and its attributes. A loader may use this record to locate the data records of the overlay in the object file.                                                                                                                       |
| 78H | ENDREC | <b>End Record</b>                         | This record is used to denote the end of a set of records, such as a block or an overlay.                                                                                                                                                                                                                      |
| 7AH | BLKDEF | <b>Block Definition Record</b>            | This record provides information about blocks that were defined in the source program input to the translator that produced the module. A BLKDEF record will be generated for every procedure and for every block that contains variables. This information is used to aid debugging programs.                 |
| 7CH | BLKEND | <b>Block End Record</b>                   | This record, together with the BLKDEF record, provides information about the scope of variables in the source program. Each BLKDEF record must be followed by a BLKEND record. The order of the BLKDEF, debug symbol records, and BLKEND records should reflect the order of declaration in the source module. |

| 7EH | DEBSYM | <b>Debug Symbols Record</b><br>This record provides information about all local symbols, including stack and based symbols. The purpose of this information is to aid debugging programs.                                                                                                                                                                                       |
|-----|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 84H | PEDATA | <b>Physical Enumerated Data Record</b><br>This record provides contiguous data, from which a portion of an 8086 memory image may be constructed. The data belongs to the "unnamed absolute segment" in that it has been assigned absolute 8086 memory addresses and has been divorced from all logical segment information.                                                     |
| 86H | PIDATA | <b>Physical Iterated Data Record</b><br>This record provides contiguous data, from which a portion of an 8086 memory image may be constructed. It allows initialization of data segments and provides a mechanism to reduce the size of object modules when there is repeated data to be used to initialize a memory image. The data belongs to the "unnamed absolute segment." |
| 8EH | TYPDEF | This record contains details about the type of data represented by a name declared in a PUBDEF or EXTDEF record. For more details on this record, refer to its description later in this appendix.                                                                                                                                                                              |
| 92H | LOCSYM | <b>Local Symbols Record</b><br>This record provides information about symbols that were used in the source program input to the translator that produced the module. This information is used to aid debugging programs. This record has a format identical to the PUBDEF record.                                                                                               |
| 9EH | (none) | <b>Unnamed record</b><br>This record number was the only even number not defined by the original Intel 8086 specification. Apparently it was never used.                                                                                                                                                                                                                        |
| A4H | LIBHED | <b>Library Header Record</b><br>This record is the first record in a library file. It immediately precedes the modules (if any) in the library. Following the modules are three more records in the following order: LIBNAM, LIBLOC, and LIBDIC.                                                                                                                                |
| A6H | LIBNAM | <b>Library Module Names Record</b><br>This record lists the names of all the modules in the library. The names are listed in the same sequence as the modules appear in the library.                                                                                                                                                                                            |
| A8H | LIBLOC | <b>Library Module Locations Record</b><br>This record provides the relative location, within the library file, of the first byte of the first record (either a THEADR or LHEADR or RHEADR record) of each module in the library. The order of the locations corresponds to the order of the modules in the library.                                                             |
| AAH | LIBDIC | <b>Library Dictionary Record</b><br>This record gives all the names of public symbols within the library. The public names are separated into groups; all names in the <i>n</i> th group are defined in the <i>n</i> th module of the library.                                                                                                                                  |

#### 8EH TYPDEF—Type Definition Record

##### Description

The TYPDEF record contains details about the type of data represented by a name declared in a PUBDEF or an EXTDEF record. This information may be used by a linker to validate references to names, or it may be used by a debugger to display data according to type.

Although the original Intel 8086 specification allowed for many different type specifications, such as scalar, pointer, and mixed data structure, many linkers used TYPDEF records to declare only communal variables. Communal variables represent globally shared memory areas—for example, FORTRAN common blocks or uninitialized public variables in Microsoft C. This function is served by the COMDEF record.

The size of a communal variable is declared explicitly in the TYPDEF record. If a communal variable has different sizes in different object modules, the linker uses the largest declared size when it generates an executable module.

##### History

Starting with Microsoft LINK version 3.5, the COMDEF record should be used for declaration of communal variables. However, for compatibility, later versions of Microsoft LINK recognize TYPDEF records as well as COMDEF records.

##### Record Format

| 1  | 2             | <variable> | 1      | <variable>      | 1        |
|----|---------------|------------|--------|-----------------|----------|
| 8E | Record Length | Name       | 0 (EN) | Leaf Descriptor | Checksum |

The name field of a TYPDEF record is in *count, char* format and is always ignored. It is usually a 1-byte field containing a single 0 byte.

The Eight-Leaf Descriptor field in the original Intel 8086 specification was a variable-length (and possibly repeated) field that contained as many as eight "leaves" that could be used to describe mixed data structures. Microsoft uses a stripped-down version of the Eight-Leaf Descriptor, of which the first byte, the EN byte, is always set to 0.

The Leaf Descriptor field is a variable-length field that describes the type and size of a variable. The two possible variable types are NEAR and FAR.

If the field describes a NEAR variable (one that can be referenced as an offset within a default data segment), the format of the Leaf Descriptor field is:

| 1   | 1             | <variable>     |
|-----|---------------|----------------|
| 62H | Variable Type | Length in Bits |

The 1-byte field containing 62H signifies a NEAR variable.

The Variable Type field is a 1-byte field that specifies the variable type:

| 77H | Array     |
|-----|-----------|
| 79H | Structure |
| 7BH | Scalar    |

###### Relocatable Object Module Format

This field must contain one of the three values given above, but the specific value is ignored by most linkers.

The Length in Bits field is a variable-length field that indicates the size of the communal variable. Its format depends on the size it represents.

If the first byte of the size is 128 (80H) or less, then the size is that value. If the first byte of the size is 81H, then a 2-byte size follows. If the first byte of the size is 84H, then a 3-byte size follows. If the first byte of the size is 88H, then a 4-byte size follows.

If the Leaf Descriptor field describes a FAR variable (one that must be referenced with an explicit segment and offset), the format is:

| 1   | 1                   | <variable>         | <variable>         |
|-----|---------------------|--------------------|--------------------|
| 61H | Variable Type (77H) | Number of Elements | Element Type Index |

The 1-byte field containing 61H signifies a FAR variable.

The 1-byte variable type for a FAR communal variable is restricted to 77H (array). (As with the NEAR Variable Type field, the linker ignores this field, but it must have the value 77H.)

The Number of Elements field is a variable-length field that contains the number of elements in the array. It has the same format as the Length in Bits field in the Leaf Descriptor field for a NEAR variable.

The Element Type Index field is an index field that references a previous TYPDEF record. A value of 1 indicates the first TYPDEF record in the object module, a value of 2 indicates the second TYPDEF record, and so on. The TYPDEF record referenced must describe a NEAR variable. This way, the data type and size of the elements in the array can be determined.

**Note:** Microsoft LINK limits the number of TYPDEF records in an object module to 256.

##### Examples

The following three examples of TYPDEF records were generated by Microsoft C Compiler version 3.0. (Later versions use COMDEF records.)

The first sample TYPDEF record corresponds to the public declaration:

```
int var; /* 16-bit integer */
```

The TYPDEF record is:

```
      0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F  
0000 8E 06 00 00 00 62 7B 10 7F             .....b{..
```

Byte 00H contains 8EH, indicating that this is a TYPDEF record.

Bytes 01-02H contain 0006H, the length of the remainder of the record.

Byte 03H (the name field) contains 00H, a null name.

Bytes 04-07H represent the Eight-Leaf Descriptor field. The first byte of this field (byte 04H) contains 00H. The remaining bytes (bytes 05-07H) represent the Leaf Descriptor field:

- Byte 05H contains 62H, indicating that this TYPDEF record describes a NEAR variable.
- Byte 06H (the Variable Type field) contains 7BH, which describes this variable as scalar.
- Byte 07H (the Length in Bits field) contains 10H, the size of the variable in bits.

Byte 08H contains the Checksum field, 7FH.

The next example demonstrates how the variable size contained in the Length in Bits field of the Leaf Descriptor field is formatted:

```
char var2[32768]; /* 32 KB array */
```

The TYPDEF record is:

|      | 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  | A  | B  | C | D | E | F |               |
|------|----|----|----|----|----|----|----|----|----|----|----|----|---|---|---|---|---------------|
| 0000 | 8E | 09 | 00 | 00 | 00 | 62 | 7B | 84 | 00 | 00 | 04 | 04 |   |   |   |   | .....bc{..... |

The Length in Bits field (bytes 07-0AH) starts with a byte containing 84H, which indicates that the actual size of the variable is represented as a 3-byte value (the following three bytes). Bytes 08-0AH contain the value 040000H, the size of the 32K array in bits.

This third Microsoft C statement, because it declares a FAR variable, causes two TYPDEF records to be generated:

```
char far var3[10][2][20]; /* 400-element FAR array*/
```

The two TYPDEF records are:

|      | 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  | A  | B  | C  | D  | E  | F  |                  |
|------|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|------------------|
| 0000 | 8E | 06 | 00 | 00 | 62 | 7B | 08 | 87 | 8E | 09 | 00 | 00 | 00 | 00 | 61 | 77 | ....bc{......aw  |
| 0010 | 81 | 90 | 01 | 01 | 7E |    |    |    |    |    |    |    |    |    |    |    | ...... ......... |

Bytes 00-08H contain the first TYPDEF record, which defines the data type of the elements of the array (NEAR, scalar, 8 bits in size).

Bytes 09-14H contain the second TYPDEF record. The Leaf Descriptor field of this record declares that the variable is FAR (byte 0EH contains 61H) and an array (byte 0FH, the variable type, contains 77H).

**Note:** Because this TYPDEF record describes a FAR variable, bytes 10-12H represent a Number of Elements field. The first byte of the field is 81H, indicating a 2-byte value, so the next two bytes (bytes 11-12H) contain the number of elements in the array, 0190H (400D).

Byte 13H (the Element Type Index field) contains 01H, which is a reference to the first TYPDEF record in the object module—in this example, the one in bytes 00-08H.

#### PharLap Extensions to The SEGDEF Record (Obsolete Extension)

The following describes an obsolete extension to the SEGDEF record.

In the PharLap 32-bit OMF, there is an additional optional field that follows the Overlay Name Index field. The reserved bits should always be 0. The format of this field is

| <----------------5 bits------------------> | <--1 bit--> | <-------2 bits------> |
|--------------------------------------------|-------------|-----------------------|
| Reserved                                   | U           | AT                    |

where **AT** is the access type for the segment and has the following possible values

- 0 Read only
- 1 Execute only
- 2 Execute/read
- 3 Read/write

and **U** is the Use16/Use32 bit for the segment and has the following possible values:

- 0 Use16
- 1 Use32

**Conflict:** The PharLap OMF uses a 16-bit Repeat Count field, even in 32-bit records.
