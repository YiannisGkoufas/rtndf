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

#include <qbytearray.h>
#include <qbuffer.h>
#include <qjsonarray.h>
#include <qsettings.h>
#include <qdebug.h>
#include <qdatetime.h>

#include "imuclient.h"
#include "LogWrapper.h"
#include "imuview.h"
#include "ManifoldJSON.h"
#include "rtndfdefs.h"
#include "imudatadefs.h"

#define TAG "IMUClient"

IMUClient::IMUClient() : Endpoint(10, TAG)
{
    m_port = -1;
}
void IMUClient::appClientInit()
{
    QSettings *settings = ManifoldUtils::getSettings();
    settings->beginGroup(IMUVIEW_PARAMS_TOPIC_GROUP);

    m_port = clientAddService(settings->value(IMUVIEW_PARAMS_IMU_TOPIC).toString(), SERVICETYPE_MULTICAST, false);

    settings->endGroup();

    delete settings;
}

void IMUClient::appClientExit()
{
    if (m_port != -1)
        clientRemoveService(m_port);
    m_port = -1;
}

void IMUClient::appClientReceiveMulticast(int /* servicePort */, MANIFOLD_EHEAD *header, int len)
{
    QJsonObject jsonData;
    QByteArray binaryData;

    if (ManifoldUtils::crackJSONBinary(header, len, jsonData, binaryData))
        emit newIMUData(jsonData);
    clientSendMulticastAck(m_port);
    free(header);
}

