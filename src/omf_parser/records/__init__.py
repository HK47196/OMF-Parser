"""OMF record handler registry."""

from collections import defaultdict


OMF_RECORD_HANDLERS = defaultdict(list)


def omf_record(*record_types, features=None):
    """Register a handler for one or more OMF record types.

    Args:
        *record_types: Record type bytes (e.g., 0x80, 0x82)
        features: Optional set of feature strings required for this handler.
                  Handler only matches if all required features are active.

    Usage:
        @omf_record(0x80, 0x82)
        def handle_theadr(omf, record):
            ...

        @omf_record(0x98, features={'easy_omf'})
        def handle_segdef_pharlap(omf, record):
            ...
    """
    required_features = features or set()

    def decorator(fn):
        for rec_type in record_types:
            OMF_RECORD_HANDLERS[rec_type].append({
                'handler': fn,
                'features': required_features,
            })
        return fn
    return decorator


def get_record_handler(rec_type, active_features):
    """Get the best matching handler for a record type.

    Selects the handler with the most specific feature requirements
    that are satisfied by the active features.

    Args:
        rec_type: Record type byte
        active_features: Set of active feature strings

    Returns:
        Handler function, or None if no handler matches
    """
    handlers = OMF_RECORD_HANDLERS.get(rec_type, [])

    matching = [
        h for h in handlers
        if h['features'] <= active_features
    ]

    if not matching:
        return None

    matching.sort(key=lambda h: len(h['features']), reverse=True)
    return matching[0]['handler']


from . import standard
from . import data
from . import microsoft
from . import library
from . import obsolete
from .. import coment  # Register COMENT handlers
