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
#include <qjsondocument.h>
#include <qbuffer.h>
#include <qjsonarray.h>
#include <qsettings.h>
#include <qdebug.h>
#include <qdatetime.h>

#include "sdclient.h"
#include "LogWrapper.h"
#include "speechdecode.h"
#include "ManifoldJSON.h"
#include "rtndfdefs.h"
#include "speechdecodedefs.h"

#define TAG "SDClient"

SDClient::SDClient() : Endpoint(10, TAG)
{
    m_inPort = -1;
    m_outPort = -1;
}
void SDClient::appClientInit()
{
    QSettings *settings = ManifoldUtils::getSettings();

    settings->beginGroup(SPEECHDECODE_PARAMS_TOPIC_GROUP);

    if (!settings->contains(SPEECHDECODE_PARAMS_DECODEDSPEECH_TOPIC))
        settings->setValue(SPEECHDECODE_PARAMS_DECODEDSPEECH_TOPIC, "decodedspeech");

    m_inPort = clientAddService(settings->value(SPEECHDECODE_PARAMS_AUDIO_TOPIC).toString(), SERVICETYPE_MULTICAST, false);
    m_outPort = clientAddService(settings->value(SPEECHDECODE_PARAMS_DECODEDSPEECH_TOPIC).toString(), SERVICETYPE_MULTICAST, true);

    delete settings;

}

void SDClient::appClientExit()
{
    if (m_inPort != -1)
        clientRemoveService(m_inPort);
    m_inPort = -1;
    if (m_outPort != -1)
        clientRemoveService(m_outPort);
    m_outPort = -1;
 }

void SDClient::appClientReceiveMulticast(int /* servicePort */, MANIFOLD_EHEAD *header, int len)
{
    QJsonObject jsonData;
    QByteArray binaryData;

    if (ManifoldUtils::crackJSONBinary(header, len, jsonData, binaryData))
        emit newAudio(jsonData, binaryData);
    clientSendMulticastAck(m_inPort);
    free(header);
}

void SDClient::decodedSpeech(QJsonObject decodedSpeech)
{
    if (m_outPort == -1)
        return;

    if (!clientIsServiceActive(m_outPort) || !clientClearToSend(m_outPort))
        return;

    decodedSpeech[RTNDF_TIMESTAMP] = (double)QDateTime::currentMSecsSinceEpoch() / 1000.0;
    decodedSpeech[RTNDF_TOPIC] = "speech";
    decodedSpeech[RTNDF_DEVICEID] = "speechdecode";
    decodedSpeech[RTNDF_TYPE] = SPEECHDECODE_META_TYPE;

    QByteArray message = ManifoldUtils::buildJSONBinary(decodedSpeech, QByteArray());

    MANIFOLD_EHEAD *header = clientBuildMessage(m_outPort, message.length(), ManifoldUtils::currentTimestamp());
    if (header == NULL)
        return;
    memcpy((char *)(header + 1), message.data(), message.length());
    clientSendMessage(m_outPort, header, message.length(), MANIFOLDLINK_LOWPRI);
}
