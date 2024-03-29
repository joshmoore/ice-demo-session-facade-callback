// **********************************************************************
//
// Copyright (c) 2003-2009 ZeroC, Inc. All rights reserved.
//
// This copy of Ice is licensed to you under the terms described in the
// ICE_LICENSE file included in this distribution.
//
// **********************************************************************

#ifndef CALLBACK_ICE
#define CALLBACK_ICE

#include <Ice/Identity.ice>

module Demo
{

interface CallbackReceiver
{
    void callback(int num);
};

interface CallbackSender
{
    void addClientObj(CallbackReceiver* prx);
};

};

#endif
