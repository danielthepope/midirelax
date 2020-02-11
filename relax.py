#!/usr/bin/env python3

import subprocess
import random
from time import sleep, time
from threading import Thread

NOTES = [40, 47, 52, 54, 56, 59, 64, 66, 68, 71, 76]  # chord E9
TIMINGS = [1244, 553, 362, 1563, 1042, 1883, 638, 1611, 1697, 1042, 2540, 263, 1497, 1423,
           530, 551, 991, 2167, 551, 1992, 759, 533, 391, 668, 1121, 561, 398, 647, 697, 1199]
VELOCITIES = [52, 27, 38, 39, 32, 35, 33, 39, 27, 23, 34, 26, 26, 27,
              19, 27, 46, 25, 24, 39, 25, 33, 38, 35, 35, 36, 37, 39, 40, 37, 50]
PLAYING = True


def send_midi(hex: str):
    subprocess.check_output(['amidi', '-p', 'hw:1,0,0', '--send-hex', hex])


def random_velocity() -> int:
    return random.choice(VELOCITIES)


def to_hex(i: int) -> str:
    return '%0.2X' % i


def random_note_hex(notes):
    note = to_hex(random.choice(notes))
    velocity = to_hex(random_velocity())
    hexcodes = '90 %s %s' % (note, velocity)
    print(hexcodes)
    return hexcodes


def setup():
    # Piano voice
    with open('piano.txt', 'r') as f:
        send_midi(f.read())
    # Sustain
    with open('sustain.txt', 'r') as f:
        send_midi(f.read())


def play_notes():
    while True:
        expected_duration_s = random.choice(TIMINGS) / 1000
        start_time = time()
        if PLAYING:
            note = random_note_hex(NOTES)
            send_midi(note)
            send_midi(note[0:6] + '00')
        sleep(max(expected_duration_s - (time() - start_time), 0))


def record():
    proc = subprocess.Popen(['amidi', '-p', 'hw:1,0,0', '--dump'], stdout=subprocess.PIPE)
    recording = False
    new_notes = []
    new_velocities = []
    new_timings = []
    global PLAYING
    prev_time = None
    command = ''

    while True:
        character = proc.stdout.read(1).decode('utf-8')
        if character == '\n':
            command = ''
        else:
            command += character
        if len(command) < 8:
            continue
        if command == 'B1 40 7F':  # Sustain pedal pressed
            recording = True
            PLAYING = False
            print('Recording')
        elif command == 'B1 40 00':  # Sustain pedal released
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
        elif recording and command.startswith('90') and not(command.endswith('00')):
            if prev_time:
                new_timings.append(int((time() - prev_time) * 1000))
            parts = command.split(' ')
            new_notes.append(int(parts[1], 16))
            new_velocities.append(int(parts[2], 16))
            prev_time = time()
        print(command)


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
    setup()
    thread = Thread(target=play_notes)
    thread.start()
    record()
