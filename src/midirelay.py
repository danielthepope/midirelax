from contextlib import contextmanager
from typing import IO


@contextmanager
def midi_relay(path: str) -> (IO, IO):
    with open(path, 'rb') as midi_in:
        with open(path, 'wb') as midi_out:
            print('Opened MIDI streams')
            yield (midi_in, midi_out)
