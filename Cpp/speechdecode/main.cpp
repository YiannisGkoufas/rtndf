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
#include "speechdecodewindow.h"
#include "ManifoldUtils.h"

#include <qapplication.h>
#include <qsettings.h>

int runGuiApp(int argc, char **);
int runConsoleApp(int argc, char **);
void presetDefaultSettings();

int main(int argc, char *argv[])
{
    if (ManifoldUtils::checkConsoleModeFlag(argc, argv))
        return runConsoleApp(argc, argv);
    else
        return runGuiApp(argc, argv);
}

int runGuiApp(int argc, char **argv)
{
    QApplication a(argc, argv);

    ManifoldUtils::loadStandardSettings("speechdecode", a.arguments());
    presetDefaultSettings();
    SpeechDecodeWindow *w = new SpeechDecodeWindow();
    w->show();
    return a.exec();
}

int runConsoleApp(int argc, char **argv)
{
    QCoreApplication a(argc, argv);

    ManifoldUtils::loadStandardSettings("speechdecode", a.arguments());
    presetDefaultSettings();
    SpeechDecode cc(&a, ManifoldUtils::checkDaemonModeFlag(argc, argv));
    return a.exec();
}

void presetDefaultSettings()
{
    QSettings *settings = ManifoldUtils::getSettings();

    settings->beginGroup(SPEECHDECODE_PARAMS_TOPIC_GROUP);
    if (!settings->contains(SPEECHDECODE_PARAMS_AUDIO_TOPIC))
        settings->setValue(SPEECHDECODE_PARAMS_AUDIO_TOPIC, "audio/audio");
    if (!settings->contains(SPEECHDECODE_PARAMS_DECODEDSPEECH_TOPIC))
        settings->setValue(SPEECHDECODE_PARAMS_DECODEDSPEECH_TOPIC, "decodedspeech");

    settings->endGroup();

    settings->beginGroup(SPEECHDECODE_SPHINX_GROUP);
    if (!settings->contains(SPEECHDECODE_SPHINX_HMMDIR))
        settings->setValue(SPEECHDECODE_SPHINX_HMMDIR, "/usr/local/share/pocketsphinx/model/en-us/en-us");
    if (!settings->contains(SPEECHDECODE_SPHINX_PHRASEDIR))
        settings->setValue(SPEECHDECODE_SPHINX_PHRASEDIR, "/usr/local/share/pocketsphinx/model/en-us/");
    if (!settings->contains(SPEECHDECODE_SPHINX_MODEL))
        settings->setValue(SPEECHDECODE_SPHINX_MODEL, "en-us.lm.bin");
    if (!settings->contains(SPEECHDECODE_SPHINX_DICT))
        settings->setValue(SPEECHDECODE_SPHINX_DICT, "cmudict-en-us.dict");
    settings->endGroup();

    delete settings;

}

