import time
import subprocess
import os
import sys
import signal
import board
import atexit
import adafruit_dotstar
from threading import Timer
from digitalio import DigitalInOut, Direction, Pull

from board import SCL, SDA
import busio
from adafruit_neotrellis.neotrellis import NeoTrellis

button = DigitalInOut(board.D17)
button.direction = Direction.INPUT
button.pull = Pull.UP

abspath = os.path.abspath(sys.argv[0])
dname = os.path.dirname(abspath)
print("change dir to " + dname)
os.chdir(dname)

DOTSTAR_DATA = board.D5
DOTSTAR_CLOCK = board.D6

# leds on voice bonnet
dots = adafruit_dotstar.DotStar(DOTSTAR_CLOCK, DOTSTAR_DATA, 3, brightness=0.2)

# create the i2c object for the trellis
i2c_bus = busio.I2C(SCL, SDA)

# create the trellis
trellis = NeoTrellis(i2c_bus)

# some color definitions
OFF = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

RECORD_AFTER_MS = 400

wasOn = []
recordProcess = False
recordingButton = -1
count = 0
playSilenceProcess = False
playSampleProcess = False

buttonDownSince = -1

for i in range(16):
    wasOn.append(0)

def stopRecording(dropRecording=False):
    global recordProcess
    global recordingButton
    global playSilenceProcess
    if not(recordProcess):
        return
    if (recordingButton<0):
        return
    print("STOP RECORD " + str(recordingButton))
    os.killpg(recordProcess.pid, signal.SIGTERM)
    recordProcess.terminate()
    recordProcess = None
    #playSilenceProcess.terminate()
    #playSilenceProcess = None
    wasOn[recordingButton] = 0
    if (not dropRecording):
        try:
            os.remove(str(recordingButton) + ".wav")
        except:
            pass
        os.rename(str(recordingButton) + "_tmp.wav", str(recordingButton) + ".wav")
    recordingButton = -1
    for j in range(3):
        dots[j] = (0, 0, 0)
    dots.show()

def startRecording(buttonNumber):
    global recordProcess
    global recordingButton
    global count
    global playSilenceProcess
    count = count + 1
    wasOn[buttonNumber] = 0
    stopRecording()
    recordingButton = buttonNumber
    print("START RECORD " + str(buttonNumber))
    filename = str(buttonNumber) + ".wav"
    # env with AUDIODEV var set for sox
    myoutput = open(filename + "-record.log",'w+')
    myoutput2 = open(filename + "-recorderr.log",'w+')
    # recordProcess = subprocess.Popen(["arecord", "-f", "cd", "-Dhw:0", "-t", "wav", filename], shell=False, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    # subprocess.Popen(my_command, env=my_env)
    #recordProcess = subprocess.Popen(["rec", filename, "-V4"], env=my_env, shell=False, stdout=myoutput, stderr=myoutput2, preexec_fn=os.setsid)
    #playSilenceProcess = subprocess.Popen(["aplay", "silence2.wav"], stdout=myoutput, stderr=myoutput2, preexec_fn=os.setsid)
    recordProcess = subprocess.Popen([dname + "/record.sh", str(buttonNumber)], shell=False, stdout=myoutput, stderr=myoutput2, preexec_fn=os.setsid)
    for j in range(3):
        dots[j] = (255, 0, 0)
    dots.show()

def playRecording(buttonNumber):
    global playSampleProcess
    print("PLAY RECORD " + str(buttonNumber))
    playSampleProcess = subprocess.Popen(["aplay", "-Dplughw:0,0", str(buttonNumber) + ".wav"], shell=False, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    print("after play")

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

# this will be called when button events are received
def blink(event):
    global wasOn
    global recordProcess
    # turn the LED on when a rising edge is detected
    if event.edge == NeoTrellis.EDGE_RISING:
        trellis.pixels[event.number] = wheel(event.number * 16)
    # turn the LED off when a rising edge is detected
    elif event.edge == NeoTrellis.EDGE_FALLING:
        trellis.pixels[event.number] = OFF
    
    if event.edge == NeoTrellis.EDGE_RISING:
        #print("START RECORD " + str(event.number))
        #startRecording(str(event.number) + ".wav")
        wasOn[event.number] = int(time.time() * 1000)
        #output, err = recordProcess.communicate()
    elif event.edge == NeoTrellis.EDGE_FALLING:
        now = int(time.time() * 1000)
        diff = (now - wasOn[event.number])
        wasOn[event.number] = 0
        if diff < 200:
            playRecording(event.number)
            stopRecording(True)
        s = Timer(0.3, stopRecording, ())
        s.start()
        #stopRecording()

for i in range(16):
    # activate rising edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_RISING)
    # activate falling edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_FALLING)
    # set all keys to trigger the blink callback
    trellis.callbacks[i] = blink

    # cycle the LEDs on startup
    trellis.pixels[i] = PURPLE
    time.sleep(0.05)

for i in range(16):
    trellis.pixels[i] = OFF
    time.sleep(0.05)

def cleanup():
    print("cleanup!")
    stopRecording()

atexit.register(cleanup)

while True:
    # check if a button is down for more than 200ms
    now = int(time.time() * 1000)
    if not button.value:
        if buttonDownSince == -1:
            buttonDownSince = now
    elif button.value and buttonDownSince != -1:
        buttonDownSince = -1
    if buttonDownSince != -1:
        if (now - buttonDownSince) > 2000 and (now - buttonDownSince) < 5000:
            print("shutdown")
            buttonDownSince = now - 5000
            playSampleProcess = subprocess.Popen(["aplay", "-Dplughw:0,0", "shutdown.wav"], shell=False, stderr=subprocess.PIPE, preexec_fn=os.setsid)
        if (now - buttonDownSince) > 7000:
            buttonDownSince = -1
            subprocess.call("sudo nohup shutdown -h now", shell=True)
    for i in range(16):
        if wasOn[i] > 0:
            diff = now - wasOn[i]
            if (diff > RECORD_AFTER_MS):
                startRecording(i)
                break

    # call the sync function call any triggered callbacks
    trellis.sync()
    
    # the trellis can only be read every 17 millisecons or so
    time.sleep(0.02)
