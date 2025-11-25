Taken from WATCOM's linker manual

---
## 2.1 Version number and source language identification

Since there may be different versions of the type and local symbol information, and there may be multiple front-ends a special OMF COMENT record is placed in the object file. It has the following form:

```
comment_class = 0xfe
'D'
major_version_number (char)
minor_version_number (char)
source_language (string)
```

The `comment_class` of 0xfe indicates a linker directive comment. The character 'D' informs the linker that this record is providing debugging information. The `major_version_number` is changed whenever there is a modification made to the types or local symbol classes that is not upwardly compatible with previous versions. The `minor_version_number` increments by one whenever a change is made to those classes that is upwardly compatible with previous versions. The `source_language` field is a string which determines what language that the file was compiled from.

If the debugging comment record is not present, the local and type segments (described later) are not in WATCOM format and should be omitted from the resulting executable file's debugging information. The current major version is one, and the current minor version is three.
