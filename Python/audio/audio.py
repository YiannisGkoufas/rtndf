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

import pyaudio
import sys
import time
import getopt
import json

import ManifoldPython
import rtndf.rtndf as rdf
import rtndf.datadefs.audiodatadefs as adefs

'''
------------------------------------------------------------
    pyaudio callbacks
'''
def callback(samples, frame_count, time_info, status):

    timestamp = time.time()
    message = rdf.newPublishMessage('audio', audioTopic, adefs.DATATYPE, timestamp)
    message[adefs.CHANNELS] = audioChannels
    message[adefs.RATE] = audioRate
    message[adefs.SAMPTYPE] = 'int16'
    message[adefs.FORMAT] = 'pcm'
    if ManifoldPython.isServiceActive(sourcePort) and ManifoldPython.isClearToSend(sourcePort):
        ManifoldPython.sendMulticastData(sourcePort, json.dumps(message), samples, timestamp)

    return (None, pyaudio.paContinue)

'''
------------------------------------------------------------
    Main code
'''
# set defaults

audioTopic = 'audio'
audioIndex = 0
audioRate = 16000
audioChannels = 1

sourcePort = -1

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], 'p:n:r:' + rdf.manifoldArgOpts)
except:
    print ('python uvccam [-p <PCMaudioTopic>] [-n <numberChannels>] [-r <rate>]' + rdf.manifoldArgs)
    print ('\nDefaults:')
    print ('  -p audio/audio\n  -n 1\n  -r 16000')
    print (rdf.manifoldArgsDefaults)
    sys.exit(2)

for opt, arg in opts:
    if opt == '-p':
        audioTopic = arg
    if opt == '-n':
        audioChannels = int(arg)
    if opt == '-r':
        audioRate = int(arg)

# start ManifoldPython running

ManifoldPython.start("audio", sys.argv, False)

# this delay is necessary to allow Qt startup to complete
time.sleep(1.0)

# Activate the source stream
sourcePort = ManifoldPython.addMulticastSource(audioTopic)
if (sourcePort == -1):
    print("Failed to activate stream service")
    ManifoldPython.stop()
    sys.exit()
        
# wake up the console
print("audio starting...")
sys.stdout.flush()

# start up the audio device

audioDevice = pyaudio.PyAudio()
audioBlockSize = audioRate / 20
audioStream = audioDevice.open(stream_callback = callback, format=pyaudio.paInt16, channels = audioChannels, 
                        rate=audioRate, input=True, output=False, frames_per_buffer=audioBlockSize)

audioStream.start_stream()
        
while audioStream.is_active():
    time.sleep(0.1) 

# Exiting so clean everything up.   
        
audioStream.stop_stream()
audioStream.close()
audioDevice.terminate()

ManifoldPython.removeService(sourcePort)
ManifoldPython.stop()
