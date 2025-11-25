"""OMF parser package."""

from .file import OMFFile
from .scanner import Scanner, RecordInfo
from .parsing import RecordParser

__version__ = "2.0.0"
__all__ = ['OMFFile', 'Scanner', 'RecordInfo', 'RecordParser']
