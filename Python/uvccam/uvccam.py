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
import time
import getopt
import json

import ManifoldPython
import rtndf.rtndf as rdf
import rtndf.datadefs.videodatadefs as vdefs

'''
------------------------------------------------------------
    Main code
'''

# set defaults

cameraIndex = 0
cameraWidth = 1280
cameraHeight = 720
cameraRate = 30
sourcePort = -1

outTopic = 'video'

try:
    opts, args = getopt.getopt(sys.argv[1:], 'h:n:r:v:w:' + rdf.manifoldArgOpts)
except:
    print ('python uvccam [h - <height>] [-n <cameraNumber>] [-r <rate>] [-v <videoTopic>] [-w <width>]' + rdf.manifoldArgs)
    print ('\nDefaults:')
    print ('  -h 720\n  -n 0\n  -r 30\n  -v video\n  -w 1280')
    print (rdf.manifoldArgsDefaults)
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        cameraHeight = int(arg)
    if opt == '-n':
        cameraIndex = int(arg)
    if opt == '-r':
        cameraRate = int(arg)
    if opt == '-v':
        outTopic = arg
    if opt == '-w':
        cameraWidth = int(arg)


# start ManifoldPython running

ManifoldPython.start("uvccam", sys.argv, True)

# this delay is necessary to allow Qt startup to complete
time.sleep(1.0)

# Activate the source stream
sourcePort = ManifoldPython.addMulticastSource(outTopic)
if (sourcePort == -1):
    print("Failed to activate stream service")
    ManifoldPython.stop()
    sys.exit()

# Open the camera device
if (not ManifoldPython.vidCapOpen(cameraIndex, cameraWidth, cameraHeight, cameraRate)):
    print("Failed to open vidcap")
    ManifoldPython.stop()
    sys.exit()

# set the title if in GUI mode
ManifoldPython.setWindowTitle("Camera stream - " + outTopic)

while(True):
    try:
        # give other things a chance
        time.sleep(0.02)
        # get a frame from the camera
        ret, frame, jpeg, width, height, rate = ManifoldPython.vidCapGetFrame(cameraIndex)
        if (ret):            
            # and display it
            if (jpeg):
                ManifoldPython.displayJpegImage(frame, "")
            else:
                ManifoldPython.displayImage(frame, width, height, "")
            
            timestamp = time.time()
            message = rdf.newPublishMessage('uvccam', outTopic, vdefs.DATATYPE, timestamp)
            message[vdefs.WIDTH] = width
            message[vdefs.HEIGHT] = height
            message[vdefs.RATE] = rate
            if jpeg:
                message[vdefs.FORMAT] = 'mjpeg'
            else:
                message[vdefs.FORMAT] = 'raw'
            if ManifoldPython.isServiceActive(sourcePort) and ManifoldPython.isClearToSend(sourcePort):
                ManifoldPython.sendMulticastData(sourcePort, json.dumps(message), frame, timestamp)

    except:
        print ("Main loop error ", sys.exc_info()[0],sys.exc_info()[1])
        break
        
# Exiting so clean everything up.    

ManifoldPython.vidCapClose(cameraIndex)
ManifoldPython.removeService(sourcePort)
ManifoldPython.stop()

