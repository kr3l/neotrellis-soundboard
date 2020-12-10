#!/bin/bash
arecord -Dhw:0 -f dat | sox -t wav -b 16 -r 44100 -e signed - -t wav $1_tmp.wav trim 00:00:00.10 lowpass 9k bandreject 1427 300 bandreject 2870 300 bandreject 4245 300 bandreject 5689 300 bandreject 7089 300 bandreject 8542 300 noisered speech.noise-profile 0.15

# The command first records with arecord (it would be easier to record directly with sox, but this keeps the audio device blocked for a few seconds after recording stops for some reason
# Then pipe into sox
# - which will write out as x_tmp.wav (x passed as first argument)
# - which will trim off the first tenth of a second (whining is loudest in beginning)
# - which applies a low pass filter of 9kHz. Frequencies above 9kHz are dropped. Voice is usually below 8kHz.
# - which applies some specific bandpass filters to reduce the annoying whine
# - which applies a bit of noise reduction
