from contextlib import contextmanager
from typing import IO


@contextmanager
def midi_relay(path: str) -> (IO, IO):
    with open(path, 'rb') as midi_in:
        with open(path, 'wb') as midi_out:
            print('Opened MIDI streams')
            yield (midi_in, midi_out)


def play_note(midi_out: IO, note: int, velocity: int):
    send_midi(midi_out, b'\x90' + bytes([note, velocity]))


def send_midi(midi_out: IO, b: bytes):
    midi_out.write(b)
    midi_out.flush()
