# MIDI Relax

A Raspberry Pi powered musical keyboard thing that listens to you play, then shuffles it up and spits it back at you.

Reads and writes directly to the MIDI stream at `/dev/snd/midiC1D0`.

Here's a handy(ish) [MIDI reference](https://www.midi.org/specifications/item/table-1-summary-of-midi-message).

This works on my keyboard - a [Yamaha DGX-305](https://www.manualslib.com/manual/196284/Yamaha-Portable-Grand-Dgx-305.html). I don't know how transferrable those MIDI codes are to other keyboard.

Here is a video of it working [on Twitter](https://twitter.com/danielthepope/status/1226546013466394626).

## Instructions

Connect MIDI keyboard to Raspberry Pi using the USB cable. Keyboard also needs a sustain pedal attached.

Go into the `src` directory and run `relax.py`. It starts off playing notes from a default chord, E9.

To record new notes, hold the sustain pedal then press some keys. It will record the notes you play, along with how hard you pressed the notes and the timings in between each note.

Once all the notes have been entered, release the sustain pedal. The Pi will play notes at random using the same velocities and timings you used.

## amidi

I used `amidi` to create the `.syx` files. You can inspect them using, for example, `hexdump -C piano.syx`.

Those `.syx` files might not work with your keyboard (I don't know how transferrable those codes are), so you might want to re-record them for your keyboard.

To create the binary files, use `amidi -p 'hw:1,0,0' -r piano.syx`, perform the action you want on your keyboard, then press ctrl-c to stop recording.
