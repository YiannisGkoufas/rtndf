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

import pygame
import pyaudio
import cStringIO
import time
import json
import sys
import getopt
import threading
import platform

import ManifoldPython
import rtndf.rtndf as rdf
import rtndf.metadefs.rtndfdefs as rtndefs
import rtndf.datadefs.videodatadefs as vdefs
import rtndf.datadefs.audiodatadefs as adefs


'''
------------------------------------------------------------
    check for received video messages
'''

def processVideoMessage():
    global firstVideo, screen, frameCount

    while True:
        ret, data, image, timestamp = ManifoldPython.getMulticastData(videoPort)
        if not ret:
            return

        try:
            jsonObj = json.loads(data)

            if firstVideo:
                firstVideo = False
                size=(int(jsonObj[vdefs.WIDTH]), int(jsonObj[vdefs.HEIGHT]))
                screen = pygame.display.set_mode(size)

            imageFile = cStringIO.StringIO(image)
            imageSurface = pygame.image.load(imageFile)
            screen.blit(imageSurface, (0, 0))
            pygame.draw.rect(screen, (0,0,0), (10, 5, 600, 30))
            label = myfont.render('Frame rate: %d fps, %s:%03d' % 
                (frameRate, time.ctime(timestamp), (timestamp * 1000) % 1000), 
                1, (255,255,255))
            screen.blit(label, (20, 10))
            pygame.display.flip()
            frameCount += 1
        except:
            print ("video data error", sys.exc_info()[0],sys.exc_info()[1])


        
'''
------------------------------------------------------------
    check for received audio messages
'''

def audioThread():
    firstAudio = True
    audioStream = None
    audioDevice = pyaudio.PyAudio()

    # Activate the audio stream
    
    audioPort = ManifoldPython.addMulticastSink(audioTopic)
    if (audioPort == -1):
        print("Failed to activate audio stream")
        ManifoldPython.stop()
        sys.exit()
        
    while not audioThreadExit:
        ret, data, samples, timestamp = ManifoldPython.getMulticastData(audioPort)
        if not ret:
            time.sleep(0.001)
            continue

        try:
            jsonObj = json.loads(data)
            if firstAudio:
                firstAudio = False
                audioStream = audioDevice.open(format=pyaudio.paInt16, channels=int(jsonObj[adefs.CHANNELS]),
                    rate=int(jsonObj[adefs.RATE]), output=True)
            audioStream.write(samples)
        except:
            print ("audio data error", sys.exc_info()[0],sys.exc_info()[1])

    try:
        audioStream.stop_stream()
        audioStream.close()
    except:
        pass
    
    audioDevice.terminate()
    ManifoldPython.removeService(audioPort)

'''
------------------------------------------------------------
    Main code
'''

# set defaults

videoTopic = "%s_uvccam/video" % platform.node()
audioTopic = "%s_audio/audio" % platform.node()

videoPort = -1

firstVideo = True

frameCount = 0
frameRate = 0

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], 'p:v:' + rdf.manifoldArgOpts)
except:
    print ('python avview [-p <PCMAudioTopic>] [-v <videoTopic>]' + rdf.manifoldArgs)
    print ('\nDefaults:')
    print ('  -p %s\n  -v %s\n' % (audioTopic, videoTopic))
    print (rdf.manifoldArgsDefaults)
    sys.exit(2)

for opt, arg in opts:
    if opt == '-p':
        audioTopic = arg
    if opt == '-v':
        videoTopic = arg

# start ManifoldPython running

ManifoldPython.start("avview", sys.argv, False)

# this delay is necessary to allow Qt startup to complete
time.sleep(1.0)

# wake up the console
print("avview starting...")
sys.stdout.flush()

pygame.init()
myfont = pygame.font.SysFont("monospace", 18)

# start audio thread

audioThreadExit = False
audioThreadObject = threading.Thread(target=audioThread)
audioThreadObject.start()

# Activate the video stream
videoPort = ManifoldPython.addMulticastSink(videoTopic)
if (videoPort == -1):
    print("Failed to activate video stream")
    ManifoldPython.stop()
    sys.exit()

lastTime = time.time()

try:
    while True:
        delta = time.time() - lastTime
        if (delta) >= 1.0:
            lastTime = time.time()
            frameRate = int(float(frameCount) / (delta - 0.01))
            frameCount = 0
        processVideoMessage()
        time.sleep(0.001)
except:
    pass

# Exiting so clean everything up.

audioThreadExit = True
audioThreadObject.join(0.1)
ManifoldPython.removeService(videoPort)
ManifoldPython.stop()
