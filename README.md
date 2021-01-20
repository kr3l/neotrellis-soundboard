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

# sox and arecord combination

One thing was annoying about recording with sox. Recording something went fine. But immediately playing or recording something after that failed. I had to wait about 4 seconds before a second clip could be recorded. This problem didn't arise when using arecord.

So we record with arecord and filter with sox.

```
arecord -Dhw:0 -f dat | sox -t wav -b 16 -r 44100 -e signed - -t wav /tmp/noise.wav bandreject 1500 200 bandreject 3000 200 bandreject 4500 200 bandreject 6000 200
```










# run at boot

(omit sudo if you don't want to run python script as sudo)

```
sudo crontab -e
```

pick nano

then

```
@reboot python3 /home/pi/neotrellis-soundboard/neotrellis.py
```

# Setup part 2: usb audio device

- bought https://www.bol.com/nl/p/3-5mm-to-usb-sound-card-adapter-audio-5-1/9200000058028767/?s2a=
and https://www.amazon.de/gp/product/B06XJCDYHB/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1
- adafruit guide https://learn.adafruit.com/usb-audio-cards-with-a-raspberry-pi/generalplus
- record on the usb device
```arecord --device=hw:1,0 --format S16_LE --rate 44100 -c1 test.wav```
- play out on voice bonnet
```aplay --device=plughw:0,0 test.wav```
