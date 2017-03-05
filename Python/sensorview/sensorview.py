#!/usr/bin/python
"""
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
"""

import sys
import time
import getopt
import platform

import ManifoldPython
import rtndf.rtndf as rdf

import sensorlib.sensorplot as splot
import sensorlib.sensorrecords as srecs


# The topic map contains the mapping between topic and sensor object

topicMap = {}

'''
------------------------------------------------------------
    process received message
'''

def processReceivedMessage():
    global topicMap
    
    while True:
        try:
            ret, data, nothing, timestamp = ManifoldPython.getMulticastData(inPort)
            if not ret:
                return
            topicMap[inTopic].newJSONData(data)

        except:
            print ("Sensor data error", sys.exc_info()[0],sys.exc_info()[1])

'''
------------------------------------------------------------
    Main code
'''

# set defaults

inTopic = "%s_sensehat/sensor" % platform.node()
plotInterval = 1.0

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:p:' + rdf.manifoldArgOpts)
except:
    print ('python sensorview [-i <inTopic>] [-p <plotInterval>]' + rdf.manifoldArgs)
    print ('\nDefaults:')
    print ('  -i %s\n  -p 1.0\n' % (inTopic))
    print (rdf.manifoldArgsDefaults)
    sys.exit(2)

for opt, arg in opts:
    if opt == '-i':
        inTopic = arg
    if opt == '-p':
        plotInterval = int(arg)

# start ManifoldPython running

ManifoldPython.start("avview", sys.argv, False)

# this delay is necessary to allow Qt startup to complete
time.sleep(1.0)

# wake up the console
print("sensorview starting...")
sys.stdout.flush()

topicMap[inTopic] = srecs.SensorRecords(inTopic, plotInterval)

# start up the plotter

sensorPlot = splot.sensorplot()

# lastPlotTime is used to control plot updates
lastPlotTime = time.time() - plotInterval

# Activate the sensor stream
inPort = ManifoldPython.addMulticastSink(inTopic)
if (inPort == -1):
    print("Failed to activate sensor stream")
    ManifoldPython.stop()
    sys.exit()

try:
    while True:
        processReceivedMessage()
        if (time.time() - lastPlotTime) >= plotInterval:
            lastPlotTime = time.time()
            sensorPlot.plot(topicMap.values())
        time.sleep(0.05)
except:
    pass

# Exiting so clean everything up.

ManifoldPython.removeService(inPort)
ManifoldPython.stop()

