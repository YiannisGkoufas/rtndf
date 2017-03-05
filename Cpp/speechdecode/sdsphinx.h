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

#ifndef _SDSPHINX_H_
#define _SDSPHINX_H_

#include "pocketsphinx.h"
#include <sphinxbase/err.h>

#include <qstringlist.h>
#include <qjsonobject.h>
#include <qnetworkaccessmanager.h>
#include <qprocess.h>

#include "ManifoldThread.h"

//  Note: this module only processes signed 16 bit, little endian, 16000 sps, 1 or 2 channel data.
//
//  Since Sphinx only supports 1 channel, if the data is two channel, the channels are averaged


class SDSphinx : public ManifoldThread
{
    Q_OBJECT

public:
    SDSphinx();

public slots:
    void newAudio(QJsonObject audioJson, QByteArray audioBinary);

signals:
    void decodedSpeech(QJsonObject speech);
    void sendControl(QString message);

protected:
    void initThread();
    void finishThread();
    void timerEvent(QTimerEvent *);

private:
    QByteArray reformatAudio(const QByteArray origData, int channels, int rate);
    void processInput(const QString& input);
    bool silenceDetector(const QByteArray& audioData);
    void sendDecodedSpeech(const QString& text);

    QByteArray m_accumulatedAudio;

    qint64 m_silenceStart;
    bool m_active;

    ps_decoder_t *m_ps;
    int m_outstandingSamples;

    int m_timerID;

};

#endif // _SDSPHINX_H_

