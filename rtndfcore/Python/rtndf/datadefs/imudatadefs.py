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

#   data type

DATATYPE = 'imu'

# variables used in rtndf JSON video data records

DATA = 'imudata'                        # the imu data object

#   fields within the imudata object

IMU_TIMESTAMP = 'timestamp'             # time since epoch in microseconds
IMU_FUSIONPOSE = 'fusionPose'           # the fused Euler angles (radians)
IMU_FUSIONQPOSE = 'fusionQPose'         # the fused quaternion
IMU_GYRO = 'gyro'                       # gyro data (radians/sec)
IMU_ACCEL = 'accel'                     # accel data (gs)
IMU_COMPASS = 'compass'                 # compass data (uT)
IMU_PRESSURE = 'pressure'               # pressurce in hPa
IMU_HUMIDITY = 'humidity'               # humidity in %RH
IMU_TEMPERATURE = 'temperature'         # temperature in C from temperature sensor
IMU_PRESSURETEMPERATURE = 'pressureTemperature'   # temperature in C from pressure sensor
IMU_HUMIDITYTEMPERATURE = 'humidityTemperature'   # temperature in C from humidity sensor

#   field validity flags

IMU_FUSIONPOSE_VALID = 'fusionPoseValid'
IMU_FUSIONQPOSE_VALID = 'fusionQPoseValid'
IMU_GYRO_VALID = 'gyroValid'
IMU_ACCEL_VALID = 'accelValid'
IMU_COMPASS_VALID = 'compassValid'
IMU_PRESSURE_VALID = 'pressureValid'
IMU_HUMIDITY_VALID = 'humidityValid'
IMU_TEMPERATURE_VALID = 'temperatureValid'
IMU_PRESSURETEMPERATURE_VALID = 'pressureTemperatureValid'
IMU_HUMIDITYTEMPERATURE_VALID = 'humidityTemperatureValid'


