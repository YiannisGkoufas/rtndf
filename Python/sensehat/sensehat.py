#!/usr/bin/python
'''
////////////////////////////////////////////////////////////////////////////
//
//  This file is part of rtndf
//
//  Copyright (c) 2016, Richard Barnett
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy of
//  this software and associated documentation files (the "Software"), to deal in
//  the Software without restriction, including without limitation the rights to use,
//  copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
//  Software, and to permit persons to whom the Software is furnished to do so,
//  subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in all
//  copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
//  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
//  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
//  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
//  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
//  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

# standard imports

import sys
import time
import traceback
import json
import getopt

import ManifoldPython
import rtndf.rtndf as rdf
import rtndf.datadefs.sensordatadefs as sdefs

from sense_hat import SenseHat
from evdev import InputDevice, list_devices, ecodes

'''
------------------------------------------------------------
    Display code
'''

BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
RED = [255, 0, 0]

# 0, 0 = Top left
# 7, 7 = Bottom right
UP_PIXELS = [[3, 0], [4, 0]]
DOWN_PIXELS = [[3, 7], [4, 7]]
LEFT_PIXELS = [[0, 3], [0, 4]]
RIGHT_PIXELS = [[7, 3], [7, 4]]
CENTRE_PIXELS = [[3, 3], [4, 3], [3, 4], [4, 4]]


def set_pixels(pixels, col):
    for p in pixels:
        sense.set_pixel(p[0], p[1], col[0], col[1], col[2])


'''
------------------------------------------------------------
    Sensor code
'''
# global to maintain last sensor read time
lastSensorReadTime = time.time()

def handle_code(message, code, colour, state):

    if code == ecodes.KEY_DOWN:
        set_pixels(DOWN_PIXELS, colour)
        message[sdefs.JOYSTICK_DATA] = ['down', state]
    elif code == ecodes.KEY_UP:
        set_pixels(UP_PIXELS, colour)
        message[sdefs.JOYSTICK_DATA] = ['up', state]
    elif code == ecodes.KEY_LEFT:
        set_pixels(LEFT_PIXELS, colour)
        message[sdefs.JOYSTICK_DATA] = ['left', state]
    elif code == ecodes.KEY_RIGHT:
        set_pixels(RIGHT_PIXELS, colour)
        message[sdefs.JOYSTICK_DATA] = ['right', state]
    elif code == ecodes.KEY_ENTER:
        set_pixels(CENTRE_PIXELS, colour)
        message[sdefs.JOYSTICK_DATA] = ['enter', state]

def sensorLoop():
    try:
        global lastSensorReadTime

        if ((time.time() - lastSensorReadTime) < sampleInterval):
            return
        lastSensorReadTime = time.time()
        message = rdf.newPublishMessage('sensehat', outTopic, sdefs.DATATYPE, lastSensorReadTime)

        while True:
            event = dev.read_one()
            if (event == None):
                break
            if event.type == ecodes.EV_KEY:
                if event.value == 1:  # key down
                    handle_code(message, event.code, WHITE, 'pressed')
                if event.value == 0:  # key up
                    handle_code(message, event.code, BLACK, 'released')

        orient = sense.get_orientation_radians()
        mag = sense.get_compass_raw()
        accel = sense.get_accelerometer_raw()
        gyro = sense.get_gyroscope_raw()
        message[sdefs.POSE_DATA] = [orient['roll'], orient['pitch'], orient['yaw']]
        message[sdefs.GYRO_DATA] = [gyro['x'], gyro['y'], gyro['z']]
        message[sdefs.ACCEL_DATA] = [accel['x'], accel['y'], accel['z']]
        message[sdefs.MAG_DATA] = [mag['x'], mag['y'], mag['z']]
        message[sdefs.TEMPERATURE_DATA] = sense.get_temperature()
        message[sdefs.HUMIDITY_DATA] = sense.get_humidity()
        message[sdefs.PRESSURE_DATA] = sense.get_pressure()
        message[sdefs.LIGHT_DATA] = 0

        if ManifoldPython.isServiceActive(sourcePort) and ManifoldPython.isClearToSend(sourcePort):
            ManifoldPython.sendMulticastData(sourcePort, json.dumps(message), '', lastSensorReadTime)

    except:
        traceback.print_exc()

'''
------------------------------------------------------------
    Main code
'''

# set defaults

outTopic = "sensor"
sampleInterval = 0.1

sourcePort = -1

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], 'o:i:' + rdf.manifoldArgOpts)
except:
    print ('python sensehat [-i <sampleInterval>] [-o <outTopic>]' + rdf.manifoldArgs)
    print ('\nDefaults:')
    print ('  -i 0.1\n  -o sensor')
    print (rdf.manifoldArgsDefaults)
    sys.exit(2)

for opt, arg in opts:
    if opt == '-i':
        sampleInterval = float(arg)
    if opt == '-o':
        outTopic = arg
        
# start ManifoldPython running

ManifoldPython.start("sensehat", sys.argv, False)

# this delay is necessary to allow Qt startup to complete
time.sleep(1.0)

# Activate the source stream
sourcePort = ManifoldPython.addMulticastSource(outTopic)
if (sourcePort == -1):
    print("Failed to activate stream service")
    ManifoldPython.stop()
    sys.exit()

sense = SenseHat()
sense.clear()  # Blank the LED matrix
sense.set_imu_config(True, True, True)

found = False;
devices = [InputDevice(fn) for fn in list_devices()]
for dev in devices:
    if dev.name == 'Raspberry Pi Sense HAT Joystick':
        found = True;
        break

if not(found):
    print('Raspberry Pi Sense HAT Joystick not found. Aborting ...')
    sys.exit()

sense.show_message("Active", text_colour=RED)

try:
    while True:
        sensorLoop()
        time.sleep(0.01)
except:
    pass

# Exiting so clean everything up.

ManifoldPython.removeService(sourcePort)
ManifoldPython.stop()
