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
import picamera
import getopt
import json

import ManifoldPython
import rtndf.rtndf as rdf
import rtndf.datadefs.videodatadefs as vdefs

# camera parameters - change as required

CAMERA_INDEX = 0


'''
------------------------------------------------------------
    pi camera functions and main loop
'''

# this is used to track when we have a new frame
piCameraLastFrameIndex = -1

mustExit = False;

def piCameraSendFrameHelper(stream, frame):
    ''' do the actual frame processing '''
    global piCameraLastFrameIndex
    
    try:
        # record index of new frame
        piCameraLastFrameIndex = frame.index

        # get the frame data and display it
        stream.seek(frame.position)
        image = stream.read(frame.frame_size)
 
        timestamp = time.time()
        message = rdf.newPublishMessage('picam', outTopic, vdefs.DATATYPE, timestamp)
        message[vdefs.WIDTH] = cameraWidth
        message[vdefs.HEIGHT] = cameraHeight
        message[vdefs.RATE] = cameraRate
        message[vdefs.FORMAT] = 'mjpeg'
        if ManifoldPython.isServiceActive(sourcePort) and ManifoldPython.isClearToSend(sourcePort):
            ManifoldPython.sendMulticastData(sourcePort, json.dumps(message), image, timestamp)
    except:
        print ("Send frame error ", sys.exc_info()[0],sys.exc_info()[1])


def piCameraSendFrame(stream):
    ''' sendFrame checks the circular buffer to see if there is a new frame
    and publish it '''

    global piCameraLastFrameIndex

    with stream.lock:
        if (cameraRate > 10):
            for frame in stream.frames:
                if (frame.index > piCameraLastFrameIndex):
                    piCameraSendFrameHelper(stream, frame)
        else:
            # skip to last frame in iteration
            frame = None
            for frame in stream.frames:
                pass
 
            if (frame is None):
                return
         
            # check to see if this is new
            if (frame.index == piCameraLastFrameIndex):
                return
            piCameraSendFrameHelper(stream, frame)
        
 
def piCameraLoop():
    ''' This is the main loop. '''

    global mustExit

    # Activate the video stream

    with picamera.PiCamera(CAMERA_INDEX) as camera:
        camera.resolution = (cameraWidth, cameraHeight)
        camera.framerate = (cameraRate, 1)

        # need enough buffering to overcome any latency
        stream = picamera.PiCameraCircularIO(camera, seconds = 1)

        # start recoding in mjpeg mode
        camera.start_recording(stream, format = 'mjpeg')

        try:
            while(True):
                # process any new frames
                camera.wait_recording(0)
                piCameraSendFrame(stream)
                
                #give other things a chance
                time.sleep(0.01)
  
        finally:
            camera.stop_recording()
            mustExit = True
          
'''
------------------------------------------------------------
    Main code
'''

# set defaults

cameraIndex = 0
cameraWidth = 1280
cameraHeight = 720
cameraRate = 30

outTopic = 'video'

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], 'h:n:r:v:w:' + rdf.manifoldArgOpts)
except:
    print ('python picam [-h <height] [-n <cameraNumber>] [-r <rate>] [-v <videoTopic>] [-w <width>]' + rdf.manifoldArgs)
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

ManifoldPython.start("picam", sys.argv, False)

# this delay is necessary to allow Qt startup to complete
time.sleep(1.0)

# Activate the source stream
sourcePort = ManifoldPython.addMulticastSource(outTopic)
if (sourcePort == -1):
    print("Failed to activate stream service")
    ManifoldPython.stop()
    sys.exit()

# wake up the console
print("picam starting...")
sys.stdout.flush()

try:
    piCameraLoop()
except:
    if not mustExit:
        print ('No Pi camera found')

# Exiting so clean everything up.

ManifoldPython.removeService(sourcePort)
ManifoldPython.stop()
