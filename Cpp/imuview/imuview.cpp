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

#include <QMessageBox>
#include <qboxlayout.h>
#include <QSettings>

#include "imuview.h"
#include "imuclient.h"
#include "RTMath.h"
#include "IMUWindow.h"
#include "imudatadefs.h"
#include "topicsetup.h"

#include "GUIAboutDlg.h"
#include "GUIBasicSetupDlg.h"

#define RATE_TIMER_INTERVAL 2

IMUView::IMUView()
    : QMainWindow()
{
    //  This is some normal Qt GUI stuff

    ui.setupUi(this);

    layoutWindow();
    layoutStatusBar();

    m_client = new IMUClient();

    //  This code connects up signals from the GUI

    connect(ui.actionExit, SIGNAL(triggered()), this, SLOT(close()));
    connect(ui.actionAbout, SIGNAL(triggered()), this, SLOT(onAbout()));
    connect(ui.actionBasicSetup, SIGNAL(triggered()), this, SLOT(onBasicSetup()));
    connect(ui.actionTopicSetup, SIGNAL(triggered()), this, SLOT(onTopicSetup()));

    connect(m_client, SIGNAL(newIMUData(QJsonObject)), this, SLOT(newIMUData(QJsonObject)));

    //  This value allows a sample rate to be calculated

    m_sampleCount = 0;

    //  start some timers to get things going

    m_rateTimer = startTimer(RATE_TIMER_INTERVAL * 1000);

    //  Only update the display 10 times per second to keep CPU reasonable

    m_displayTimer = startTimer(100);

    m_client->resumeThread();
}

void IMUView::closeEvent(QCloseEvent *)
{
    killTimer(m_displayTimer);
    killTimer(m_rateTimer);
}

void IMUView::newIMUData(QJsonObject json)
{
    m_imuData = json[IMUDATA_DATA].toObject();
    m_sampleCount++;
}


void IMUView::timerEvent(QTimerEvent *event)
{
    if (event->timerId() == m_displayTimer) {
        //  Update the GUI

        QJsonArray gyro = m_imuData[IMUDATA_IMU_GYRO].toArray();

        m_gyroX->setText(QString::number(gyro[0].toDouble(), 'f', 6));
        m_gyroY->setText(QString::number(gyro[1].toDouble(), 'f', 6));
        m_gyroZ->setText(QString::number(gyro[2].toDouble(), 'f', 6));

        QJsonArray accel = m_imuData[IMUDATA_IMU_ACCEL].toArray();
        double ax = accel[0].toDouble();
        double ay = accel[1].toDouble();
        double az = accel[2].toDouble();
        double aMag = pow(ax * ax + ay * ay + az * az, 0.5);
        m_accelX->setText(QString::number(ax, 'f', 6));
        m_accelY->setText(QString::number(ay, 'f', 6));
        m_accelZ->setText(QString::number(az, 'f', 6));

        QJsonArray compass = m_imuData[IMUDATA_IMU_COMPASS].toArray();
        double cx = compass[0].toDouble();
        double cy = compass[1].toDouble();
        double cz = compass[2].toDouble();
        double cMag = pow(cx * cx + cy * cy + cz * cz, 0.5);
        m_compassX->setText(QString::number(cx, 'f', 6));
        m_compassY->setText(QString::number(cy, 'f', 6));
        m_compassZ->setText(QString::number(cz, 'f', 6));

        QJsonArray fusionPose = m_imuData[IMUDATA_IMU_FUSIONPOSE].toArray();
        double fx = fusionPose[0].toDouble();
        double fy = fusionPose[1].toDouble();
        double fz = fusionPose[2].toDouble();
        m_fusionPoseX->setText(QString::number(fx * RTMATH_RAD_TO_DEGREE, 'f', 6));
        m_fusionPoseY->setText(QString::number(fy * RTMATH_RAD_TO_DEGREE, 'f', 6));
        m_fusionPoseZ->setText(QString::number(fz * RTMATH_RAD_TO_DEGREE, 'f', 6));

        QJsonArray fusionQPose = m_imuData[IMUDATA_IMU_FUSIONQPOSE].toArray();
        m_fusionQPoseScalar->setText(QString::number(fusionQPose[0].toDouble(), 'f', 6));
        m_fusionQPoseX->setText(QString::number(fusionQPose[1].toDouble(), 'f', 6));
        m_fusionQPoseY->setText(QString::number(fusionQPose[1].toDouble(), 'f', 6));
        m_fusionQPoseZ->setText(QString::number(fusionQPose[1].toDouble(), 'f', 6));


        m_accelMagnitude->setText(QString::number(aMag, 'f', 6));
        m_compassMagnitude->setText(QString::number(cMag, 'f', 6));
        if (m_imuData[IMUDATA_IMU_PRESSURE_VALID].toInt() > 0) {
            m_pressure->setText(QString::number(m_imuData[IMUDATA_IMU_PRESSURE].toDouble(), 'f', 2));
            m_height->setText(QString::number(RTMath::convertPressureToHeight(m_imuData[IMUDATA_IMU_PRESSURE].toDouble()), 'f', 2));
        } else {
            m_pressure->setText("0");
            m_height->setText("0");
        }

        if (m_imuData[IMUDATA_IMU_HUMIDITY_VALID].toInt() > 0) {
            m_humidity->setText(QString::number(m_imuData[IMUDATA_IMU_HUMIDITY].toDouble(), 'f', 2));
        } else {
            m_humidity->setText("0");
        }

        double temperature = -1000;

        if (m_imuData[IMUDATA_IMU_TEMPERATURE_VALID].toInt() > 0)
            temperature = m_imuData[IMUDATA_IMU_TEMPERATURE].toDouble();
        else if (m_imuData[IMUDATA_IMU_PRESSURETEMPERATURE_VALID].toInt() > 0)
            temperature = m_imuData[IMUDATA_IMU_PRESSURETEMPERATURE].toDouble();
        else if (m_imuData[IMUDATA_IMU_HUMIDITYTEMPERATURE_VALID].toInt() > 0)
            temperature = m_imuData[IMUDATA_IMU_HUMIDITYTEMPERATURE].toDouble();

        if (temperature > -1000)
            m_temperature->setText(QString::number(temperature, 'f', 2));
        else
            m_temperature->setText("0");

        m_view->updateIMU(fx, fy, fz);
    } else {

        //  Update the sample rate

        float rate = (float)m_sampleCount / (float(RATE_TIMER_INTERVAL));
        m_sampleCount = 0;
        m_rateStatus->setText(QString("Sample rate: %1 per second").arg(rate));
    }
}

void IMUView::layoutWindow()
{
    QHBoxLayout *mainLayout = new QHBoxLayout();
    mainLayout->setContentsMargins(3, 3, 3, 3);
    mainLayout->setSpacing(3);

    QVBoxLayout *vLayout = new QVBoxLayout();
    vLayout->addSpacing(10);

    vLayout->addWidget(new QLabel("Fusion state (quaternion): "));

    QHBoxLayout *dataLayout = new QHBoxLayout();
    dataLayout->setAlignment(Qt::AlignLeft);
    m_fusionQPoseScalar = getFixedPanel("1");
    m_fusionQPoseX = getFixedPanel("0");
    m_fusionQPoseY = getFixedPanel("0");
    m_fusionQPoseZ = getFixedPanel("0");
    dataLayout->addSpacing(30);
    dataLayout->addWidget(m_fusionQPoseScalar);
    dataLayout->addWidget(m_fusionQPoseX);
    dataLayout->addWidget(m_fusionQPoseY);
    dataLayout->addWidget(m_fusionQPoseZ);
    vLayout->addLayout(dataLayout);

    vLayout->addSpacing(10);
    vLayout->addWidget(new QLabel("Pose - roll, pitch, yaw (degrees): "));

    m_fusionPoseX = getFixedPanel("0");
    m_fusionPoseY = getFixedPanel("0");
    m_fusionPoseZ = getFixedPanel("0");
    dataLayout = new QHBoxLayout();
    dataLayout->setAlignment(Qt::AlignLeft);
    dataLayout->addSpacing(30);
    dataLayout->addWidget(m_fusionPoseX);
    dataLayout->addWidget(m_fusionPoseY);
    dataLayout->addWidget(m_fusionPoseZ);
    vLayout->addLayout(dataLayout);

    vLayout->addSpacing(10);
    vLayout->addWidget(new QLabel("Gyros (radians/s): "));

    m_gyroX = getFixedPanel("0");
    m_gyroY = getFixedPanel("0");
    m_gyroZ = getFixedPanel("0");
    dataLayout = new QHBoxLayout();
    dataLayout->setAlignment(Qt::AlignLeft);
    dataLayout->addSpacing(30);
    dataLayout->addWidget(m_gyroX);
    dataLayout->addWidget(m_gyroY);
    dataLayout->addWidget(m_gyroZ);
    vLayout->addLayout(dataLayout);

    vLayout->addSpacing(10);
    vLayout->addWidget(new QLabel("Accelerometers (g): "));

    m_accelX = getFixedPanel("0");
    m_accelY = getFixedPanel("0");
    m_accelZ = getFixedPanel("0");
    dataLayout = new QHBoxLayout();
    dataLayout->addSpacing(30);
    dataLayout->setAlignment(Qt::AlignLeft);
    dataLayout->addWidget(m_accelX);
    dataLayout->addWidget(m_accelY);
    dataLayout->addWidget(m_accelZ);
    vLayout->addLayout(dataLayout);

    vLayout->addSpacing(10);
    vLayout->addWidget(new QLabel("Accelerometer magnitude (g): "));

    m_accelMagnitude = getFixedPanel("0");
    dataLayout = new QHBoxLayout();
    dataLayout->addSpacing(30);
    dataLayout->addWidget(m_accelMagnitude);
    dataLayout->setAlignment(Qt::AlignLeft);
    vLayout->addLayout(dataLayout);

    vLayout->addWidget(new QLabel("Magnetometers (uT): "));

    m_compassX = getFixedPanel("0");
    m_compassY = getFixedPanel("0");
    m_compassZ = getFixedPanel("0");
    dataLayout = new QHBoxLayout();
    dataLayout->setAlignment(Qt::AlignLeft);
    dataLayout->addSpacing(30);
    dataLayout->addWidget(m_compassX);
    dataLayout->addWidget(m_compassY);
    dataLayout->addWidget(m_compassZ);
    vLayout->addLayout(dataLayout);

    vLayout->addSpacing(10);
    vLayout->addWidget(new QLabel("Compass magnitude (uT): "));

    m_compassMagnitude = getFixedPanel("0");
    dataLayout = new QHBoxLayout();
    dataLayout->addSpacing(30);
    dataLayout->addWidget(m_compassMagnitude);
    dataLayout->setAlignment(Qt::AlignLeft);
    vLayout->addLayout(dataLayout);

    vLayout->addSpacing(10);
    vLayout->addWidget(new QLabel("Pressure (hPa), height above sea level (m): "));

    m_pressure = getFixedPanel("0");
    m_height = getFixedPanel("0");
    dataLayout = new QHBoxLayout();
    dataLayout->addSpacing(30);
    dataLayout->addWidget(m_pressure);
    dataLayout->addWidget(m_height);
    dataLayout->setAlignment(Qt::AlignLeft);
    vLayout->addLayout(dataLayout);

    vLayout->addSpacing(10);
    vLayout->addWidget(new QLabel("Temperature (C): "));

    m_temperature = getFixedPanel("0");
    dataLayout = new QHBoxLayout();
    dataLayout->addSpacing(30);
    dataLayout->addWidget(m_temperature);
    dataLayout->setAlignment(Qt::AlignLeft);
    vLayout->addLayout(dataLayout);

    vLayout->addSpacing(10);
    vLayout->addWidget(new QLabel("Humidity (RH): "));

    m_humidity = getFixedPanel("0");
    dataLayout = new QHBoxLayout();
    dataLayout->addSpacing(30);
    dataLayout->addWidget(m_humidity);
    dataLayout->setAlignment(Qt::AlignLeft);
    vLayout->addLayout(dataLayout);

    vLayout->addSpacing(10);

    vLayout->addStretch(1);

    mainLayout->addLayout(vLayout);

    vLayout = new QVBoxLayout();
    vLayout->setContentsMargins(3, 3, 3, 3);
    vLayout->setSpacing(3);

    m_view = new IMUWindow(this);
    vLayout->addWidget(m_view);

    mainLayout->addLayout(vLayout, 1);
    centralWidget()->setLayout(mainLayout);
    setMinimumWidth(1000);
    setMinimumHeight(700);
}

QLabel* IMUView::getFixedPanel(QString text)
{
    QLabel *label = new QLabel(text);
    label->setFrameStyle(QFrame::Panel);
    label->setFixedSize(QSize(100, 16));
    return label;
}

void IMUView::layoutStatusBar()
{
    m_rateStatus = new QLabel(this);
    m_rateStatus->setAlignment(Qt::AlignLeft);
    ui.statusBar->addWidget(m_rateStatus, 1);
}

void IMUView::onAbout()
{
    GUIAboutDlg dlg(this);
    dlg.exec();
}

void IMUView::onBasicSetup()
{
    GUIBasicSetupDlg dlg(this);
    dlg.exec();
}

void IMUView::onTopicSetup()
{
    TopicSetup dlg(this);
    dlg.exec();
}
