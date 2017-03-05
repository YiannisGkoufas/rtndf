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

import sys

sys.path.append('.')

import RTIMU
import os.path
import time
import math
import getopt
import json

import ManifoldPython
import rtndf.rtndf as rdf
import rtndf.datadefs.imudatadefs as idefs




#  computeHeight() - the conversion uses the formula:
#
#  h = (T0 / L0) * ((p / P0)**(-(R* * L0) / (g0 * M)) - 1)
#
#  where:
#  h  = height above sea level
#  T0 = standard temperature at sea level = 288.15
#  L0 = standard temperatur elapse rate = -0.0065
#  p  = measured pressure
#  P0 = static pressure = 1013.25
#  g0 = gravitational acceleration = 9.80665
#  M  = mloecular mass of earth's air = 0.0289644
#  R* = universal gas constant = 8.31432
#
#  Given the constants, this works out to:
#
#  h = 44330.8 * (1 - (p / P0)**0.190263)

def computeHeight(pressure):
    return 44330.8 * (1 - pow(pressure / 1013.25, 0.190263))

'''
------------------------------------------------------------
    Main code
'''

# set defaults

iniFile = 'RTIMULib'
outTopic = 'imudata'

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:o:' + rdf.manifoldArgOpts)
except:
    print ('python imageproc [-i <iniFile>] [-o <outTopic>]' + rdf.manifoldArgs)
    print ('\nDefaults:')
    print ('  -i RTIMULib\n  -o imageproc')
    print (rdf.manifoldArgsDefaults)
    sys.exit(2)

for opt, arg in opts:
    if opt == '-i':
        iniFile = arg
    if opt == '-o':
        outTopic = arg
        
# start ManifoldPython running

ManifoldPython.start("imu", sys.argv, False)

# this delay is necessary to allow Qt startup to complete
time.sleep(1.0)

# wake up the console
print("imu starting...")
sys.stdout.flush()

# Activate the output stream
outPort = ManifoldPython.addMulticastSource(outTopic)
if (outPort == -1):
    print("Failed to activate output stream")
    ManifoldPython.stop()
    sys.exit()

print("Using ini file " + iniFile + ".ini")
if not os.path.exists(iniFile + ".ini"):
    print("Settings file does not exist, will be created")

s = RTIMU.Settings(iniFile)
imu = RTIMU.RTIMU(s)
pressure = RTIMU.RTPressure(s)
humidity = RTIMU.RTHumidity(s)

print("IMU Name: " + imu.IMUName())
print("Pressure Name: " + pressure.pressureName())
print("Humidity Name: " + humidity.humidityName())

if (not imu.IMUInit()):
    print("IMU Init Failed")
    sys.exit(1)
else:
    print("IMU Init Succeeded");

# this is a good time to set any fusion parameters

imu.setSlerpPower(0.02)
imu.setGyroEnable(True)
imu.setAccelEnable(True)
imu.setCompassEnable(True)

if (not pressure.pressureInit()):
    print("Pressure sensor Init Failed")
else:
    print("Pressure sensor Init Succeeded")

if (not humidity.humidityInit()):
    print("Humidity sensor Init Failed")
else:
    print("Humidity sensor Init Succeeded")

poll_interval = imu.IMUGetPollInterval()
print("Recommended Poll Interval: %dmS\n" % poll_interval)

while True:
    time.sleep(poll_interval*1.0/1000.0)
    if imu.IMURead():
        timestamp = time.time()
        message = rdf.newPublishMessage('imu', outTopic, idefs.DATATYPE, timestamp)
        data = imu.getIMUData()
        (data["pressureValid"], data["pressure"], data["pressureTemperatureValid"], data["pressureTemperature"]) = pressure.pressureRead()
        (data["humidityValid"], data["humidity"], data["humidityTemperatureValid"], data["humidityTemperature"]) = humidity.humidityRead()
        message[idefs.DATA] = data
        if ManifoldPython.isServiceActive(outPort) and ManifoldPython.isClearToSend(outPort):
            ManifoldPython.sendMulticastData(outPort, json.dumps(message), '', timestamp)


ManifoldPython.removeService(outPort)
ManifoldPython.stop()
