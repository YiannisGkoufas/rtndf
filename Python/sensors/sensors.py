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

# import the sensor drivers

sys.path.append('../SensorDrivers')

import sensorlib.adxl345 as adxl345
import sensorlib.tsl2561 as tsl2561
import sensorlib.tmp102 as tmp102
import sensorlib.bmp180 as bmp180
import sensorlib.mcp9808 as mcp9808
import sensorlib.htu21d as htu21d
import sensorlib.nullsensor as nullsensor

# The set of sensors. Uncomment one in each class or use NullSensor if no physical sensor
# Multi sensor objects (such as bmp180 for temp and pressure) can be reused

# Acceleration

#accel = nullsensor.nullsensor()
accel = adxl345.adxl345()

# Light

#light = nullsensor.nullsensor()
light = tsl2561.tsl2561()

# Temperature

#temperature = nullsensor.nullsensor()
#temperature = tmp102.tmp102()
#temperature = mcp9808.mcp9808()
temperature = bmp180.bmp180()

# Pressure

#pressure = nullsensor.nullsensor()
pressure = bmp180.bmp180()

# Humidity

#humidity = nullsensor.nullsensor()
humidity = htu21d.htu21d()


'''
------------------------------------------------------------
    Sensor functions
'''

# global to maintain last sensor read time
lastSensorReadTime = time.time() 


def initSensors():
    accel.enable()
    light.enable()
    temperature.enable()
    pressure.enable()
    humidity.enable()

def readSensors():
    global lastSensorReadTime

    if ((time.time() - lastSensorReadTime) < sampleInterval):
        return
    # call background loops
    if accel.sensorValid:
        accel.background()
    if light.sensorValid:
        light.background()
    if temperature.sensorValid:
        temperature.background()
    if pressure.sensorValid:
        pressure.background()
    if humidity.sensorValid:
        humidity.background()

    # time send send the sensor readings
    lastSensorReadTime = time.time()
    
    message = rdf.newPublishMessage('sensors', outTopic, sdefs.DATATYPE, lastSensorReadTime)

    if accel.dataValid:
        accelData = accel.readAccel()
        message[sdefs.ACCEL_DATA] = accelData
        
    if light.dataValid:
        lightData = light.readLight()
        message[sdefs.LIGHT_DATA] = lightData

    if temperature.dataValid:
        temperatureData = temperature.readTemperature()
        message[sdefs.TEMPERATURE_DATA] = temperatureData

    if pressure.dataValid:
        pressureData = pressure.readPressure()
        message[sdefs.PRESSURE_DATA] = pressureData
        
    if humidity.dataValid:
        humidityData = humidity.readHumidity()
        message[sdefs.HUMIDITY_DATA] = humidityData

    if ManifoldPython.isServiceActive(sourcePort) and ManifoldPython.isClearToSend(sourcePort):
        ManifoldPython.sendMulticastData(sourcePort, json.dumps(message), '', lastSensorReadTime)

'''
------------------------------------------------------------
    Main sensor loop loop
'''


def sensorLoop():
    ''' This is the main sensor loop. '''

    while True:
        # see if anything from the sensors
        readSensors()

        # give other things a chance
        time.sleep(0.01)

        '''
------------------------------------------------------------
    Custom arg handler
'''

def processArg(opt, arg):
    global sampleInterval, outTopic

    if opt == '-i':
        sampleInterval = float(arg)
    if opt == '-o':
        outTopic = arg

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

ManifoldPython.start("sensors", sys.argv, False)

# this delay is necessary to allow Qt startup to complete
time.sleep(1.0)

# Activate the source stream
sourcePort = ManifoldPython.addMulticastSource(outTopic)
if (sourcePort == -1):
    print("Failed to activate stream service")
    ManifoldPython.stop()
    sys.exit()

initSensors()

# wake up the console
print("sensors starting...")
sys.stdout.flush()

try:
    sensorLoop()
except:
    traceback.print_exc()

# Exiting so clean everything up.

ManifoldPython.removeService(sourcePort)
ManifoldPython.stop()
