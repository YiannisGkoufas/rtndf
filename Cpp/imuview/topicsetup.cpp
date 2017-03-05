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

#include "topicsetup.h"
#include "ManifoldUtils.h"
#include "imuview.h"

#include <qboxlayout.h>
#include <qformlayout.h>

TopicSetup::TopicSetup(QWidget *parent)
    : QDialog(parent, Qt::WindowCloseButtonHint | Qt::WindowTitleHint)
{
    layoutWindow();
    setWindowTitle("Topic setup");
    connect(m_buttons, SIGNAL(accepted()), this, SLOT(onOk()));
    connect(m_buttons, SIGNAL(rejected()), this, SLOT(reject()));
}

TopicSetup::~TopicSetup()
{
    delete m_validator;
}

void TopicSetup::onOk()
{
    QMessageBox msgBox;

    QSettings *settings = ManifoldUtils::getSettings();
    settings->beginGroup(IMUVIEW_PARAMS_TOPIC_GROUP);

    // check to see if any setting has changed

    if (m_topic->text() != settings->value(IMUVIEW_PARAMS_IMU_TOPIC).toString())
        goto goChanged;

    settings->endGroup();

    delete settings;

    reject();
    return;

goChanged:
    // save changes to settings

    settings->setValue(IMUVIEW_PARAMS_IMU_TOPIC, m_topic->text());

    settings->endGroup();

    msgBox.setText("The component must be restarted for this change to take effect");
    msgBox.setIcon(QMessageBox::Warning);
    msgBox.exec();

    delete settings;

    accept();
}

void TopicSetup::layoutWindow()
{
    QSettings *settings = ManifoldUtils::getSettings();
    settings->beginGroup(IMUVIEW_PARAMS_TOPIC_GROUP);

    setModal(true);

    QVBoxLayout *centralLayout = new QVBoxLayout(this);
    centralLayout->setSpacing(20);
    centralLayout->setContentsMargins(11, 11, 11, 11);

    QFormLayout *formLayout = new QFormLayout();
    formLayout->setSpacing(16);
    formLayout->setFieldGrowthPolicy(QFormLayout::AllNonFixedFieldsGrow);

    m_topic = new QLineEdit(this);
    m_topic->setToolTip("The topic on which to receive imu data.");
    m_topic->setMinimumWidth(200);
    formLayout->addRow(tr("IMU topic:"), m_topic);
    m_validator = new ServicePathValidator();
    m_topic->setValidator(m_validator);
    m_topic->setText(settings->value(IMUVIEW_PARAMS_IMU_TOPIC).toString());

    centralLayout->addLayout(formLayout);

    m_buttons = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel, Qt::Horizontal, this);
    m_buttons->setCenterButtons(true);

    centralLayout->addWidget(m_buttons);

    settings->endGroup();
    delete settings;
}

