"""OMF format variant definitions.

Variants change how records are parsed (field sizes, extra fields, etc.).
This is distinct from extensions which add new semantics but use the same parsing.

Variants:
- TIS Standard: Baseline OMF-86/286/386 per TIS specification
- PharLap Easy OMF-386: 32-bit DOS extender format with fixed 4-byte offsets
- IBM LINK386: OS/2 2.x+ format with inline names in some records
"""

from dataclasses import dataclass

from .constants import OMFVariant


@dataclass
class Variant:
    """Base TIS Standard OMF variant."""
    omf_variant: OMFVariant = OMFVariant.TIS_STANDARD

    @property
    def name(self) -> str:
        """Return the variant name string."""
        return self.omf_variant.value

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


@dataclass
class PharLapVariant(Variant):
    """PharLap Easy OMF-386 variant for 32-bit DOS extenders."""
    omf_variant: OMFVariant = OMFVariant.PHARLAP

    def offset_field_size(self, is_32bit: bool) -> int:
        """PharLap: Always 4 bytes, regardless of record type."""
        return 4

    def lidata_repeat_count_size(self, is_32bit: bool) -> int:
        """PharLap: Always 2 bytes, even in LIDATA32."""
        return 2

    def segdef_has_access_byte(self) -> bool:
        """PharLap adds an access byte after overlay name index."""
        return True


@dataclass
class IBMVariant(Variant):
    """IBM LINK386 variant for OS/2 2.x+."""
    omf_variant: OMFVariant = OMFVariant.IBM_LINK386

    def comdat_uses_inline_name(self) -> bool:
        """IBM stores COMDAT symbol as inline name."""
        return True

    def nbkpat_uses_inline_name(self) -> bool:
        """IBM stores NBKPAT symbol as inline name."""
        return True

    def linsym_uses_inline_name(self) -> bool:
        """IBM stores LINSYM symbol as inline name."""
        return True


# Singleton instances
TIS_STANDARD = Variant()
PHARLAP = PharLapVariant()
IBM_LINK386 = IBMVariant()
