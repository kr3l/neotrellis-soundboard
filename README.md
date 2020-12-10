# neotrellis-soundboard

A small sound board made from a raspberry pi zero, a neotrellis and a voice bonnet 


# setup

Follow Adafruit instructions on how to set up the voice bonnet (https://learn.adafruit.com/adafruit-voice-bonnet/overview)

After that:

```sh
pip3 install --upgrade adafruit-circuitpython-dotstar adafruit-circuitpython-neotrellis
python neotrellis.py
```

# sox

## install and record

```
sudo apt-get install sox
```

now record with
(on Pi4 setting the AUDIODEV env var was not necessary, but on pi0w it was)

```
AUDIODEV=hw:0 rec test.wav
```

## bandfilter

Remove annoying whine with bandfilters on 1500Hz and harmonics

```
rec test1.wav bandreject 3000 200 bandreject 1500 200 bandreject 4500 200 bandreject 6000 200 bandreject 7500 200 bandreject 9000 200
```


## Noise filtering

```
sox test.wav -n trim 0 1.0 noiseprof speech.noise-profile
```

```
sox test.wav cleaned.wav noisered speech.noise-profile 0.15
```