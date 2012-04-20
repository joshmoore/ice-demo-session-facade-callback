#!/usr/bin/env python
# **********************************************************************
#
# Copyright (c) 2003-2009 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************

import sys, traceback, Ice, Glacier2, Demo

class DummyPermissionsVerifierI(Glacier2.PermissionsVerifier):
    def checkPermissions(self, userId, password, current=None):
        print "verified user `" + userId + "' with password `" + password + "'"
        return (True, "")

class SessionI(Glacier2.Session):
    def __init__(self, userId):
        self.userId = userId

    def destroy(self, current=None):
        print "destroying session for user `" + self.userId + "'"
        current.adapter.remove(current.id)

class SessionManagerI(Glacier2.SessionManager):
    def __init__(self, communicator):
        self._communicator = communicator
        self._backend = self._communicator.propertyToProxy("Callback.Backend")
        print self._backend
        self._backend = Demo.CallbackSenderPrx.checkedCast(self._backend)
        if not self._backend:
            raise Exception("No Backend!")

    def create(self, userId, control, current=None):
        print "creating session for user `" + userId + "'"
        # session = SessionI(userId)
        from Server import CallbackSenderI
        session = CallbackSenderI(self._communicator, control, self._backend)
        session.start()
        prx = current.adapter.addWithUUID(session)
        return Glacier2.SessionPrx.uncheckedCast(prx)

class SessionServer(Ice.Application):
    def run(self, args):
        if len(args) > 1:
            print self.appName() + ": too many arguments"
            return 1

        adapter = self.communicator().createObjectAdapter("SessionServer")
        adapter.add(DummyPermissionsVerifierI(), self.communicator().stringToIdentity("verifier"))
        adapter.add(SessionManagerI(self.communicator()), self.communicator().stringToIdentity("sessionmanager"))
        adapter.activate()
        self.communicator().waitForShutdown()
        return 0

app = SessionServer()
sys.exit(app.main(sys.argv, "config.sessionserver"))
