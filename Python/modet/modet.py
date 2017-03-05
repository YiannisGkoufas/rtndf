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

This code is based on some ideas here:
    http://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/

'''

import time
import json
import sys
import getopt
import platform

import cv2
import numpy as np

import ManifoldPython
import rtndf.rtndf as rdf
import rtndf.datadefs.videodatadefs as vdefs
import rtndf.metadefs.rtndfdefs as rtndefs
import rtndf.metadefs.modetdefs as mdefs

'''
------------------------------------------------------------
    process an incoming message
'''

def processReceivedMessage():
    global processing, jsonToProcess, imageToProcess, imageTS

    ret, data, image, timestamp = ManifoldPython.getMulticastData(inPort)
    if not ret:
        return
    try:
        jsonObj = json.loads(data)

        if not processing:
            jsonToProcess = jsonObj
            imageToProcess = image
            imageTS = timestamp
            processing=True

    except:
        print ("JSON error", sys.exc_info()[0],sys.exc_info()[1])

'''
------------------------------------------------------------
    Main code
'''

# set defaults

inTopic = "%s_uvccam/video" % platform.node()
outTopic = 'modet'
jsonToProcess = None
imageToProcess = None
imageTS = time.time()
processing = False

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:o:' + rdf.manifoldArgOpts)
except:
    print ('python modet [-i <inTopic>] [-o <outTopic>]' + rdf.manifoldArgs)
    print ('\nDefaults:')
    print ('  -i %s\n  -o modet' % inTopic)
    print (rdf.manifoldArgsDefaults)
    sys.exit(2)

for opt, arg in opts:
    if opt == '-i':
        inTopic = arg
    if opt == '-o':
        outTopic = arg
        
# start ManifoldPython running

ManifoldPython.start("modet", sys.argv, False)

# this delay is necessary to allow Qt startup to complete
time.sleep(1.0)

# wake up the console
print("modet starting...")
sys.stdout.flush()

#   Tuning factors. The default values seem to work well at 1280 x 720 frame size, 30fps.

# This is how much to scale down the image before background subtraction. Bigger images need bigger factors
scaleFactor = 6

# This controls the length of the history used by the background subtractor - adjust for frame rate
bgHistory = 200

# This controls the amount of change needed to trigger the foreground mode
bgThreshold = 16

# This controls blur kernel size applied to the mask before contour detection
blurMaskKernel = 9

# This controls the number of dilate iterations to help the contour detection
dilateIterations = 4

# This controls the minimum contour area that will be accepted
minContourArea = 300

# This controls the thresholding applied before contour detection
maskThreshold = 8

# Activate the input stream
inPort = ManifoldPython.addMulticastSink(inTopic)
if (inPort == -1):
    print("Failed to activate input stream")
    ManifoldPython.stop()
    sys.exit()

# Activate the output stream
outPort = ManifoldPython.addMulticastSource(outTopic)
if (outPort == -1):
    print("Failed to activate output stream")
    ManifoldPython.stop()
    sys.exit()

try:
#   Create the background subtractor
    fgbg = cv2.createBackgroundSubtractorMOG2(bgHistory, bgThreshold, False)

    while True:
        processReceivedMessage()
        if (processing):
            try:
                image = imageToProcess

            except:
                print ("video data error", sys.exc_info()[0],sys.exc_info()[1])

            try:
                # convert the image to a numpy array
                inJpeg = np.frombuffer(image, dtype=np.uint8)

                # decode the jpeg
                inImage = cv2.imdecode(inJpeg, cv2.IMREAD_COLOR)

                # scale the image size down
                inSmallImage = cv2.resize(inImage, (0,0), fx=1./scaleFactor, fy=1./scaleFactor)

                # use the background subtractor to generate a mask
                fgMask = fgbg.apply(inSmallImage)

                # create the blurred version
                blurMask = cv2.GaussianBlur(fgMask, (blurMaskKernel, blurMaskKernel), 0)

                # threshold the result
                retVal, threshMask = cv2.threshold(blurMask, maskThreshold, 255, cv2.THRESH_BINARY)

                # dilate the mask to fill holes
                dilateMask = cv2.dilate(threshMask, None, iterations = dilateIterations)

                # no detect the contours
                contourImage, contours, hierarchy = cv2.findContours(dilateMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                try:
                    metadata = jsonToProcess[rtndefs.METADATA]
                except:
                    metadata = {}

                try:
                    modetarray = metadata[mdefs.TYPE]
                except:
                    modetarray = []

                modetindex = len(modetarray)
               
                for contour in contours:
                    if cv2.contourArea(contour) < minContourArea:
                        continue
                    (x, y, w, h) = cv2.boundingRect(contour)

                    x = int(x * scaleFactor)
                    y = int(y * scaleFactor)
                    w = int(w * scaleFactor)
                    h = int(h * scaleFactor)

                    modetarrayentry = {}
                    modetarrayentry[mdefs.REGION_X] = x
                    modetarrayentry[mdefs.REGION_Y] = y
                    modetarrayentry[mdefs.REGION_W] = w
                    modetarrayentry[mdefs.REGION_H] = h
                    modetarrayentry[mdefs.INDEX] = modetindex
                    modetindex += 1
#                    subImage = inImage[y:(y+h), x:(x+w)]
#                    if len(subImage) == 0:
#                        continue
#                    cv2.imshow('subImage', subImage)
#                    cv2.waitKey(1)

#                    retVal, subJpeg = cv2.imencode('.jpeg', subImage)
#                    binSubImage = base64.b64encode(subJpeg)
#                    modetarrayentry[mdefs.JPEG] = binSubImage
                    modetarray.append(modetarrayentry)

                    # draw the box in the original image

                    cv2.rectangle(inImage, (x, y), (x+w, y+h), (0, 255, 0), 2)
 
                metadata[mdefs.TYPE] = modetarray
                jsonToProcess[rtndefs.METADATA] = metadata

                retVal, outJpeg = cv2.imencode('.jpeg', inImage)
                jsonToProcess[rtndefs.TOPIC] = outTopic
                if ManifoldPython.isServiceActive(outPort) and ManifoldPython.isClearToSend(outPort):
                    ManifoldPython.sendMulticastData(outPort, json.dumps(jsonToProcess), outJpeg, imageTS)


            except:
                print ("Processing error", sys.exc_info()[0],sys.exc_info()[1])
                
            processing = False
        time.sleep(0.01)
except:
    print ("Main loop error", sys.exc_info()[0],sys.exc_info()[1])
    pass

ManifoldPython.removeService(inPort)
ManifoldPython.removeService(outPort)
ManifoldPython.stop()
