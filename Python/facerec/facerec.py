#!/usr/bin/env python2

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

This code is based on the OpenFace web demo at:

    https://github.com/cmusatyalab/openface

Original header:

# Copyright 2015-2016 Carnegie Mellon University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""


import os
import sys
import time
import copy

fileDir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(fileDir, "..", ".."))

import cv2
import imagehash
import json
from PIL import Image
import numpy as np
import StringIO
import pickle
import threading
import platform
import getopt

from sklearn.decomposition import PCA
from sklearn.grid_search import GridSearchCV
from sklearn.manifold import TSNE
from sklearn.svm import SVC

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm

import openface

import ManifoldPython
import rtndf.rtndf as rdf
import rtndf.datadefs.videodatadefs as vdefs
import rtndf.metadefs.rtndfdefs as rtndefs
import rtndf.metadefs.modetdefs as mdefs

modelDir = os.path.join(fileDir)
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')
openfaceDBDir =  '/.config/Manifold/facerec'

globalSvm = None
globalImages = {}
globalPeople = []

param_grid = [
                {'C': [1, 10, 100, 1000],
                 'kernel': ['linear']},
                {'C': [1, 10, 100, 1000],
                 'gamma': [0.001, 0.0001],
                 'kernel': ['rbf']}
            ]


class Face:

    def __init__(self, rep, identity):
        self.rep = rep
        self.identity = identity

    def __repr__(self):
        return "{{id: {}, rep[0:5]: {}}}".format(
            str(self.identity),
            self.rep[0:5]
        )


'''
------------------------------------------------------------
    process incoming message
'''

def processReceivedMessage():
    # have to throw away frames to ensure queue empty - processing load is too high
    # in some cases for the forwarding to work correctly
    while True:
        global processingFaceRec, faceRecMessage, faceRecImage, 
        processingForward, forwardMessage, forwardImage, forwardTS, inPort
        
        ret, data, image, timestamp = ManifoldPython.getMulticastData(inPort)
        if not ret:
            return
    
        try:
            if processingForward:
                continue
                
            jsonObj = json.loads(data)

            if not processingFaceRec:
                faceRecMessage = copy.deepcopy(jsonObj)
                faceRecImage = image
                processingFaceRec=True

            if not processingForward:
                forwardMessage = copy.deepcopy(jsonObj)
                forwardImage = image
                forwardTS = timestamp
                processingForward=True
                
        except:
            print ("Receive JSON error", sys.exc_info()[0],sys.exc_info()[1])
            return

'''
------------------------------------------------------------
    thread to handle message forwarding
'''

def forwardThread():
    global processingForward, forwardMessage, forwardImage, forwardTS, forwardThreadExit, inPort

    # start ManifoldPython running

    ManifoldPython.start("facerec", sys.argv, False)

    # this delay is necessary to allow Qt startup to complete
    time.sleep(1.0)
    
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

    while not forwardThreadExit:
        time.sleep(0.01)
        processReceivedMessage()       
        if not processingForward:
            continue
        
        try:
            image = forwardImage
            inJpeg = np.frombuffer(image, dtype=np.uint8)
            cv2Image = cv2.imdecode(inJpeg, cv2.IMREAD_COLOR)

        except:
            print ("Forward jpeg error", sys.exc_info()[0],sys.exc_info()[1])

        try:
            dataLock.acquire()
            for detectedData in globalDetectedData:
                name = detectedData['name']
                namepos = detectedData['namepos']

                cv2.putText(cv2Image, name, namepos,
                    cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.75,
                    color=(152, 255, 204), thickness=2)

                landMarks = detectedData['landmarks']

                for landMark in landMarks:
                    cv2.circle(cv2Image, center=landMark, radius=3,
                       color=(102, 204, 255), thickness=-1)
        except:
            pass

        dataLock.release()

        # generate the output jpeg
        retVal, outJpeg = cv2.imencode('.jpeg', cv2Image)

        forwardMessage[rtndefs.TOPIC] = outTopic
        if ManifoldPython.isServiceActive(outPort) and ManifoldPython.isClearToSend(outPort):
            ManifoldPython.sendMulticastData(outPort, json.dumps(forwardMessage), outJpeg, forwardTS)
        processingForward = False

    ManifoldPython.removeService(inPort)
    ManifoldPython.removeService(outPort)
    ManifoldPython.stop()            
'''
------------------------------------------------------------
    openface code
'''

def getData():
    X = []
    y = []
    for img in globalImages.values():
        X.append(img.rep)
        y.append(img.identity)
            
    numIdentities = len(set(y + [-1])) - 1
    if numIdentities == 0:
        print("numIdentities == 0")
        return None
        
    X = np.vstack(X)
    y = np.array(y)
    return (X, y)

def trainSVM():
    global globalSvm, globalImages, globalPeople
        
    print("+ Training SVM on {} labeled images.".format(len(globalImages)))
    d = getData()
    if d is None:
        globalSvm = None
        return
    else:
        (X, y) = d
        numIdentities = len(set(y + [-1]))
        if numIdentities > 1:
            globalSvm = GridSearchCV(SVC(C=1, probability=True), param_grid, cv=5).fit(X, y)
             
        # save the trained data set
            
        print("Saving training data")
        pickle.dump(globalPeople, open(openfaceDBDir + '/ofpeople.ini', 'wb'))
        pickle.dump(globalImages, open(openfaceDBDir + '/ofimages.ini', "wb"))
            
def processFrame(recJpeg, origImage, origWidth, origHeight, origX, origY):
    global globalSvm, globalImages, globalPeople, globalTraining, globalDetectedData

    try:
        imgF = StringIO.StringIO()
        imgF.write(recJpeg)
        imgF.seek(0)
        bigImage = Image.open(imgF)
    except:
        print("Failed to decode image")
        return

    bis = bigImage.size

    if (bis[0] is 0) or (bis[1] is 0):
        return

    scaleFactor = bis[0] / 300
    if scaleFactor < 1:
        scaleFactor = 1

    smallImageX = bis[0] / scaleFactor
    smallImageY = bis[1] / scaleFactor
    smallImage = bigImage.resize((smallImageX, smallImageY))
    buf = np.asarray(smallImage)
    rgbFrame = np.zeros((smallImageY, smallImageX, 3), dtype=np.uint8)
    rgbFrame[:, :, 0] = buf[:, :, 2]
    rgbFrame[:, :, 1] = buf[:, :, 1]
    rgbFrame[:, :, 2] = buf[:, :, 0]

    identities = []
    bb = align.getLargestFaceBoundingBox(rgbFrame)
    bbs = [bb] if bb is not None else []

    detectedData = {}
    detectedLandmarks = []

    for bb in bbs:

        landmarks = align.findLandmarks(rgbFrame, bb)
        alignedFace = align.align(openFaceImageDim, rgbFrame, bb,
                                  landmarks=landmarks,
                                  landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        if alignedFace is None:
            continue

        phash = str(imagehash.phash(Image.fromarray(alignedFace)))
        if phash in globalImages:
            identity = globalImages[phash].identity
        else:
            rep = net.forward(alignedFace)
            if globalTraining:
                globalImages[phash] = Face(rep, identity)
                trainSVM()
                return []
            else:
                if len(globalPeople) == 0:
                    identity = -1
                elif len(globalPeople) == 1:
                    identity = 0
                elif globalSvm:
                    probs = globalSvm.predict_proba(rep.reshape(1,-1))[0]
                    print(probs)
                    maxProb = -1
                    bestIndex = -1
                    personIndex = 0
                    for prob in probs:
                        if prob > maxProb:
                            maxProb = prob
                            bestIndex = personIndex
                        personIndex += 1
                    if maxProb < probThresh:
                        identity = -1
                    else:
                        identity = bestIndex                           
                else:
                    identity = -1
                if identity not in identities:
                    identities.append(identity)

        for p in openface.AlignDlib.OUTER_EYES_AND_NOSE:
            scaledCenter = (origX + landmarks[p][0] * scaleFactor,
                            origY + landmarks[p][1] * scaleFactor)
            detectedLandmarks.append(scaledCenter)

        if identity == -1:
            if len(globalPeople) == 1:
                name = globalPeople[0]
            else:
                name = "Unknown"
        else:
            name = globalPeople[identity]
                
        detectedData['name'] = name
        detectedData['namepos'] = (origX + bb.left() * scaleFactor, origY + bb.top() * scaleFactor)
        print("Detected: {}".format(name))

        detectedData['landmarks'] = detectedLandmarks

    return detectedData

def getGlobalData():
    X = []
    y = []
    for img in globalImages.values():
        X.append(img.rep)
        y.append(img.identity)

    numIdentities = len(set(y + [-1])) - 1
    if numIdentities == 0:
        return None

    X = np.vstack(X)
    y = np.array(y)
    return (X, y)

'''
------------------------------------------------------------
    Main code
'''

# set defaults

inTopic = "%s_uvccam/video" % platform.node()
outTopic = 'facerec'
useModet = False
inPort = -1
outPort = -1

globalTraining = False

openFaceImageDim = 96

# probability threshold is used to decide if a match is signifcant

probThresh = 0.85

# this flag is set when there is a new JSON message that needs face recognition

processingFaceRec = False

# this is the JSON to process

faceRecMessage = None
faceRecImage = None

# this flag is set when there is a new message to forward

processingForward = False

# this is the message

forwardMessage = None
forwardImage = None
forwardTS = time.time()

# this lock is used to prevent slivering when using face detect metadata

dataLock = threading.Lock()

# this is the data that is protected

globalDetectedData = []

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:mo' + rdf.manifoldArgOpts)
except:
    print ('python facerec [-i <inTopic>]  [-m] [-o <outTopic>]' + rdf.manifoldArgs)
    print ('\nDefaults:')
    print ('  -i %s\n  -m if present use modet regions\n  -o facerec' % (inTopic))
    print (rdf.manifoldArgsDefaults)
    sys.exit(2)

for opt, arg in opts:
    if opt == '-i':
        inTopic = arg
    if opt == '-o':
        outTopic = arg
    if opt == '-m':
        useModet = True

# wake up the console
print("facerec starting...")
sys.stdout.flush()

align = openface.AlignDlib(os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))
net = openface.TorchNeuralNet(os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'),
                              imgDim=openFaceImageDim,
                              cuda=False)

try:
    globalPeople = pickle.load(open(openfaceDBDir + '/ofpeople.ini', 'rb'))
    globalImages = pickle.load(open(openfaceDBDir + '/ofimages.ini', 'rb'))
    (X, y) = getGlobalData()
    globalSvm = GridSearchCV(SVC(C=1, probability=True), param_grid, cv=5).fit(X, y)
    print("Using saved data")
except:
    globalImages = {}
    globalPeople = []
    globalSvm = None
    print("Not using saved data")
        
# start forwarding thread

forwardThreadExit = False
forwardThreadObject = threading.Thread(target=forwardThread)
forwardThreadObject.start()

try:
    while True:
        if (processingFaceRec):
            detectedData = []
            try:
                image = faceRecImage
                width = faceRecMessage[vdefs.WIDTH]
                height = faceRecMessage[vdefs.HEIGHT]
                inJpeg = np.frombuffer(image, dtype=np.uint8)
                cv2Image = cv2.imdecode(inJpeg, cv2.IMREAD_COLOR)

                if (useModet):

                    # go through the modet metadata processing each segment
                    try:
                        metadata = faceRecMessage[rtndefs.METADATA]
                        modetarray = metadata[mdefs.TYPE]

                        for modetarrayentry in modetarray:
                            # decode the segment jpag and try to recognize it
                            modetInJpeg = base64.b64decode(modetarrayentry[mdefs.JPEG])
                            x = modetarrayentry[mdefs.REGION_X]
                            y = modetarrayentry[mdefs.REGION_Y]
                            data = processFrame(modetInJpeg, cv2Image, width, height, x, y)
                            if len(data) > 0:
                                detectedData.append(data)


                    except:
                        # lots of reasons to get here - just let it go
                        pass
                else:
                    # just add the single label
                    data = processFrame(image, cv2Image, width, height, 0, 0)
                    if len(data) > 0:
                        detectedData.append(data)
                    retVal, outJpeg = cv2.imencode('.jpeg', cv2Image)

                dataLock.acquire()
                if len(detectedData) > 0:
                    globalDetectedData = copy.deepcopy(detectedData)
                else:
                    globalDetectedData = []
                dataLock.release()

            except:
                print ("video data error", sys.exc_info()[0],sys.exc_info()[1])

            processingFaceRec = False

        time.sleep(0.01)

except:
    pass

# Exiting so clean everything up.

forwardThreadExit = True
forwardThreadObject.join(0.1)


