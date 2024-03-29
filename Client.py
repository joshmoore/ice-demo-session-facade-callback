#!/usr/bin/env python
# **********************************************************************
#
# Copyright (c) 2003-2009 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************

import os, sys, Ice

slice_dir = Ice.getSliceDir()
if not slice_dir:
    print sys.argv[0] + ': Slice directory not found.'
    sys.exit(1)

Ice.loadSlice('-I' + slice_dir + ' Callback.ice')
import Demo

class CallbackReceiverI(Demo.CallbackReceiver):
    def callback(self, num, current=None):
        print "received callback #" + str(num)
        if num == 1:
            print "stopping"
            raise SystemExit()

class Client(Ice.Application):
    def run(self, args):
        if len(args) > 1:
            print self.appName() + ": too many arguments"
            return 1

        import Glacier2
        ## Copied from demopy/Glacier2/callback/Client.py
        defaultRouter = self.communicator().getDefaultRouter()
        if not defaultRouter:
            print self.appName() + ": no default router set"
            return 1

        router = Glacier2.RouterPrx.checkedCast(defaultRouter)
        if not router:
            print self.appName() + ": configured router is not a Glacier2 router"
            return 1
        ## End copied

        session = router.createSession("", "")
        server = Demo.CallbackSenderPrx.checkedCast(session)
        if not server:
            print self.appName() + ": invalid proxy"
            return 1

        adapter = self.communicator().createObjectAdapterWithRouter("Callback.Client", router)
        adapter.activate()

        ident = Ice.Identity()
        ident.name = Ice.generateUUID()
        ident.category = router.getCategoryForClient()

        prx = adapter.add(CallbackReceiverI(), ident)
        prx = Demo.CallbackReceiverPrx.uncheckedCast(prx)

        server.addClientObj(prx)
        self.communicator().waitForShutdown()

        print "here"
        return 0

app = Client()
sys.exit(app.main(sys.argv, "config.client"))
