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

import json
import rtndf.datadefs.sensordatadefs as sdefs
import rtndf.metadefs.rtndfdefs as rtndfdefs
import sensorrecordinstance

# global defines

SENSOR_RECORD_LENGTH = 600                                  # number of time intervals

# the sensor record array indices

SENSOR_RECORD_POSE_X =      0
SENSOR_RECORD_POSE_Y =      1
SENSOR_RECORD_POSE_Z =      2
SENSOR_RECORD_GYRO_X =      3
SENSOR_RECORD_GYRO_Y =      4
SENSOR_RECORD_GYRO_Z =      5
SENSOR_RECORD_ACCEL_X =     6
SENSOR_RECORD_ACCEL_Y =     7
SENSOR_RECORD_ACCEL_Z =     8
SENSOR_RECORD_MAG_X =       9
SENSOR_RECORD_MAG_Y =       10
SENSOR_RECORD_MAG_Z =       11
SENSOR_RECORD_LIGHT =       12
SENSOR_RECORD_TEMPERATURE = 13
SENSOR_RECORD_PRESSURE =    14
SENSOR_RECORD_HUMIDITY =    15

SENSOR_RECORD_COUNT =       16

class SensorRecords():
    ''' Sensor model used by viewers '''
        
    def __init__(self, topicName, accumInterval):       
        # the sensor instance vars
        self.sensorRecords = []
        for i in range (0, SENSOR_RECORD_COUNT):
            self.sensorRecords.append(sensorrecordinstance.sensorrecordinstance(SENSOR_RECORD_LENGTH,
                            accumInterval))
        self.topicName = topicName
        self.accumInterval = accumInterval
                              
    def newJSONData(self, data):
        ''' adds a sensor JSON record to the record '''
        # decode the JSON record
        sensorDict = json.loads(data)
        newTimestamp = sensorDict.get(rtndfdefs.TIMESTAMP)
        newMagData = sensorDict.get(sdefs.MAG_DATA)
        newAccelData = sensorDict.get(sdefs.ACCEL_DATA)
        newGyroData = sensorDict.get(sdefs.GYRO_DATA)
        newPoseData = sensorDict.get(sdefs.POSE_DATA)
        newLightData = sensorDict.get(sdefs.LIGHT_DATA)
        newTemperatureData = sensorDict.get(sdefs.TEMPERATURE_DATA)
        newPressureData = sensorDict.get(sdefs.PRESSURE_DATA)
        newHumidityData = sensorDict.get(sdefs.HUMIDITY_DATA)
         
        if (newTimestamp == None):
            print ("Received JSON record without timestamp")
            return
            
        # now update instances
        
        if (newPoseData != None):
            self.sensorRecords[SENSOR_RECORD_POSE_X].addData(newTimestamp, newPoseData[0])
            self.sensorRecords[SENSOR_RECORD_POSE_Y].addData(newTimestamp, newPoseData[1])
            self.sensorRecords[SENSOR_RECORD_POSE_Z].addData(newTimestamp, newPoseData[2])
            
        if (newGyroData != None):
            self.sensorRecords[SENSOR_RECORD_GYRO_X].addData(newTimestamp, newGyroData[0])
            self.sensorRecords[SENSOR_RECORD_GYRO_Y].addData(newTimestamp, newGyroData[1])
            self.sensorRecords[SENSOR_RECORD_GYRO_Z].addData(newTimestamp, newGyroData[2])
            
        if (newAccelData != None):
            self.sensorRecords[SENSOR_RECORD_ACCEL_X].addData(newTimestamp, newAccelData[0])
            self.sensorRecords[SENSOR_RECORD_ACCEL_Y].addData(newTimestamp, newAccelData[1])
            self.sensorRecords[SENSOR_RECORD_ACCEL_Z].addData(newTimestamp, newAccelData[2])
            
        if (newMagData != None):
            self.sensorRecords[SENSOR_RECORD_MAG_X].addData(newTimestamp, newMagData[0])
            self.sensorRecords[SENSOR_RECORD_MAG_Y].addData(newTimestamp, newMagData[1])
            self.sensorRecords[SENSOR_RECORD_MAG_Z].addData(newTimestamp, newMagData[2])
            
        if (newLightData != None):
             self.sensorRecords[SENSOR_RECORD_LIGHT].addData(newTimestamp, newLightData)
             
        if (newTemperatureData != None):
             self.sensorRecords[SENSOR_RECORD_TEMPERATURE].addData(newTimestamp, newTemperatureData)
             
        if (newPressureData != None):
             self.sensorRecords[SENSOR_RECORD_PRESSURE].addData(newTimestamp, newPressureData)
             
        if (newHumidityData != None):
             self.sensorRecords[SENSOR_RECORD_HUMIDITY].addData(newTimestamp, newHumidityData)
   
    def getTopicName(self):
        return self.topicName
   
    # data validity functions
    
    def getPoseValid(self):
        return self.sensorRecords[SENSOR_RECORD_POSE_X].getDataValid()
        
    def getGyroValid(self):
        return self.sensorRecords[SENSOR_RECORD_GYRO_X].getDataValid()
        
    def getAccelValid(self):
        return self.sensorRecords[SENSOR_RECORD_ACCEL_X].getDataValid()
        
    def getMagValid(self):
        return self.sensorRecords[SENSOR_RECORD_MAG_X].getDataValid()
        
    def getLightValid(self):
        return self.sensorRecords[SENSOR_RECORD_LIGHT].getDataValid()
    
    def getTemperatureValid(self):
        return self.sensorRecords[SENSOR_RECORD_TEMPERATURE].getDataValid()
    
    def getPressureValid(self):
        return self.sensorRecords[SENSOR_RECORD_PRESSURE].getDataValid()
    
    def getHumidityValid(self):
        return self.sensorRecords[SENSOR_RECORD_HUMIDITY].getDataValid()
        
    # accumulated data access function
    
    def getPoseDataX(self):
        return self.sensorRecords[SENSOR_RECORD_POSE_X].getData()
        
    def getPoseDataY(self):
        return self.sensorRecords[SENSOR_RECORD_POSE_Y].getData()
        
    def getPoseDataZ(self):
        return self.sensorRecords[SENSOR_RECORD_POSE_Z].getData()
        
    def getGyroDataX(self):
        return self.sensorRecords[SENSOR_RECORD_GYRO_X].getData()
        
    def getGyroDataY(self):
        return self.sensorRecords[SENSOR_RECORD_GYRO_Y].getData()
        
    def getGyroDataZ(self):
        return self.sensorRecords[SENSOR_RECORD_GYRO_Z].getData()
        
    def getAccelDataX(self):
        return self.sensorRecords[SENSOR_RECORD_ACCEL_X].getData()
        
    def getAccelDataY(self):
        return self.sensorRecords[SENSOR_RECORD_ACCEL_Y].getData()
        
    def getAccelDataZ(self):
        return self.sensorRecords[SENSOR_RECORD_ACCEL_Z].getData()
        
    def getMagDataX(self):
        return self.sensorRecords[SENSOR_RECORD_MAG_X].getData()
        
    def getMagDataY(self):
        return self.sensorRecords[SENSOR_RECORD_MAG_Y].getData()
        
    def getMagDataZ(self):
        return self.sensorRecords[SENSOR_RECORD_MAG_Z].getData()
        
    def getLightData(self):
        return self.sensorRecords[SENSOR_RECORD_LIGHT].getData()
    
    def getTemperatureData(self):
        return self.sensorRecords[SENSOR_RECORD_TEMPERATURE].getData()
    
    def getPressureData(self):
        return self.sensorRecords[SENSOR_RECORD_PRESSURE].getData()
    
    def getHumidityData(self):
        return self.sensorRecords[SENSOR_RECORD_HUMIDITY].getData()
        
    # current data access function
    
    def getCurrentPoseDataX(self):
        return self.sensorRecords[SENSOR_RECORD_POSE_X].getCurrentData()
        
    def getCurrentPoseDataY(self):
        return self.sensorRecords[SENSOR_RECORD_POSE_Y].getCurrentData()
        
    def getCurrentPoseDataZ(self):
        return self.sensorRecords[SENSOR_RECORD_POSE_Z].getCurrentData()
        
    def getCurrentGyroDataX(self):
        return self.sensorRecords[SENSOR_RECORD_GYRO_X].getCurrentData()
        
    def getCurrentGyroDataY(self):
        return self.sensorRecords[SENSOR_RECORD_GYRO_Y].getCurrentData()
        
    def getCurrentGyroDataZ(self):
        return self.sensorRecords[SENSOR_RECORD_GYRO_Z].getCurrentData()
        
    def getCurrentAccelDataX(self):
        return self.sensorRecords[SENSOR_RECORD_ACCEL_X].getCurrentData()
        
    def getCurrentAccelDataY(self):
        return self.sensorRecords[SENSOR_RECORD_ACCEL_Y].getCurrentData()
        
    def getCurrentAccelDataZ(self):
        return self.sensorRecords[SENSOR_RECORD_ACCEL_Z].getCurrentData()
        
    def getCurrentMagDataX(self):
        return self.sensorRecords[SENSOR_RECORD_MAG_X].getCurrentData()
        
    def getCurrentMagDataY(self):
        return self.sensorRecords[SENSOR_RECORD_MAG_Y].getCurrentData()
        
    def getCurrentMagDataZ(self):
        return self.sensorRecords[SENSOR_RECORD_MAG_Z].getCurrentData()
        
    def getCurrentLightData(self):
        return self.sensorRecords[SENSOR_RECORD_LIGHT].getCurrentData()
    
    def getCurrentTemperatureData(self):
        return self.sensorRecords[SENSOR_RECORD_TEMPERATURE].getCurrentData()
    
    def getCurrentPressureData(self):
        return self.sensorRecords[SENSOR_RECORD_PRESSURE].getCurrentData()
    
    def getCurrentHumidityData(self):
        return self.sensorRecords[SENSOR_RECORD_HUMIDITY].getCurrentData()
        
        
        
        
        
        
 
