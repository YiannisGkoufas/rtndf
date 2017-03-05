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

import time
import json
import getopt
import platform
import threading

import sys

import numpy as np
import tensorflow as tf

import ManifoldPython
import rtndf.rtndf as rdf
import rtndf.datadefs.videodatadefs as vdefs
import rtndf.metadefs.rtndfdefs as rtndefs


'''
------------------------------------------------------------
    process incoming messages
'''

def receiveThread():
    global processing, jsonToProcess, imageToProcess, imageTS, receiveThreadExit
    
    while not receiveThreadExit:

        ret, data, image, timestamp = ManifoldPython.getMulticastData(inPort)
        if not ret:
            time.sleep(0.001)
            continue
            
        if processing:
            time.sleep(0.001)
            continue
        
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
outTopic = 'imageproc'
jsonToProcess = None
imageToProcess = None
imageTS = time.time()
processing = False
receiveThreadExit = False
receiveThreadObject = threading.Thread(target=receiveThread)

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:o:' + rdf.manifoldArgOpts)
except:
    print ('python imageproc [-i <inTopic>] [-o <outTopic>]' + rdf.manifoldArgs)
    print ('\nDefaults:')
    print ('  -i %s\n  -o imageproc' % inTopic)
    print (rdf.manifoldArgsDefaults)
    sys.exit(2)

for opt, arg in opts:
    if opt == '-i':
        inTopic = arg
    if opt == '-o':
        outTopic = arg
        
# start ManifoldPython running

ManifoldPython.start("imageproc", sys.argv, False)

# this delay is necessary to allow Qt startup to complete
time.sleep(1.0)

# wake up the console
print("imageproc starting...")
sys.stdout.flush()

# Activate the input stream
inPort = ManifoldPython.addMulticastSink(inTopic)
if (inPort == -1):
    print("Failed to activate input stream")
    ManifoldPython.stop()
    sys.exit()
    
receiveThreadObject.start()

# Activate the output stream
outPort = ManifoldPython.addMulticastSource(outTopic)
if (outPort == -1):
    print("Failed to activate output stream")
    ManifoldPython.stop()
    sys.exit()

try:

#   simple Laplacian

    cfactor = 8.
    efactor = -1.
    
#   create filter 

    npFilter = np.zeros((3, 3, 3, 3), dtype=np.float32)
    for channel in range(0, 3):
        npFilter[0, 0, channel, channel] = efactor
        npFilter[0, 1, channel, channel] = efactor
        npFilter[0, 2, channel, channel] = efactor
        npFilter[1, 0, channel, channel] = efactor
        npFilter[1, 1, channel, channel] = cfactor
        npFilter[1, 2, channel, channel] = efactor
        npFilter[2, 0, channel, channel] = efactor
        npFilter[2, 1, channel, channel] = efactor
        npFilter[2, 2, channel, channel] = efactor

    filter = tf.Variable(npFilter, dtype=tf.float32)
    inputDataNode = tf.placeholder(tf.string)
    
#   create graph
    
    # first convert jpeg to a tensor
    decodedImage = tf.image.decode_jpeg(inputDataNode)
    
    # the processing functions require floats so convert to a tensor of floats
    decodedImageFloat = tf.to_float(decodedImage)
    
    # the decoded image is 3-D so expand to 4-D with a batch size of 1
    decodedImage4D = tf.expand_dims(decodedImageFloat, 0)
    
    # scale the image size down by a factor of 2 just because we can
    decodedImagePool = tf.nn.avg_pool(decodedImage4D, [1, 2, 2, 1], [1, 2, 2, 1], 'SAME')
    
    # perform the convolution
    convImage = tf.nn.conv2d(decodedImagePool, filter, strides=[1,1,1,1], padding='SAME')
    
    # convert the 4-D tensor back to 3-D
    convImage3D = tf.squeeze(convImage)
    
    # convert the floats to uint8s with a saturating cast
    convImage3D8 = tf.saturate_cast(convImage3D, dtype=tf.uint8)
    
    # re-encode the resulting image as a jpeg
    encodedImage = tf.image.encode_jpeg(convImage3D8)

#   main loop

    gpu_options = tf.GPUOptions(
        per_process_gpu_memory_fraction=0.6)
    with tf.Session(config=tf.ConfigProto(
        device_count={"CPU":8},
        inter_op_parallelism_threads=1,
        intra_op_parallelism_threads=1,
        gpu_options=gpu_options,
    )) as sess:

        tf.initialize_all_variables().run()

        while True:
            if (processing):
                try:
                    image = imageToProcess
                    width = int(jsonToProcess[vdefs.WIDTH])
                    height = int(jsonToProcess[vdefs.HEIGHT])

                except:
                    print ("video data error", sys.exc_info()[0],sys.exc_info()[1])

                try:

                    convJpeg = sess.run(encodedImage, feed_dict={inputDataNode : image})
                    jsonToProcess[rtndefs.TOPIC] = outTopic
                    jsonToProcess[vdefs.WIDTH] = width / 2
                    jsonToProcess[vdefs.HEIGHT] = height / 2
                    if ManifoldPython.isServiceActive(outPort) and ManifoldPython.isClearToSend(outPort):
                        ManifoldPython.sendMulticastData(outPort, json.dumps(jsonToProcess), convJpeg, imageTS)
     
                except:
                    print ("Video processing error", sys.exc_info()[0],sys.exc_info()[1])
                
            processing = False
        time.sleep(0.01)
except:
    print ("Main loop error", sys.exc_info()[0],sys.exc_info()[1])
    pass

# Exiting so clean everything up.

ManifoldPython.removeService(inPort)
ManifoldPython.removeService(outPort)
receiveThreadExit = True
receiveThreadObject.join(0.1)
ManifoldPython.stop()
