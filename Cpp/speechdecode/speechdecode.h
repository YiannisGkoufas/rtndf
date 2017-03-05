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

#ifndef _SPEECHDECODE_H_
#define _SPEECHDECODE_H_

#include "MainConsole.h"

class speechdecodeClient;

//  Management JSON defs

#define SPEECHDECODE_TOPICCONFIG_NAME     "topicConfig"
#define SPEECHDECODE_TOPICCONFIG_DESC     "Configure topics"

#define SPEECHDECODE_SPHINXCONFIG_NAME    "sphinxConfig"
#define SPEECHDECODE_SPHINXCONFIG_DESC    "Configure Sphinx"

//  Settings keys

#define SPEECHDECODE_PARAMS_TOPIC_GROUP   "speechdecodeTopicGroup"
#define SPEECHDECODE_PARAMS_AUDIO_TOPIC   "audio"
#define SPEECHDECODE_PARAMS_DECODEDSPEECH_TOPIC   "decodedSpeech"

#define SPEECHDECODE_SPHINX_GROUP         "speechDecoder"
#define SPEECHDECODE_SPHINX_HMMDIR        "hmmdir"
#define SPEECHDECODE_SPHINX_PHRASEDIR     "phrasedir"
#define SPEECHDECODE_SPHINX_MODEL         "model"
#define SPEECHDECODE_SPHINX_DICT          "dict"

class SDClient;
class SDSphinx;

class SpeechDecode : public MainConsole
{
    Q_OBJECT

public:
    SpeechDecode(QObject *parent, bool daemonMode);

protected:
    void processInput(char c);

private:
    void showHelp();
    void showStatus();

    SDClient *m_client;
    SDSphinx *m_decoder;
};

#endif // _SPEECHDECODE_H_
