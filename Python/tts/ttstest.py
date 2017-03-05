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
import json

import ManifoldPython
import rtndf.rtndf as rdf
import rtndf.metadefs.rtndfdefs as rtndefs
import rtndf.datadefs.ttsdatadefs as ttsdefs
import rtndf.datadefs.ttscompletedatadefs as ttscompletedefs

'''
------------------------------------------------------------
    Send the text message
'''

def sendMessage():
    global waitForComplete
    
    ret = False    
    
    if (ManifoldPython.isServiceActive(clientPort)):
        ret = ManifoldPython.sendE2EData(clientPort, json.dumps(textMessage), '', time.time())
            
    if ret:
        print('Sent: ' + testText)
        waitForComplete = True
        
'''
------------------------------------------------------------
    check for received completion messages
'''

def processCompletion():
    global completionToProcess, gotCompletion
 
    ret, data, binaryData, timestamp = ManifoldPython.getMulticastData(sinkPort)
    if not ret:
        return
        
    if gotCompletion:
        return
        
    completionToProcess = data
    gotCompletion = True
        
        
        
'''
------------------------------------------------------------
    Main code
'''

# global variables

waitForComplete = False
testText = 'hello'

textTopic = "%s_tts/tts" % platform.node()
completionTopic = "%s_tts/ttscomplete" % platform.node()

gotCompletion = False
completionToProcess = False

try:
    opts, args = getopt.getopt(sys.argv[1:], "c:m:t:")
except:
    print ('python ttstest [-c < completionTopic> [-m <message>] [-t <ttsTopic>]\n')
    print ('Defaults:')
    print ('  -c ' + completionTopic)
    print ('  -m ' + testText)
    print ('  -t ' + textTopic)
    sys.exit(2)

for opt, arg in opts:
    if opt == '-c':
        completionTopic = arg
    if opt == '-m':
        testText = arg
    elif opt == '-t':
        textTopic = arg
        
# start ManifoldPython running

ManifoldPython.start("ttstest", sys.argv, False)

# this delay is necessary to allow Qt startup to complete
time.sleep(1.0)

# wake up the console
print("ttstest starting...")
sys.stdout.flush()

# Activate the client endpoint
clientPort = ManifoldPython.addE2EClient(textTopic)
if (clientPort == -1):
    print("Failed to activate E2E client endpoint")
    ManifoldPython.stop()
    sys.exit()

# Activate the sink endpoint
sinkPort = ManifoldPython.addMulticastSink(completionTopic)
if (sinkPort == -1):
    print("Failed to activate multicast sink endpoint")
    ManifoldPython.stop()
    sys.exit()

lastSendTime = time.time()

textMessage = rdf.newPublishMessage('tts', textTopic, ttsdefs.DATATYPE, time.time())
textMessage[ttsdefs.TEXT] = testText

try:
    while(True):
        # main loop
        
        processCompletion()
        
        if gotCompletion:
            try:
                jsonObj = json.loads(completionToProcess)
                finished = jsonObj[ttscompletedefs.COMPLETE]
                print('Completion status: ' + str(finished))
                if finished:
                    waitForComplete = False
                gotCompletion = False
                    
            except:
                print ("JSON error", sys.exc_info()[0],sys.exc_info()[1])
                continue
        
        now = time.time()
        if (now - lastSendTime) >= 10.0:
            waitForComplete = False
            
        if not waitForComplete:
            sendMessage()
            lastSendTime = now
            
finally:
        pass

# Exiting so clean everything up.    

ManifoldPython.removeService(clientPort)
ManifoldPython.removeService(sinkPort)
ManifoldPython.stop()
print("ttstest exiting")
