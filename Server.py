#!/usr/bin/env python
# **********************************************************************
#
# Copyright (c) 2003-2009 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************

import os, sys, traceback, threading, Ice, Glacier2

slice_dir = Ice.getSliceDir()
if not slice_dir:
    print sys.argv[0] + ': Slice directory not found.'
    sys.exit(1)

Ice.loadSlice('-I' + slice_dir + ' Callback.ice')
import Demo

class CallbackSenderI(Demo.CallbackSender, threading.Thread, Glacier2.Session): # Inheritance from Session added
    def __init__(self, communicator, control):
        threading.Thread.__init__(self)
        self._communicator = communicator
        self._control = control
        self._destroy = False
        self._clients = []
        self._cond = threading.Condition()

    def destroy(self, current=None):
        self._cond.acquire()

        print "destroying callback sender"
        self._destroy = True

        try:
            self._cond.notify()
        finally:
            self._cond.release()

        self.join()

    def addClientObj(self, obj, current=None):
        self._cond.acquire()

        print "adding client `" + str(obj) + "'"

        # Immediate call
        obj.callback(-1)

        # Delayed call
        self._clients.append(obj)

        self._cond.release()

    def run(self):
        num = 0

        while True:

            self._cond.acquire()
            try:
                self._cond.wait(2)
                if self._destroy:
                    break
                clients = self._clients[:]
            finally:
                self._cond.release()

            if len(clients) > 0:
                num = num + 1

                for p in clients:
                    try:
                        p.callback(num)
                    except Ice.UnknownLocalException, exception:
                        if "ConnectionLost" not in exception.unknown:
                            traceback.print_exc()
                        print "removing client `" + self._communicator.identityToString(p.ice_getIdentity()) + "':"

                        self._cond.acquire()
                        try:
                            self._clients.remove(p)
                        finally:
                            self._cond.release()

                        
class Server(Ice.Application):
    def run(self, args):
        if len(args) > 1:
            print self.appName() + ": too many arguments"
            return 1

        adapter = self.communicator().createObjectAdapter("Callback.Server")
        sender = CallbackSenderI(self.communicator())
        adapter.add(sender, self.communicator().stringToIdentity("sender"))
        adapter.activate()

        sender.start()
        try:
            self.communicator().waitForShutdown()
        finally:
            sender.destroy()

        return 0

if __name__ == "__main__": ## Added to allow reuse
    app = Server()
    sys.exit(app.main(sys.argv, "config.server"))
