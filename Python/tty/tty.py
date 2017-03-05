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
import json
import getopt
import serial

import ManifoldPython
import rtndf.rtndf as rdf
import rtndf.metadefs.rtndfdefs as rtndefs


'''
------------------------------------------------------------
    check for received text
'''

def processReceivedText():
    ret, data, binaryData, timestamp = ManifoldPython.getE2EData(ttyOutPort)
    if not ret:
        return
        
    try:
        serialPort.write(binaryData)
         
    except:
        print ("JSON error", sys.exc_info()[0],sys.exc_info()[1])
        

'''
------------------------------------------------------------
    Main code
'''

# set defaults

ttyOutTopic = "ttyout"
ttyInTopic = 'ttyin'
ttyRate = 115200
ttyPort = '/dev/ttyACM0'

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:o:p:r:' + rdf.manifoldArgOpts)
except:
    print ('python tty [-i <ttyInTopic>] [-o <ttyOutTopic>] [-p <port>] [-r <rate>]' + rdf.manifoldArgs)
    print ('\nDefaults:')
    print ('  -i %s\n  -o %s\n  -p %s\n  -r %d\n' % (ttyInTopic, ttyOutTopic, ttyPort, ttyRate))
    print (rdf.manifoldArgsDefaults)
    sys.exit(2)

for opt, arg in opts:
    if opt == '-i':
        ttyInTopic = arg
    if opt == '-o':
        ttyOutTopic = arg
    if opt == 'p':
        ttyPort = arg
    if opt == 'r':
        ttyRate = int(arg)

# start ManifoldPython running

ManifoldPython.start("tty", sys.argv, False)

# this delay is necessary to allow Qt startup to complete
time.sleep(1.0)

# wake up the console
print("tty starting...")
sys.stdout.flush()

# Activate the service endpoint
ttyOutPort = ManifoldPython.addE2EService(ttyOutTopic)
if (ttyOutPort == -1):
    print("Failed to activate E2E service endpoint")
    ManifoldPython.stop()
    sys.exit()
    
# Activate the multicast endpoint
ttyInPort = ManifoldPython.addMulticastSource(ttyInTopic)
if (ttyInPort == -1):
    print("Failed to activate multicast source endpoint")
    ManifoldPython.stop()
    sys.exit()
        
serialPort = serial.Serial(ttyPort, ttyRate, timeout=0)

try:
    while True:
        processReceivedText()
        
        readBytes = serialPort.read(256)
        if len(readBytes) > 0:
            timestamp = time.time()
            inMessage = rdf.newPublishMessage('tty', ttyInTopic, 'tty', timestamp)
 
            if ManifoldPython.isServiceActive(ttyInPort) and ManifoldPython.isClearToSend(ttyInPort):
                ManifoldPython.sendMulticastData(ttyInPort, json.dumps(inMessage), readBytes, timestamp) 
      
        time.sleep(0.001)
except:
    print ("Main loop error", sys.exc_info()[0],sys.exc_info()[1])

# Exiting so clean everything up.   
        
ManifoldPython.removeService(ttyInPort)
ManifoldPython.removeService(ttyOutPort)
serialPort.close()
ManifoldPython.stop()

print("Exiting")
