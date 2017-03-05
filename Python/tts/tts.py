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
import base64
import subprocess

import ManifoldPython
import rtndf.rtndf as rdf
import rtndf.metadefs.rtndfdefs as rtndefs
import rtndf.datadefs.ttsdatadefs as ttsdefs
import rtndf.datadefs.ttscompletedatadefs as ttscompletedefs


'''
------------------------------------------------------------
    check for received text
'''

def processReceivedText():
    global messageToProcess, sayIt
 
    ret, data, binaryData, timestamp = ManifoldPython.getE2EData(servicePort)
    if not ret:
        return
        
    if sayIt:
        return
        
    messageToProcess = data
    sayIt = True

'''
------------------------------------------------------------
    Main code
'''

# set defaults

textTopic = "tts"
completionTopic = 'ttscomplete'

sayIt = False
messageToProcess = None

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], 'c:i:' + rdf.manifoldArgOpts)
except:
    print ('python tts [-c <completionTopic>] [-i <ttsTopic>]' + rdf.manifoldArgs)
    print ('\nDefaults:')
    print ('  -c %s\n  -i %s\n' % (completionTopic, textTopic))
    print (rdf.manifoldArgsDefaults)
    sys.exit(2)

for opt, arg in opts:
    if opt == '-c':
        completeTopic = arg
    if opt == '-i':
        textTopic = arg

# start ManifoldPython running

ManifoldPython.start("tts", sys.argv, False)

# this delay is necessary to allow Qt startup to complete
time.sleep(1.0)

# wake up the console
print("tts starting...")
sys.stdout.flush()

# Activate the service endpoint
servicePort = ManifoldPython.addE2EService(textTopic)
if (servicePort == -1):
    print("Failed to activate E2E service endpoint")
    ManifoldPython.stop()
    sys.exit()
    
# Activate the multicast endpoint
multiPort = ManifoldPython.addMulticastSource(completionTopic)
if (multiPort == -1):
    print("Failed to activate multicast source endpoint")
    ManifoldPython.stop()
    sys.exit()

try:
    while True:
        processReceivedText()
        if sayIt:
            try:
                jsonObj = json.loads(messageToProcess)
                text = jsonObj[ttsdefs.TEXT]
                print(text)
                if len(text) == 0:
                    sayIt = False
                    continue
                    
            except:
                print ("JSON error", sys.exc_info()[0],sys.exc_info()[1])
                continue

            timestamp = time.time()
            completionMessage = rdf.newPublishMessage('tts', completionTopic, ttscompletedefs.DATATYPE, timestamp)
            completionMessage[ttscompletedefs.COMPLETE] = False
            if ManifoldPython.isServiceActive(multiPort) and ManifoldPython.isClearToSend(multiPort):
                ManifoldPython.sendMulticastData(multiPort, json.dumps(completionMessage), '', timestamp) 
            text = '....' + text
            subprocess.call(['espeak', "-s140 -ven+18 -z",text.encode('utf-8')])
            time.sleep(1)
            completionMessage[ttscompletedefs.COMPLETE] = True
            if ManifoldPython.isServiceActive(multiPort) and ManifoldPython.isClearToSend(multiPort):
                ManifoldPython.sendMulticastData(multiPort, json.dumps(completionMessage), '', timestamp) 
            sayIt = False;
        else:
            time.sleep(0.01)
except:
    print ("Main loop error", sys.exc_info()[0],sys.exc_info()[1])
    pass

# Exiting so clean everything up.   
        
ManifoldPython.removeService(servicePort)
ManifoldPython.removeService(multiPort)
ManifoldPython.stop()

print("Exiting")
