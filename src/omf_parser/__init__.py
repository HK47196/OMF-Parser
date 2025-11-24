"""OMF parser package."""

from .omf_parser import OMFCompleteParser
from .constants import MODE_AUTO, MODE_MS, MODE_IBM, MODE_PHARLAP

__version__ = "1.0.0"
__all__ = ['OMFCompleteParser', 'MODE_AUTO', 'MODE_MS', 'MODE_IBM', 'MODE_PHARLAP']
