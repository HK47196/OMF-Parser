"""Vendor-specific OMF extension handlers."""

from abc import ABC
import pkgutil
import importlib
import os


class VendorExtension(ABC):
    """Base class for vendor-specific OMF extension.

    Each extension handles a specific vendor feature (e.g., a single COMENT class,
    a format behavior modification, etc.). Extensions are organized by vendor in
    separate modules.
    """

    vendor_name = "Unknown"
    extension_name = "Unknown Extension"

    def is_active(self, parser):
        """Return True if this extension should be active for the current file.

        Most extensions return True (always available).
        Extensions that modify parsing behavior may check parser.target_mode.

        Args:
            parser: The OMFCompleteParser instance

        Returns:
            bool: True if this extension is active
        """
        return True

    def get_offset_field_size(self, parser, is_32bit):
        """Override offset field size calculation if needed.

        Used by extensions (like PharLap) that change the size of
        offset/length fields in data records.

        Args:
            parser: The OMFCompleteParser instance
            is_32bit: True if processing a 32-bit record type

        Returns:
            int: Field size (2 or 4), or None to use default behavior
        """
        return None

    def handle_coment(self, parser, sub, cls, flags, text):
        """Handle COMENT record for this vendor extension.

        Args:
            parser: The OMFCompleteParser instance
            sub: Sub-parser for record content
            cls: Comment class byte
            flags: Comment flags byte
            text: Remaining comment text (may be empty bytes)

        Returns:
            bool: True if handled, False to continue checking other extensions
        """
        return False

    def handle_segdef_extension(self, parser, sub, is_32bit, seg_info):
        """Handle vendor-specific SEGDEF extensions.

        Some vendors add extra fields to SEGDEF records.

        Args:
            parser: The OMFCompleteParser instance
            sub: Sub-parser for record content (positioned after standard fields)
            is_32bit: True if SEGDEF32
            seg_info: Dict with segment information parsed so far

        Returns:
            dict or None: Additional segment info to merge, or None
        """
        return None

    def handle_fixupp_location_type(self, parser, loc_type):
        """Translate vendor-specific FIXUPP location types.

        Some vendors define additional location types beyond the standard set.

        Args:
            parser: The OMFCompleteParser instance
            loc_type: Raw location type value (0x00-0x0F)

        Returns:
            tuple or None: (type_name, size_bytes) or None for default handling
        """
        return None

    def handle_lidata_repeat_count_size(self, parser, is_32bit):
        """Override LIDATA repeat count field size if needed.

        PharLap uses 2-byte repeat counts even in LIDATA32, unlike standard.

        Args:
            parser: The OMFCompleteParser instance
            is_32bit: True if LIDATA32

        Returns:
            int: Field size in bytes (2 or 4), or None for default
        """
        return None

    def handle_vendext(self, parser, sub, vendor_num):
        """Handle VENDEXT record for this vendor.

        VENDEXT (0xCE) is the modern standardized way to add vendor extensions.

        Args:
            parser: The OMFCompleteParser instance
            sub: Sub-parser for record content
            vendor_num: Vendor number from record

        Returns:
            bool: True if handled, False to continue
        """
        return False


def _discover_extensions():
    """Auto-discover all extension classes from vendor modules.

    Recursively scans pharlap/, microsoft/, borland/, intel/ directories
    and finds all VendorExtension subclasses.

    Returns:
        list: Extension instances sorted by vendor and extension name
    """
    extensions = []

    # Get path to extensions package
    extensions_path = os.path.dirname(__file__)

    # Iterate through vendor packages
    for entry in os.listdir(extensions_path):
        vendor_path = os.path.join(extensions_path, entry)

        # Skip non-directories and __pycache__
        if not os.path.isdir(vendor_path) or entry.startswith('_'):
            continue

        # Recursively find all .py files in vendor directory
        for root, dirs, files in os.walk(vendor_path):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if not d.startswith('_')]

            for filename in files:
                if not filename.endswith('.py') or filename.startswith('_'):
                    continue

                # Build module path
                rel_path = os.path.relpath(os.path.join(root, filename), extensions_path)
                module_parts = rel_path.replace(os.sep, '.').rsplit('.py', 1)[0]
                module_name = f'omf_parser.handlers.extensions.{module_parts}'

                try:
                    # Import module
                    module = importlib.import_module(module_name)

                    # Find VendorExtension subclasses
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and
                            issubclass(attr, VendorExtension) and
                            attr is not VendorExtension):
                            extensions.append(attr())
                except Exception as e:
                    # Print error but continue discovery
                    print(f"Warning: Failed to load extension module {module_name}: {e}")

    # Sort by vendor and extension name for consistent ordering
    return sorted(extensions, key=lambda ext: (ext.vendor_name, ext.extension_name))


# Build registry on import
# This will be populated once vendor extensions are created
EXTENSION_REGISTRY = []


def _initialize_registry():
    """Initialize the extension registry.

    Called by OMFCompleteParser on first use to avoid circular imports.
    """
    global EXTENSION_REGISTRY
    if not EXTENSION_REGISTRY:
        EXTENSION_REGISTRY = _discover_extensions()
