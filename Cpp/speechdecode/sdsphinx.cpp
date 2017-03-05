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

#include "LogWrapper.h"
#include "speechdecode.h"

#include "sdsphinx.h"
#include "audiodatadefs.h"
#include "speechdecodedefs.h"
#include "ManifoldThread.h"
#include "ManifoldUtils.h"

#include <qdatetime.h>
#include <qdebug.h>
#include <qsettings.h>
#include <qdir.h>

#include <stdint.h>


#define TAG "SDSphinx"

#define SPEECH_SILENCE                  2048                // max value defined as silence
#define SPEECH_GAP                      500                 // this much silence is a gap
#define SPEECH_MAX_OUTSTANDING_SAMPLES  (16000 * 256)       // max samples before we force recognition

SDSphinx::SDSphinx() : ManifoldThread(TAG)
{
    m_ps = NULL;

    m_timerID = -1;
}

void SDSphinx::initThread()
{
    cmd_ln_t *config;

    QSettings *settings = ManifoldUtils::getSettings();

    settings->beginGroup(SPEECHDECODE_SPHINX_GROUP);

    QString hmmDir = settings->value(SPEECHDECODE_SPHINX_HMMDIR).toString();
    QString phraseDir = settings->value(SPEECHDECODE_SPHINX_PHRASEDIR).toString();
    QString languageModel = settings->value(SPEECHDECODE_SPHINX_MODEL).toString();
    QString dictionary = settings->value(SPEECHDECODE_SPHINX_DICT).toString();

    settings->endGroup();

    delete settings;

    config = cmd_ln_init(NULL, ps_args(), TRUE,
                 "-hmm",qPrintable(hmmDir),
                 "-lm", qPrintable(phraseDir + "/" + languageModel),
                 "-dict", qPrintable(phraseDir + "/" + dictionary),
                 NULL);
    if (config == NULL) {
        logError(TAG, "Failed to load speech recognizer config");
        return;
    }
    m_ps = ps_init(config);
    if (m_ps == NULL) {
        logError(TAG, "Failed to generate speech decoder");
        return;
    }

    if (ps_start_utt(m_ps) < 0) {
        logError(TAG, "Speech decoder failed to start");
        ps_free(m_ps);
        m_ps = NULL;
        return;
    }

    m_silenceStart = 1000;
    m_active = false;
    m_outstandingSamples = 0;

    m_timerID = startTimer(100);
}

void SDSphinx::finishThread()
{
    if (m_timerID != -1) {
        killTimer(m_timerID);
        m_timerID = -1;
    }

    if (m_ps != NULL) {
        ps_free(m_ps);
        m_ps = NULL;
    }
}

void SDSphinx::timerEvent(QTimerEvent *)
{
}

void SDSphinx::newAudio(QJsonObject audioJson, QByteArray audioBinary)
{
    char const *hyp;
    qint32 bestScore;

    if (m_ps == NULL)
        return;

    //  get the actual audio data

    if (!audioJson.contains(AUDIO_DATA_CHANNELS)) {
        logError(TAG, QString("No audio channels in audio message"));
        return;
    }

    if (!audioJson.contains(AUDIO_DATA_RATE)) {
        logError(TAG, QString("No audio rate in audio message"));
        return;
    }

    int rate = audioJson.value(AUDIO_DATA_RATE).toInt();
    int channels = audioJson.value(AUDIO_DATA_CHANNELS).toInt();

    if (rate != 16000) {
        logError(TAG, QString("Unsupported audio rate %1").arg(rate));
        return;
    }

    QByteArray audioData = reformatAudio(audioBinary, channels, rate);

    int sampleCount = audioData.count() / 2;

    silenceDetector(audioData);

    if (m_active) {
        try {
            if (ps_process_raw(m_ps, (const int16 *)audioData.constData(), sampleCount, FALSE, FALSE) < 0) {
                logError(TAG, "Speech decoder generated an error");
                return;
            }
        } catch (int e) {
            logError(TAG, QString("ps_process_raw failed %1").arg(e));
            ps_free(m_ps);
            m_ps = NULL;
            return;
        }
        m_outstandingSamples += sampleCount;
        m_accumulatedAudio += audioData;
    }
    if (m_active && (((QDateTime::currentMSecsSinceEpoch() - m_silenceStart) >= SPEECH_GAP) ||
                    (m_outstandingSamples >= SPEECH_MAX_OUTSTANDING_SAMPLES))) {
        qDebug() << "Processing samples " << m_outstandingSamples;
        m_active = false;
        m_outstandingSamples = false;
        try {
            ps_end_utt(m_ps);
        } catch (int e) {
            logError(TAG, QString("ps_end_utt failed %1").arg(e));
            ps_free(m_ps);
            m_ps = NULL;
            return;
        }
        try {
            hyp = ps_get_hyp(m_ps, &bestScore);
        } catch (int e) {
            logError(TAG, QString("ps_get_hyp failed %1").arg(e));
            ps_free(m_ps);
            m_ps = NULL;
            return;
        }
        processInput(QString(hyp));

        try {
            if (ps_start_utt(m_ps) < 0) {
                logError(TAG, "Speech decoder failed to start");
                ps_free(m_ps);
                m_ps = NULL;
                return;
            }
        } catch (int e) {
            logError(TAG, QString("ps_start_utt failed %1").arg(e));
            ps_free(m_ps);
            m_ps = NULL;
            return;
        }

    }
}


QByteArray SDSphinx::reformatAudio(const QByteArray origData, int channels, int /* rate */)
{
    if (channels != 2)
        return origData;

    QByteArray newData;
    int val1, val2;
    int res;
    int loopCount = origData.count() / 4;

    for (int i = 0, index = 0; i < loopCount; i++, index += 4) {
        val1 = (int)((int16_t)(((uint16_t)origData[index]) + (((uint16_t)origData[index+1]) << 8)));
        val2 = (int)((int16_t)(((uint16_t)origData[index+2]) + (((uint16_t)origData[index+3]) << 8)));
        res = (val1 + val2) / 2;

        newData.append(res & 0xff);
        newData.append((res >> 8) & 0xff);
    }
    return newData;
}

void SDSphinx::processInput(const QString& input)
{
    sendDecodedSpeech(input);
    m_accumulatedAudio.clear();
}

bool SDSphinx::silenceDetector(const QByteArray& audioData)
{
    unsigned char *ptr = (unsigned char *)audioData.data();
    qint64 now = QDateTime::currentMSecsSinceEpoch();
    bool allSilence = true;

    for (int i = 0; i < audioData.length(); i += 2, ptr += 2) {
        short val = (short)((unsigned short)(*ptr) + (((unsigned short)(*(ptr + 1))) << 8));
        if (abs(val) > SPEECH_SILENCE) {
            m_active = true;
            m_silenceStart = now;
            allSilence = false;
        }
    }
    return allSilence;
}

void SDSphinx::sendDecodedSpeech(const QString &text)
{
    if (text.length() == 0)
        return;
    QJsonObject jso;

    qDebug() << text;

    jso[SPEECHDECODE_META_TEXT] = text;
    emit decodedSpeech(jso);
}
