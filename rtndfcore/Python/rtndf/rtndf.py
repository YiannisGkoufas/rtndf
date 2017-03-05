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

import platform
import sys

import metadefs.rtndfdefs as rtndfdefs

'''
------------------------------------------------------------
    Global variables
'''
scriptName = 'rtndf'

#   This string should be added to the getopt call to avoid errors due to Manifold-processed options.
#   Also, no app should try to use a, s, x, or y as runtime arguments.

manifoldArgOpts = 'a:s:xy'

manifoldArgs = '\n  [-a <adaptor] [-s <ini file>] [-x] [-y]'
    
manifoldArgsDefaults = '  -a <any>\n  -s %s_%s.ini\n  -x for console mode\n  -y for daemon mode' % (platform.node(), sys.argv[0])
    
    
'''
------------------------------------------------------------
    Message creation
'''

def newPublishMessage(deviceID, topic, dataType, timestamp):
    message = {}
    message[rtndfdefs.TIMESTAMP] = timestamp
    message[rtndfdefs.DEVICEID] = deviceID
    message[rtndfdefs.TOPIC] = topic
    message[rtndfdefs.TYPE] = dataType
    return message


