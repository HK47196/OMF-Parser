Taken from 386|LINK reference manual
---

# Appendix C

# Object Module Formats

The format used by 386|LINK for 32-bit object files (".OBJ" files) is called "Easy OMF-386". Easy OMF-386 is a simple extension of the OMF-86 format used by Intel and Microsoft. This appendix describes the differences between Easy OMF-386 and OMF-86. For a description of OMF-86, see references 1 or 2.

An assembler or compiler signals to 386|LINK that an object module is targeted for the 80386 by placing the following comment record at the beginning of an object module:

```
0      1      2         3                7      8
    ┌──────┬──────┬──────┬───────────────────┬──────┐
    │ 88H  │ 80H  │ AAH  │      '80386'      │      │
    └──────┴──────┴──────┴───────────────────┴──────┘
    Record  Flags  Class                      Checksum
     Type
```

**FIGURE C-1**
Comment Record Format

The 80386 comment record should be located immediately after the module header record (THEADR) and before any other records of the object module.

The other records of an object module are formatted in Easy OMF-386 the same way as the 8086, except that any offset, displacement, or segment length field of an object record is four bytes long instead of two bytes. The following records contain fields which increase in size:


## Object Module Formats

---

| Record:        | Field:                    |
|----------------|---------------------------|
| SEGDEF         | Offset and segment length |
| PUBDEF         | Offset                    |
| LEDATA         | Offset                    |
| LIDATA         | Offset                    |
| Explicit FIXUPP| Target displacement       |
| BLKDEF         | Return address offset     |
| LINNUM         | Offset                    |
| MODEND         | Target displacement       |

In FIXUPP records, the following new "Loc" values have been defined:

- 5 -- 32-bit offset
- 6 -- Base + 32-bit offset (long pointer)

In SEGDEF records, the following new "align" value has been defined:

- 6 -- Segment is aligned on a 4K page boundary

An optional attribute byte is placed immediately following the overlay name
index field in a SEGDEF record. The format of the attribute byte is:
```
    7                       3   2   1   0
    ┌───────────────────────┬───┬───────┐
    │       Reserved        │ U │  AT   │
    └───────────────────────┴───┴───────┘
```

**FIGURE C-2**
Attribute Byte Format

These are the bits in the attribute byte:

- Bits 0-1 -- Segment Access Type

      00 = RO (read only)
      01 = EO (execute only)
      10 = ER (execute/read)
      11 = RW (read write)

