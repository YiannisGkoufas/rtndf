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
# data type

DATATYPE = 'sensor'

# sensor types

ACCEL_DATA = 'accel'                    # accelerometer x, y, z data in gs
GYRO_DATA = 'gyro'                      # gyro x, y, z in radians per second
MAG_DATA = 'mag'                        # magnetometer x, y, z in uT
POSE_DATA = 'pose'                      # orientation roll, pitch and yaw data 
LIGHT_DATA = 'light'                    # light data in lux
TEMPERATURE_DATA = 'temperature'        # temperature data in degrees C
PRESSURE_DATA = 'pressure'              # pressure in mB
HUMIDITY_DATA = 'humidity'              # humidity in %RH
JOYSTICK_DATA = 'joy'                   # joystick data as [direction, pressState]

