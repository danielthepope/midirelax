#!/usr/bin/env python3

import asyncio
import random
from asyncio import AbstractEventLoop
from time import time
from typing import IO

from midirelay import midi_relay, play_note, send_midi

NOTES = [40, 47, 52, 54, 56, 59, 64, 66, 68, 71, 76]  # chord E9
TIMINGS = [1244, 553, 362, 1563, 1042, 1883, 638, 1611, 1697, 1042, 2540, 263, 1497, 1423,
           530, 551, 991, 2167, 551, 1992, 759, 533, 391, 668, 1121, 561, 398, 647, 697, 1199]
VELOCITIES = [52, 27, 38, 39, 32, 35, 33, 39, 27, 23, 34, 26, 26, 27,
              19, 27, 46, 25, 24, 39, 25, 33, 38, 35, 35, 36, 37, 39, 40, 37, 50]
PLAYING = True


def setup(midi_out: IO):
    # Piano voice
    with open('piano.syx', 'rb') as f:
        send_midi(midi_out, f.read())
    # Sustain
    with open('sustain-on.syx', 'rb') as f:
        send_midi(midi_out, f.read())

    print('Setup keyboard')


async def play_notes(midi_out: IO):
    while True:
        expected_duration_s = random.choice(TIMINGS) / 1000
        start_time = time()
        if PLAYING:
            note = random.choice(NOTES)
            velocity = random.choice(VELOCITIES)
            play_note(midi_out, note, velocity)
            play_note(midi_out, note, 0)
        await asyncio.sleep(max(expected_duration_s - (time() - start_time), 0))


async def record(midi_in: IO, loop: AbstractEventLoop):
    recording = False
    new_notes = []
    new_velocities = []
    new_timings = []
    global PLAYING
    prev_time = None

    reader = asyncio.StreamReader(loop=loop)
    reader_protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: reader_protocol, midi_in)

    while True:
        command = await reader.read(1)
        if command == b'\xB0':
            # It's a control. Let's get the next two bytes
            command += await reader.read(2)
            if command == b'\xB0\x40\x7F':  # Sustain pedal pressed
                recording = True
                PLAYING = False
                print('Recording')
            elif command == b'\xB0\x40\x00':  # Sustain pedal released
                recording = False
                PLAYING = True
                if len(new_timings) > 0:
                    print('Updating notes')
                    update_notes(new_notes)
                    update_velocities(new_velocities)
                    update_timings(new_timings)
                else:
                    print('Not enough notes played')
                new_notes = []
                new_velocities = []
                new_timings = []
                prev_time = None

        if recording and command == b'\x90':
            # It's a note. Let's get the next two bytes
            command += await reader.read(2)
            # We only care if the key has been pressed. Ignore key release
            if command[2] > 0:
                if prev_time:
                    new_timings.append(int((time() - prev_time) * 1000))
                new_notes.append(command[1])
                new_velocities.append(command[2])
                prev_time = time()


def update_notes(notes):
    global NOTES
    NOTES = notes
    print('new notes:', NOTES)


def update_velocities(velocities):
    global VELOCITIES
    VELOCITIES = velocities
    print('new velocities:', VELOCITIES)


def update_timings(timings):
    global TIMINGS
    TIMINGS = timings
    print('new timings:', TIMINGS)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        with midi_relay('/dev/snd/midiC1D0') as (midi_in, midi_out):
            setup(midi_out)
            loop.create_task(play_notes(midi_out))
            loop.run_until_complete(record(midi_in, loop))
    except Exception:
        loop.close()
