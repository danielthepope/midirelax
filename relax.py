#!/usr/bin/env python3

import subprocess
import random
from time import sleep, time
from threading import Thread

NOTES = [52, 54, 56, 59, 64, 66, 68, 71]  # chord E9
MAX_VELOCITY = 58
MIN_VELOCITY = 31
MAX_TIME_MS = 3000
MIN_TIME_MS = 300
PLAYING = True


def send_midi(hex: str):
    subprocess.check_output(['amidi', '-p', 'hw:1,0,0', '--send-hex', hex])


def random_velocity() -> int:
    return random.randint(MIN_VELOCITY, MAX_VELOCITY)


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
        if PLAYING:
            send_midi(random_note_hex(NOTES))
        sleep(random.randint(MIN_TIME_MS, MAX_TIME_MS) / 1000)


def record():
    proc = subprocess.Popen(['amidi', '-p', 'hw:1,0,0', '--dump'], stdout=subprocess.PIPE)
    recording = False
    new_notes = []
    new_velocities = []
    new_timings = []
    global PLAYING
    prev_time = None

    for line in iter(proc.stdout.readline, ''):
        command = str(line.rstrip(), 'utf8')
        if command == 'B1 40 7F':
            recording = True
            PLAYING = False
            print('Recording')
        elif command == 'B1 40 00':
            recording = False
            PLAYING = True
            if len(new_notes) > 0:
                print('Updating notes')
                update_notes(new_notes)
                update_velocities(new_velocities)
                update_timings(new_timings)
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
    global MAX_VELOCITY
    global MIN_VELOCITY
    MAX_VELOCITY = max(velocities)
    MIN_VELOCITY = min(velocities)
    print('new max velocity:', MAX_VELOCITY)
    print('new min velocity:', MIN_VELOCITY)


def update_timings(timings):
    global MAX_TIME_MS
    global MIN_TIME_MS
    MAX_TIME_MS = max(timings)
    MIN_TIME_MS = min(timings)
    print('new max time:', MAX_TIME_MS)
    print('new min time:', MIN_TIME_MS)


if __name__ == "__main__":
    setup()
    thread = Thread(target=play_notes)
    thread.start()
    record()
