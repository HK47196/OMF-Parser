"""OMF format variant definitions.

Variants change how records are parsed (field sizes, extra fields, etc.).
This is distinct from extensions which add new semantics but use the same parsing.

Variants:
- TIS Standard: Baseline OMF-86/286/386 per TIS specification
- PharLap Easy OMF-386: 32-bit DOS extender format with fixed 4-byte offsets
- IBM LINK386: OS/2 2.x+ format with inline names in some records
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Variant:
    """Base TIS Standard OMF variant."""
    name: str = "TIS Standard"

    # --- Field Size Methods ---

    def offset_field_size(self, is_32bit: bool) -> int:
        """Size of offset/displacement fields.

        TIS: 2 bytes for 16-bit records, 4 bytes for 32-bit records.
        """
        return 4 if is_32bit else 2

    def lidata_repeat_count_size(self, is_32bit: bool) -> int:
        """Size of repeat count field in LIDATA.

        TIS: 2 bytes for LIDATA, 4 bytes for LIDATA32.
        """
        return 4 if is_32bit else 2

    # --- SEGDEF Variant Handling ---

    def segdef_has_access_byte(self) -> bool:
        """Whether SEGDEF has an access byte after overlay name index."""
        return False

    def segdef_access_byte_names(self) -> dict[int, str]:
        """Access type names for SEGDEF access byte (bits 0-1)."""
        return {}

    def segdef_extra_align_names(self) -> dict[int, str]:
        """Additional alignment names beyond TIS standard."""
        return {}

    # --- FIXUPP Variant Handling ---

    def fixupp_loc_names(self) -> dict[int, str]:
        """Location type names for FIXUPP records."""
        return {
            0: "Byte(8)",
            1: "Offset(16)",
            2: "Segment(16)",
            3: "Ptr(16:16)",
            4: "HiByte(8)",
            5: "Loader-resolved Offset(16)",
            9: "Offset(32)",
            11: "Ptr(16:32)",
            13: "Loader-resolved Offset(32)",
        }

    # --- Symbol Reference Format ---

    def comdat_uses_inline_name(self) -> bool:
        """Whether COMDAT stores symbol as inline name vs LNAMES index."""
        return False

    def nbkpat_uses_inline_name(self) -> bool:
        """Whether NBKPAT stores symbol as inline name vs LNAMES index."""
        return False

    def linsym_uses_inline_name(self) -> bool:
        """Whether LINSYM stores symbol as inline name vs LNAMES index."""
        return False

    # --- NBKPAT Variant Handling ---

    def nbkpat_loc_names(self) -> dict[int, str]:
        """Location type names for NBKPAT records."""
        return {
            0: "Byte(8)",
            1: "Word(16)",
            2: "DWord(32)",
        }


@dataclass
class PharLapVariant(Variant):
    """PharLap Easy OMF-386 variant for 32-bit DOS extenders."""
    name: str = "PharLap Easy OMF-386"

    def offset_field_size(self, is_32bit: bool) -> int:
        """PharLap: Always 4 bytes, regardless of record type."""
        return 4

    def lidata_repeat_count_size(self, is_32bit: bool) -> int:
        """PharLap: Always 2 bytes, even in LIDATA32."""
        return 2

    def segdef_has_access_byte(self) -> bool:
        """PharLap adds an access byte after overlay name index."""
        return True

    def segdef_access_byte_names(self) -> dict[int, str]:
        """Access type values (bits 0-1 of access byte)."""
        return {
            0: "RO (Read Only)",
            1: "EO (Execute Only)",
            2: "ER (Execute/Read)",
            3: "RW (Read/Write)",
        }

    def segdef_extra_align_names(self) -> dict[int, str]:
        """PharLap adds align type 6 = 4K page."""
        return {
            6: "Page (4K)",
        }

    def fixupp_loc_names(self) -> dict[int, str]:
        """PharLap redefines some location types for 32-bit."""
        return {
            0: "Byte(8)",
            1: "Offset(16)",
            2: "Segment(16)",
            3: "Ptr(16:32)",      # Different from TIS
            4: "HiByte(8)",
            5: "Offset(32)",      # Different from TIS
            9: "Offset(32)",
            11: "Ptr(16:32)",
            13: "Loader-resolved Offset(32)",
        }


@dataclass
class IBMVariant(Variant):
    """IBM LINK386 variant for OS/2 2.x+."""
    name: str = "IBM LINK386"

    def comdat_uses_inline_name(self) -> bool:
        """IBM stores COMDAT symbol as inline name."""
        return True

    def nbkpat_uses_inline_name(self) -> bool:
        """IBM stores NBKPAT symbol as inline name."""
        return True

    def linsym_uses_inline_name(self) -> bool:
        """IBM stores LINSYM symbol as inline name."""
        return True

    def nbkpat_loc_names(self) -> dict[int, str]:
        """IBM adds location type 9."""
        return {
            0: "Byte(8)",
            1: "Word(16)",
            2: "DWord(32)",
            9: "DWord(32-IBM)",
        }


# Singleton instances
TIS_STANDARD = Variant()
PHARLAP = PharLapVariant()
IBM_LINK386 = IBMVariant()
