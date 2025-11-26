"""COMENT class handler registry."""

from collections import defaultdict
from typing import TypedDict, Callable

from ..protocols import OMFFileProtocol
from ..parsing import RecordParser
from ..models import AnyComentContent

ComentHandler = Callable[[OMFFileProtocol, RecordParser, int, bytes], AnyComentContent | None]


class ComentHandlerEntry(TypedDict):
    handler: ComentHandler
    features: frozenset[str]


COMENT_CLASS_HANDLERS: defaultdict[int, list[ComentHandlerEntry]] = defaultdict(list)


class DuplicateHandlerError(Exception):
    """Raised when multiple handlers are registered at the same priority level."""
    pass


def coment_class(
    *classes: int, features: set[str] | None = None
) -> Callable[[ComentHandler], ComentHandler]:
    """Register a handler for one or more COMENT classes.

    Args:
        *classes: Comment class bytes (e.g., 0x00, 0xA0)
        features: Optional set of feature strings required for this handler

    Handlers with more specific features take priority. If two handlers
    have the same feature specificity, a DuplicateHandlerError is raised.

    Usage:
        @coment_class(0x00)
        def handle_translator(omf, sub, flags):
            ...

        @coment_class(0x00, features={'vendor_x'})
        def handle_translator_vendor_x(omf, sub, flags):
            # Takes priority when 'vendor_x' feature is active
            ...
    """
    required_features = frozenset(features) if features else frozenset()

    def decorator(fn: ComentHandler) -> ComentHandler:
        for cls in classes:
            for existing in COMENT_CLASS_HANDLERS[cls]:
                if existing['features'] == required_features:
                    raise DuplicateHandlerError(
                        f"Duplicate COMENT handler for class 0x{cls:02X} "
                        f"with features {required_features or '(none)'}: "
                        f"{existing['handler'].__name__} and {fn.__name__}"
                    )
            COMENT_CLASS_HANDLERS[cls].append({
                'handler': fn,
                'features': required_features,
            })
        return fn
    return decorator


def get_coment_handler(cls: int, active_features: set[str]) -> ComentHandler | None:
    """Get the best matching handler for a comment class.

    Selects the handler whose required features are all present in
    active_features, preferring handlers with more specific requirements.
    """
    handlers = COMENT_CLASS_HANDLERS.get(cls, [])

    matching = [
        h for h in handlers
        if h['features'] <= active_features
    ]

    if not matching:
        return None

    matching.sort(key=lambda h: len(h['features']), reverse=True)
    return matching[0]['handler']


from . import standard  # Must be first - registers COMENT record handler
from . import intel
from . import watcom
from . import microsoft  # Must be after watcom (imports from it)
