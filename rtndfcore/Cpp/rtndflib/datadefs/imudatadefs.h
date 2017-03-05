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

//  data type

#define IMUDATA_DATATYPE "imu"

//  variables used in rtndf JSON video data records

#define IMUDATA_DATA                    "imudata"           // the imu data object

//  fields within the imudata object

#define IMUDATA_IMU_TIMESTAMP           "timestamp"         // time since epoch in microseconds
#define IMUDATA_IMU_FUSIONPOSE          "fusionPose"        // the fused Euler angles (radians)
#define IMUDATA_IMU_FUSIONQPOSE         "fusionQPose"       // the fused quaternion
#define IMUDATA_IMU_GYRO                "gyro"              // gyro data (radians/sec)
#define IMUDATA_IMU_ACCEL               "accel"             // accel data (gs)
#define IMUDATA_IMU_COMPASS             "compass"           // compass data (uT)
#define IMUDATA_IMU_PRESSURE            "pressure"          // pressurce in hPa
#define IMUDATA_IMU_HUMIDITY            "humidity"          // humidity in %RH
#define IMUDATA_IMU_TEMPERATURE         "temperature"       // temperature in C from temperature sensor
#define IMUDATA_IMU_PRESSURETEMPERATURE "pressureTemperature"  // temperature in C from pressure sensor
#define IMUDATA_IMU_HUMIDITYTEMPERATURE "humidityTemperature"  // temperature in C from humidity sensor

//  field validity flags

#define IMUDATA_IMU_FUSIONPOSE_VALID    "fusionPoseValid"
#define IMUDATA_IMU_FUSIONQPOSE_VALID   "fusionQPoseValid"
#define IMUDATA_IMU_GYRO_VALID          "gyroValid"
#define IMUDATA_IMU_ACCEL_VALID         "accelValid"
#define IMUDATA_IMU_COMPASS_VALID       "compassValid"
#define IMUDATA_IMU_PRESSURE_VALID      "pressureValid"
#define IMUDATA_IMU_HUMIDITY_VALID      "humidityValid"
#define IMUDATA_IMU_TEMPERATURE_VALID   "temperatureValid"
#define IMUDATA_IMU_PRESSURETEMPERATURE_VALID   "pressureTemperatureValid"
#define IMUDATA_IMU_HUMIDITYTEMPERATURE_VALID   "humidityTemperatureValid"


