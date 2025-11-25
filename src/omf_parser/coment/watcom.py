"""Watcom COMENT class handlers."""

from . import coment_class
from ..constants import CommentClass
from ..models import ComentProcModel


PROCESSOR_NAMES = {
    '0': '8086',
    '2': '80286',
    '3': '80386+',
}

MEM_MODEL_NAMES = {
    's': 'Small',
    'm': 'Medium',
    'c': 'Compact',
    'l': 'Large',
    'h': 'Huge',
    'f': 'Flat',
}

FP_MODE_NAMES = {
    'e': 'Emulated inline',
    'c': 'Emulator calls',
    'p': '80x87 inline',
}


def parse_proc_model(text: bytes) -> ComentProcModel:
    """Parse processor/model string (shared by 0x9B and 0x9D)."""
    if not text or len(text) < 4:
        return ComentProcModel(
            processor='Unknown',
            processor_raw='',
            mem_model='Unknown',
            mem_model_raw='',
            optimized=False,
            fp_mode='Unknown',
            fp_mode_raw='',
            pic=False,
        )

    proc_raw = chr(text[0])
    model_raw = chr(text[1])
    opt_raw = chr(text[2])
    fp_raw = chr(text[3])
    pic = len(text) >= 5 and chr(text[4]) == 'i'

    return ComentProcModel(
        processor=PROCESSOR_NAMES.get(proc_raw, f'Unknown({proc_raw})'),
        processor_raw=proc_raw,
        mem_model=MEM_MODEL_NAMES.get(model_raw, f'Unknown({model_raw})'),
        mem_model_raw=model_raw,
        optimized=(opt_raw == 'O'),
        fp_mode=FP_MODE_NAMES.get(fp_raw, f'Unknown({fp_raw})'),
        fp_mode_raw=fp_raw,
        pic=pic,
    )


@coment_class(CommentClass.WAT_PROC_MODEL)
def handle_wat_proc_model(omf, sub, flags, text):
    """Watcom Processor & Model info (0x9B)."""
    return parse_proc_model(text)
