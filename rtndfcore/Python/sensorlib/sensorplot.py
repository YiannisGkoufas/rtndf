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

import numpy as np
import matplotlib.pyplot as plt
import time

import rtndf.datadefs.sensordatadefs as sdefs
import sensorrecords

class sensorplot():
    
    # this is used to provide the x axis data for the plots
    xAxis = np.arange(-sensorrecords.SENSOR_RECORD_LENGTH, 0, 1)
    
    # this list contains the active figures (one per sensor)
    figures = []
    
    # this list contains the axis data for each figure
    axes = []
    
    def __doPlot(self, figNumber, sensor):
        if (figNumber > len(self.figures)):
            return
        
        if (figNumber == len(self.figures)):
            # need to add a figure
            fig, axarr = plt.subplots(8, sharex = True)
            self.figures.append(fig)
            self.axes.append(axarr)
            fig.subplots_adjust(hspace = 0.5)
            fig.set_size_inches(8, 11, forward=True)
       
        # now ready to actually draw the charts
       
        plt.figure(figNumber + 1)
        axarr = self.axes[figNumber]
        
        self.figures[figNumber].canvas.set_window_title(sensor.getTopicName())
        
        di = 0
   
        # do pose plot
        axarr[di].clear()
        axarr[di].set_ylim(-5, 5)        
        if (sensor.getPoseValid()):
 
            axarr[di].plot(self.xAxis, sensor.getPoseDataX(), 'b-', 
                            label = 'Pose X (%.2frad)' % sensor.getCurrentPoseDataX())
            axarr[di].plot(self.xAxis, sensor.getPoseDataY(), 'r-', 
                            label = 'Pose Y(%.2frad)' % sensor.getCurrentPoseDataY())
            axarr[di].plot(self.xAxis, sensor.getPoseDataZ(), 'g-', 
                            label = 'Pose Z(%.2frad)' % sensor.getCurrentPoseDataZ())
        else:
            axarr[di].plot(self.xAxis, sensor.getPoseDataX(), 'b-', 
                            label = 'No data')

        axarr[di].legend(loc='upper center', shadow=True, fontsize='x-small')
        axarr[di].set_title("Pose data")       
        di += 1
        
        # do gyro plot
        axarr[di].clear()
        axarr[di].set_ylim(-5, 5)        
        if (sensor.getGyroValid()):
 
            axarr[di].plot(self.xAxis, sensor.getGyroDataX(), 'b-', 
                            label = 'Gyro X (%.2frad/s)' % sensor.getCurrentGyroDataX())
            axarr[di].plot(self.xAxis, sensor.getGyroDataY(), 'r-', 
                            label = 'Gyro Y(%.2frad/s)' % sensor.getCurrentGyroDataY())
            axarr[di].plot(self.xAxis, sensor.getGyroDataZ(), 'g-', 
                            label = 'Gyro Z(%.2frad/s)' % sensor.getCurrentGyroDataZ())
        else:
            axarr[di].plot(self.xAxis, sensor.getGyroDataX(), 'b-', 
                            label = 'No data')

        axarr[di].legend(loc='upper center', shadow=True, fontsize='x-small')
        axarr[di].set_title("Gyro data")       
        di += 1
        
        # do accel plot
        axarr[di].clear()
        axarr[di].set_ylim(-2, 2)        
        if (sensor.getAccelValid()):
 
            axarr[di].plot(self.xAxis, sensor.getAccelDataX(), 'b-', 
                            label = 'Accel X (%.2fg)' % sensor.getCurrentAccelDataX())
            axarr[di].plot(self.xAxis, sensor.getAccelDataY(), 'r-', 
                            label = 'Accel Y(%.2fg)' % sensor.getCurrentAccelDataY())
            axarr[di].plot(self.xAxis, sensor.getAccelDataZ(), 'g-', 
                            label = 'Accel Z(%.2fg)' % sensor.getCurrentAccelDataZ())
        else:
            axarr[di].plot(self.xAxis, sensor.getAccelDataX(), 'b-', 
                            label = 'No data')

        axarr[di].legend(loc='upper center', shadow=True, fontsize='x-small')
        axarr[di].set_title("Accelerometer data")
        di += 1

        # do mag plot
        axarr[di].clear()
        axarr[di].set_ylim(-100, 100)        
        if (sensor.getMagValid()):
 
            axarr[di].plot(self.xAxis, sensor.getMagDataX(), 'b-', 
                            label = 'Mag X (%.2fuT)' % sensor.getCurrentMagDataX())
            axarr[di].plot(self.xAxis, sensor.getAccelDataY(), 'r-', 
                            label = 'Mag Y(%.2fuT)' % sensor.getCurrentMagDataY())
            axarr[di].plot(self.xAxis, sensor.getAccelDataZ(), 'g-', 
                            label = 'Mag Z(%.2fuT)' % sensor.getCurrentMagDataZ())
        else:
            axarr[di].plot(self.xAxis, sensor.getMagDataX(), 'b-', 
                            label = 'No data')

        axarr[di].legend(loc='upper center', shadow=True, fontsize='x-small')
        axarr[di].set_title("Mag data")
        di += 1

        #do light intensity plot
        axarr[di].clear()
        axarr[di].set_ylim(0, 1500)
        if (sensor.getLightValid()):
            axarr[di].plot(self.xAxis, sensor.getLightData(), 'b-', 
                           label = 'Light (%.2f lux)' % sensor.getCurrentLightData())
        else:
            axarr[di].plot(self.xAxis, sensor.getLightData(), 'b-', 
                           label = 'No data')
            
        axarr[di].legend(loc='upper center', shadow=True, fontsize='x-small')
        axarr[di].set_title("Light intensity data")
        di += 1
       
        #do temperature plot 
        axarr[di].clear()
        axarr[di].set_ylim(-50, 150)
        if (sensor.getTemperatureValid()):
            axarr[di].plot(self.xAxis, sensor.getTemperatureData(), 'b-', 
                           label = 'Temperature (%.2f deg C)' % sensor.getCurrentTemperatureData())
        else:
            axarr[di].plot(self.xAxis, sensor.getTemperatureData(), 'b-', 
                           label = 'No data')
                
        axarr[di].legend(loc='upper center', shadow=True, fontsize='x-small')
        axarr[di].set_title("Temperature data")
        di += 1
                 
        #do pressure plot 
        axarr[di].clear()
        axarr[di].set_ylim(800, 1200)
        if (sensor.getPressureValid()):
            axarr[di].plot(self.xAxis, sensor.getPressureData(), 'b-', 
                           label = 'Pressure (%.2f hPa)' % sensor.getCurrentPressureData())
        else:
            axarr[di].plot(self.xAxis, sensor.getPressureData(), 'b-', 
                           label = 'No data')
                
        axarr[di].legend(loc='upper center', shadow=True, fontsize='x-small')
        axarr[di].set_title("Pressure data")
        di += 1
                 
        #do humidity plot 
        axarr[di].clear()
        axarr[di].set_ylim(0, 100)
        if (sensor.getHumidityValid()):
            axarr[di].plot(self.xAxis, sensor.getHumidityData(), 'b-', 
                           label = 'Humidity (%.2f %%RH)' % sensor.getCurrentHumidityData())
        else:
            axarr[di].plot(self.xAxis, sensor.getHumidityData(), 'b-', 
                           label = 'No data')
                
        axarr[di].legend(loc='upper center', shadow=True, fontsize='x-small')
        axarr[di].set_title("Humidity data")
        di += 1
                          
    def __init__(self):
        ''' Sets up the sensor plot '''
        plt.ion()
       
    def plot(self, sensors):
        ''' Plots the data in the list of sensors '''
        figNumber = 0
        for sensor in sensors:
            self.__doPlot(figNumber, sensor)
            figNumber += 1
            
        if (len(self.figures) > 0):   
            plt.draw()
            plt.pause(0.001)
                       
        # check if anything has gone missing
        while (len(self.figures) > figNumber):
            plt.close(len(self.figures))
            self.figures.pop()
            self.axes.pop()
            
            
        
 
      
        
        
    
