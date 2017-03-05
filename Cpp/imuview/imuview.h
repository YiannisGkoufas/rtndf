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


#ifndef _IMUVIEW_H_
#define _IMUVIEW_H_

#include <QMainWindow>
#include <QLabel>
#include <qjsonobject.h>

#include "ui_imuview.h"

//  Settings keys

#define IMUVIEW_PARAMS_TOPIC_GROUP          "imuTopicGroup"
#define IMUVIEW_PARAMS_IMU_TOPIC            "topic"

class IMUWindow;
class IMUClient;

class IMUView : public QMainWindow
{
    Q_OBJECT

public:
    IMUView();

public slots:
    void onAbout();
    void onBasicSetup();
    void onTopicSetup();

    void newIMUData(QJsonObject json);

protected:
    void timerEvent(QTimerEvent *event);
    void closeEvent(QCloseEvent *event);

private:
    void layoutStatusBar();
    void layoutWindow();
    QLabel *getFixedPanel(QString text);

    QJsonObject m_imuData;                                   // this holds the IMU information and fusion output

    IMUClient *m_client;

    //  Qt GUI stuff

    Ui::IMUViewClass ui;

    QLabel *m_fusionQPoseScalar;
    QLabel *m_fusionQPoseX;
    QLabel *m_fusionQPoseY;
    QLabel *m_fusionQPoseZ;

    QLabel *m_fusionPoseX;
    QLabel *m_fusionPoseY;
    QLabel *m_fusionPoseZ;

    QLabel *m_gyroX;
    QLabel *m_gyroY;
    QLabel *m_gyroZ;

    QLabel *m_accelX;
    QLabel *m_accelY;
    QLabel *m_accelZ;
    QLabel *m_accelMagnitude;

    QLabel *m_compassX;
    QLabel *m_compassY;
    QLabel *m_compassZ;
    QLabel *m_compassMagnitude;

    QLabel *m_pressure;
    QLabel *m_height;
    QLabel *m_temperature;
    QLabel *m_humidity;

    IMUWindow *m_view;

    QLabel *m_rateStatus;

    int m_rateTimer;
    int m_displayTimer;

    int m_sampleCount;
};

#endif // _IMUVIEW_H_

