Parser/dumper for the Relocatable Object Module Format(OMF) format based upon
the TIS Specification v1.1. The intent is to be an entirely standards compliant parser as per the TIS spec.

Should support all mentioned extensions and obsolete features.

## Known Limitations

- **Mixed-variant libraries not supported**: Libraries containing object modules
  compiled with different OMF variants (e.g., some PharLap Easy OMF-386, some TIS
  standard) are not supported. The parser detects variant at the file level and
  applies it uniformly to all modules. If a mixed-variant library is detected,
  the parser will exit with an error.

## TODO

- May eventually support the OS/2 OMF Specification.

- Need to review Microsoft's specifications to see what, if any, extensions they
  made.

- Need a large test corpus
