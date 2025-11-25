"""COMENT class handler registry."""

from collections import defaultdict

COMENT_CLASS_HANDLERS = defaultdict(list)


def coment_class(*classes, features=None):
    """Register a handler for one or more COMENT classes.

    Args:
        *classes: Comment class bytes (e.g., 0x00, 0xA0)
        features: Optional set of feature strings required

    Usage:
        @coment_class(0x00)
        def handle_translator(omf, sub, flags):
            ...
    """
    required_features = features or set()

    def decorator(fn):
        for cls in classes:
            COMENT_CLASS_HANDLERS[cls].append({
                'handler': fn,
                'features': required_features,
            })
        return fn
    return decorator


def get_coment_handler(cls, active_features):
    """Get the best matching handler for a comment class."""
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
from . import microsoft
