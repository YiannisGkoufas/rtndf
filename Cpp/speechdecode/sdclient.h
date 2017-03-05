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

#ifndef _SDCLIENT_H_
#define _SDCLIENT_H_

#include "Endpoint.h"
#include <qjsonobject.h>

class SDClient : public Endpoint
{
    Q_OBJECT

public:
    SDClient();

public slots:
    void decodedSpeech(QJsonObject decodedSpeech);

signals:
    void newAudio(QJsonObject json, QByteArray binaryData);

protected:
    void appClientInit();
    void appClientExit();
    void appClientReceiveMulticast(int servicePort, MANIFOLD_EHEAD *header, int len);

private:
    int m_inPort;
    int m_outPort;
};

#endif // _SDCLIENT_H_

