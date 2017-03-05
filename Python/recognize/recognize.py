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


This was created from the Inception-v3 example here:

    https://github.com/tensorflow/tensorflow/blob/master/tensorflow/models/image/imagenet/classify_image.py

Original header:

# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================


*** Note: this can be very slow to start up! Also, the first time it is run
it will download the Inception data file.

'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pygame
import cStringIO
import time
import json
import platform
import getopt
import threading

import os
import re
import sys
import tarfile

import numpy as np
from six.moves import urllib
import tensorflow as tf

import cv2

import ManifoldPython
import rtndf.rtndf as rdf
import rtndf.datadefs.videodatadefs as vdefs
import rtndf.metadefs.rtndfdefs as rtndefs
import rtndf.metadefs.modetdefs as mdefs

FLAGS = tf.app.flags.FLAGS

tempModelDir = '/.config/Manifold/recognize'

if not os.access(tempModelDir, os.W_OK):
    tempModelDir = '~/.config/Manifold/recognize'

tf.app.flags.DEFINE_string(
    'model_dir', tempModelDir,
    """Path to classify_image_graph_def.pb, """
    """imagenet_synset_to_human_label_map.txt, and """
    """imagenet_2012_challenge_label_map_proto.pbtxt.""")
tf.app.flags.DEFINE_string('image_file', '',
                           """Absolute path to image file.""")
tf.app.flags.DEFINE_integer('num_top_predictions', 5,
                            """Display this many predictions.""")

# pylint: disable=line-too-long
DATA_URL = 'http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz'
# pylint: enable=line-too-long

class NodeLookup(object):
  """Converts integer node ID's to human readable labels."""

  def __init__(self,
               label_lookup_path=None,
               uid_lookup_path=None):
    if not label_lookup_path:
      label_lookup_path = os.path.join(
          FLAGS.model_dir, 'imagenet_2012_challenge_label_map_proto.pbtxt')
    if not uid_lookup_path:
      uid_lookup_path = os.path.join(
          FLAGS.model_dir, 'imagenet_synset_to_human_label_map.txt')
    self.node_lookup = self.load(label_lookup_path, uid_lookup_path)

  def load(self, label_lookup_path, uid_lookup_path):
    """Loads a human readable English name for each softmax node.

    Args:
      label_lookup_path: string UID to integer node ID.
      uid_lookup_path: string UID to human-readable string.

    Returns:
      dict from integer node ID to human-readable string.
    """
    if not tf.gfile.Exists(uid_lookup_path):
      tf.logging.fatal('File does not exist %s', uid_lookup_path)
    if not tf.gfile.Exists(label_lookup_path):
      tf.logging.fatal('File does not exist %s', label_lookup_path)

    # Loads mapping from string UID to human-readable string
    proto_as_ascii_lines = tf.gfile.GFile(uid_lookup_path).readlines()
    uid_to_human = {}
    p = re.compile(r'[n\d]*[ \S,]*')
    for line in proto_as_ascii_lines:
      parsed_items = p.findall(line)
      uid = parsed_items[0]
      human_string = parsed_items[2]
      uid_to_human[uid] = human_string

    # Loads mapping from string UID to integer node ID.
    node_id_to_uid = {}
    proto_as_ascii = tf.gfile.GFile(label_lookup_path).readlines()
    for line in proto_as_ascii:
      if line.startswith('  target_class:'):
        target_class = int(line.split(': ')[1])
      if line.startswith('  target_class_string:'):
        target_class_string = line.split(': ')[1]
        node_id_to_uid[target_class] = target_class_string[1:-2]

    # Loads the final mapping of integer node ID to human-readable string
    node_id_to_name = {}
    for key, val in node_id_to_uid.items():
      if val not in uid_to_human:
        tf.logging.fatal('Failed to locate: %s', val)
      name = uid_to_human[val]
      node_id_to_name[key] = name

    return node_id_to_name

  def id_to_string(self, node_id):
    if node_id not in self.node_lookup:
      return ''
    return self.node_lookup[node_id]


def create_graph():
  """Creates a graph from saved GraphDef file and returns a saver."""
  # Creates graph from saved graph_def.pb.
  with tf.gfile.FastGFile(os.path.join(
      FLAGS.model_dir, 'classify_image_graph_def.pb'), 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')



def maybe_download_and_extract():
  """Download and extract model tar file."""
  dest_directory = FLAGS.model_dir
  if not os.path.exists(dest_directory):
    os.makedirs(dest_directory)
  filename = DATA_URL.split('/')[-1]
  filepath = os.path.join(dest_directory, filename)
  if not os.path.exists(filepath):
    def _progress(count, block_size, total_size):
      sys.stdout.write('\r>> Downloading %s %.1f%%' % (
          filename, float(count * block_size) / float(total_size) * 100.0))
      sys.stdout.flush()
    filepath, _ = urllib.request.urlretrieve(DATA_URL, filepath, _progress)
    print()
    statinfo = os.stat(filepath)
    print('Succesfully downloaded', filename, statinfo.st_size, 'bytes.')
  tarfile.open(filepath, 'r:gz').extractall(dest_directory)

'''
------------------------------------------------------------
    process incoming message
'''

def processReceivedMessage():
    global processing, jsonToProcess, imageToProcess, imageTS
    
    while not receiveThreadExit:
        ret, data, image, timestamp = ManifoldPython.getMulticastData(inPort)
        if not ret:
            time.sleep(0.01)
            continue
        
        try:
            jsonObj = json.loads(data)

            dataLock.acquire()
            if not processing:
                jsonToProcess = jsonObj
                imageToProcess = image
                imageTS = timestamp
                processing=True
 
        except:
            print ("JSON error", sys.exc_info()[0],sys.exc_info()[1])

        dataLock.release()


'''
------------------------------------------------------------
    Perform recognition and return label
'''

def recognize(image):
    try:
        softmax_tensor = sess.graph.get_tensor_by_name('softmax:0')
        predictions = sess.run(softmax_tensor,
              {'DecodeJpeg/contents:0': image})
        predictions = np.squeeze(predictions)

        top_k = predictions.argsort()[-FLAGS.num_top_predictions:][::-1]
        return (node_lookup.id_to_string(top_k[0]))

    except:
        print ("Inference error", sys.exc_info()[0],sys.exc_info()[1])
        return ''

'''
------------------------------------------------------------
    Custom arg handler
'''

def processArg(opt, arg):
    global inTopic, outTopic, useModet

    if opt == '-i':
        inTopic = arg
    if opt == '-o':
        outTopic = arg
    if opt == '-m':
        useModet = True

'''
------------------------------------------------------------
    Main code
'''

# set defaults

inTopic = "%s_uvccam/video" % platform.node()
outTopic = 'recognize'
jsonToProcess = None
imageToProcess = None
processing = False
useModet = False

dataLock = threading.Lock()

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:o:m' + rdf.manifoldArgOpts)
except:
    print ('python recognize [-i <inTopic>] [-m] [-o <outTopic>]' + rdf.manifoldArgs)
    print ('\nDefaults:')
    print ('  -i %s\n  -m if present use modet regions\n  -o recognize' % inTopic)
    print (rdf.manifoldArgsDefaults)
    sys.exit(2)

for opt, arg in opts:
    if opt == '-i':
        inTopic = arg
    if opt == '-o':
        outTopic = arg
    if opt == '-m':
        useModet = True

# start ManifoldPython running

ManifoldPython.start("recognize", sys.argv, False)

# this delay is necessary to allow Qt startup to complete
time.sleep(1.0)

# wake up the console
print("recognize starting...")
sys.stdout.flush()

maybe_download_and_extract()

# Creates graph from saved GraphDef.
create_graph()

try:
    # Creates node ID --> English string lookup.
    node_lookup = NodeLookup()

    with tf.Session() as sess:
        # Activate the input stream
        inPort = ManifoldPython.addMulticastSink(inTopic)
        if (inPort == -1):
            print("Failed to activate input stream")
            ManifoldPython.stop()
            sys.exit()
            
        receiveThreadExit = False
        receiveThreadObject = threading.Thread(target=processReceivedMessage)    
        receiveThreadObject.start()


        # Activate the output stream
        outPort = ManifoldPython.addMulticastSource(outTopic)
        if (outPort == -1):
            print("Failed to activate output stream")
            ManifoldPython.stop()
            sys.exit()
                        
        while True:
            if (processing):
                try:
                    image = imageToProcess
                    height = jsonToProcess[vdefs.HEIGHT]

                    # get this in case we need to add labels to the image
                    inJpeg = np.frombuffer(image, dtype=np.uint8)
                    cv2Image = cv2.imdecode(inJpeg, cv2.IMREAD_COLOR)
                    font = cv2.FONT_HERSHEY_SIMPLEX

                    # in case nothing gets processed
                    outJpeg = image

                    if (useModet):

                        # go through the modet metadata processing each segment
                        try:
                            metadata = jsonToProcess[rtndefs.METADATA]
                            modetarray = metadata[mdefs.TYPE]

                            for modetarrayentry in modetarray:
                                # decode the segment jpag and try to recognize it
                                modetInJpeg = base64.b64decode(modetarrayentry[mdefs.JPEG])
                                label = recognize(modetInJpeg)
                                if label is '':
                                    continue
                                # draw the label in the appropriate place
                                x = modetarrayentry[mdefs.REGION_X]
                                y = modetarrayentry[mdefs.REGION_Y]
                                cv2.putText(cv2Image,label,(x+5,y+20), font, 1,(0,255,255),1,cv2.LINE_AA)

                            # generate the output jpeg
                            retVal, outJpeg = cv2.imencode('.jpeg', cv2Image)

                        except:
                            # lots of reasons to get here - just let it go
                            pass
                    else:
                        # just add the single label
                        label = recognize(image)
                        if label is not '':
                            cv2.putText(cv2Image,label,(10,height - 30), font, 2,(255,255,0),2,cv2.LINE_AA)
                            retVal, outJpeg = cv2.imencode('.jpeg', cv2Image)
                        else:
                            outJpeg = image
                    jsonToProcess[rtndefs.TOPIC] = outTopic
                    if ManifoldPython.isServiceActive(outPort) and ManifoldPython.isClearToSend(outPort):
                        ManifoldPython.sendMulticastData(outPort, json.dumps(jsonToProcess), outJpeg, imageTS)

                except:
                    print ("video data error", sys.exc_info()[0],sys.exc_info()[1])

                processing = False
 
            time.sleep(0.01)
            pass
except:
    pass

# Exiting so clean everything up.

receiveThreadExit = True
receiveThreadObject.join(0.1)

ManifoldPython.removeService(inPort)
ManifoldPython.removeService(outPort)
ManifoldPython.stop()
