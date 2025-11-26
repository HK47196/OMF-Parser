"""OMF parser package."""

from .file import OMFFile
from .scanner import Scanner, RecordInfo
from .parsing import RecordParser
from .formatters import HumanFormatter, JSONFormatter
from .models import ParseResult
from .constants import OMFVariant
from .detect import (
    is_omf,
    detect_omf,
    scan_for_omf,
    scan_for_patterns,
    OMFCandidate,
    GREP_PATTERNS,
)

__version__ = "2.0.0"
__all__ = [
    'OMFFile',
    'Scanner',
    'RecordInfo',
    'RecordParser',
    'HumanFormatter',
    'JSONFormatter',
    'ParseResult',
    'OMFVariant',
    'is_omf',
    'detect_omf',
    'scan_for_omf',
    'scan_for_patterns',
    'OMFCandidate',
    'GREP_PATTERNS',
]
