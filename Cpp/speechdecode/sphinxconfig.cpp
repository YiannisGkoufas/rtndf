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

#include <qsettings.h>

#include "sphinxconfig.h"
#include "speechdecode.h"
#include "ManifoldUtils.h"

SphinxConfig::SphinxConfig() : Dialog(SPEECHDECODE_SPHINXCONFIG_NAME, SPEECHDECODE_SPHINXCONFIG_DESC, 600)
{
    setConfigDialog(true);
}

bool SphinxConfig::setVar(const QString& name, const QJsonObject& var)
{
    bool changed = false;

    if (name == "hmmDir") {
        if (m_hmmDir != var.value(MANIFOLDJSON_CONFIG_VAR_VALUE).toString()) {
            changed = true;
            m_hmmDir = var.value(MANIFOLDJSON_CONFIG_VAR_VALUE).toString();
        }
    } else if (name == "phraseDir") {
        if (m_phraseDir != var.value(MANIFOLDJSON_CONFIG_VAR_VALUE).toString()) {
            changed = true;
            m_phraseDir = var.value(MANIFOLDJSON_CONFIG_VAR_VALUE).toString();
        }
    } else if (name == "languageModel") {
        if (m_languageModel != var.value(MANIFOLDJSON_CONFIG_VAR_VALUE).toString()) {
            changed = true;
            m_languageModel = var.value(MANIFOLDJSON_CONFIG_VAR_VALUE).toString();
        }
    } else if (name == "dictionary") {
        if (m_dictionary != var.value(MANIFOLDJSON_CONFIG_VAR_VALUE).toString()) {
            changed = true;
            m_dictionary = var.value(MANIFOLDJSON_CONFIG_VAR_VALUE).toString();
        }
    }
    return changed;
}

void SphinxConfig::getDialog(QJsonObject& newDialog)
{
    clearDialog();
    addVar(createConfigStringVar("hmmDir", "HMM directory", m_hmmDir));
    addVar(createGraphicsLineVar());
    addVar(createConfigStringVar("phraseDir", "Phrase directory", m_phraseDir));
    addVar(createConfigStringVar("languageModel", "Language model file name", m_languageModel));
    addVar(createConfigStringVar("dictionary", "Dictionary file name", m_dictionary));

    return dialog(newDialog);
}

void SphinxConfig::loadLocalData(const QJsonObject& /* param */)
{
    QSettings *settings = ManifoldUtils::getSettings();

    settings->beginGroup(SPEECHDECODE_SPHINX_GROUP);
    m_hmmDir = settings->value(SPEECHDECODE_SPHINX_HMMDIR).toString();
    m_phraseDir = settings->value(SPEECHDECODE_SPHINX_PHRASEDIR).toString();
    m_languageModel = settings->value(SPEECHDECODE_SPHINX_MODEL).toString();
    m_dictionary = settings->value(SPEECHDECODE_SPHINX_DICT).toString();
    settings->endGroup();

    delete settings;
}

void SphinxConfig::saveLocalData()
{
    QSettings *settings = ManifoldUtils::getSettings();

    settings->beginGroup(SPEECHDECODE_SPHINX_GROUP);
    settings->setValue(SPEECHDECODE_SPHINX_HMMDIR, m_hmmDir);
    settings->setValue(SPEECHDECODE_SPHINX_PHRASEDIR, m_phraseDir);
    settings->setValue(SPEECHDECODE_SPHINX_MODEL, m_languageModel);
    settings->setValue(SPEECHDECODE_SPHINX_DICT, m_dictionary);
    settings->endGroup();

    delete settings;
}

