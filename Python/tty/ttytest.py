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
import platform

import ManifoldPython
import rtndf.rtndf as rdf
import rtndf.metadefs.rtndfdefs as rtndefs


'''
------------------------------------------------------------
    check for received text
'''

def processReceivedText():
    ret, data, binaryData, timestamp = ManifoldPython.getMulticastData(ttyInPort)
    if not ret:
        return
        
    try:
        print(binaryData)
         
    except:
        print ("JSON error", sys.exc_info()[0],sys.exc_info()[1])
        

'''
------------------------------------------------------------
    Main code
'''

# set defaults

ttyInTopic = "%s_tty/ttyin" % platform.node()
ttyOutTopic = "%s_tty/ttyout" % platform.node()

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:o:' + rdf.manifoldArgOpts)
except:
    print ('python tty [-i <ttyInTopic>] [-o <ttyOutTopic>]' + rdf.manifoldArgs)
    print ('\nDefaults:')
    print ('  -i %s\n  -o %s\n' % (ttyInTopic, ttyOutTopic))
    print (rdf.manifoldArgsDefaults)
    sys.exit(2)

for opt, arg in opts:
    if opt == '-i':
        ttyInTopic = arg
    if opt == '-o':
        ttyOutTopic = arg

# start ManifoldPython running

ManifoldPython.start("ttytest", sys.argv, False)

# this delay is necessary to allow Qt startup to complete
time.sleep(1.0)

# wake up the console
print("ttytest starting...")
sys.stdout.flush()

# Activate the client endpoint
ttyOutPort = ManifoldPython.addE2EClient(ttyOutTopic)
if (ttyOutPort == -1):
    print("Failed to activate E2E client endpoint")
    ManifoldPython.stop()
    sys.exit()
    
# Activate the multicast endpoint
ttyInPort = ManifoldPython.addMulticastSink(ttyInTopic)
if (ttyInPort == -1):
    print("Failed to activate multicast sink endpoint")
    ManifoldPython.stop()
    sys.exit()
    
ManifoldPython.startConsoleInput()

print("Type characters to send:")
        
try:
    while True:
        time.sleep(0.001)
        processReceivedText()
        
        c = ManifoldPython.getConsoleInput()
        if c is None:
            continue
       
        timestamp = time.time()
        inMessage = rdf.newPublishMessage('ttytest', ttyOutTopic, 'ttydatatype', timestamp)

        if ManifoldPython.isServiceActive(ttyOutPort):
            ManifoldPython.sendE2EData(ttyOutPort, json.dumps(inMessage), str(chr(c)), timestamp) 
      
except:
    print ("Main loop error", sys.exc_info()[0],sys.exc_info()[1])

# Exiting so clean everything up.   
        
ManifoldPython.removeService(ttyInPort)
ManifoldPython.removeService(ttyOutPort)
ManifoldPython.stop()

print("Exiting")
