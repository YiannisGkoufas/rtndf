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

#include "speechdecode.h"
#include "sdclient.h"
#include "topicconfig.h"
#include "sphinxconfig.h"
#include "sdsphinx.h"

#include "ManifoldJSON.h"
#include <stdio.h>

SpeechDecode::SpeechDecode(QObject *parent, bool daemonMode) : MainConsole(parent, daemonMode)
{
    m_client = new SDClient();
    m_decoder = new SDSphinx();

    connect(m_decoder, SIGNAL(decodedSpeech(QJsonObject)), m_client, SLOT(decodedSpeech(QJsonObject)));
    connect(m_client, SIGNAL(newAudio(QJsonObject)), m_decoder, SLOT(newAudio(QJsonObject)));

    addStandardDialogs();

    TopicConfig *topicConfig = new TopicConfig();
    ManifoldJSON::addConfigDialog(topicConfig);

    SphinxConfig *sphinxConfig = new SphinxConfig();
    ManifoldJSON::addConfigDialog(sphinxConfig);

    m_client->resumeThread();
    m_decoder->resumeThread();

    startServices();
}

void SpeechDecode::showHelp()
{
    printf("\nOptions are:\n\n");
    printf("  H - Show help\n");
    printf("  X - Exit\n");
}

void SpeechDecode::processInput(char c)
{
    switch (c) {
    case 'H':
        showHelp();
        break;
    }

    printf("\n");
}
