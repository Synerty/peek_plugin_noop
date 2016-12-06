import logging
import os

from twisted.internet import reactor

from papp_base.server.PappServerMainBase import PappServerMainBase

logger = logging.getLogger(__name__)

class PappServerMain(PappServerMainBase):
    _instance = None

    _title = "Noop for testing"
    _angularAdminModule = "papp-noop-admin.module"

    def _initSelf(self):
        self._instance = self
        self._startLaterCall = None

    @property
    def platform(self):
        return self._platform

    def start(self):
        # Force migration
        from papp_noop.storage import DeclarativeBase
        self._initialiseDb(DeclarativeBase.metadata, __file__)

        from papp_noop.admin import papp_noop
        siteDir = os.path.dirname(papp_noop.__file__)
        self.platform.addStaticResourceDir(siteDir)

        def started():
            self._startLaterCall = None
            logger.info("started")

            from papp_noop.server import NoopCeleryTaskMaster
            NoopCeleryTaskMaster.start()

        self._startLaterCall = reactor.callLater(3.0, started)
        logger.info("starting")

        from papp_noop import admin
        admin.setup(self._platform)

    def stop(self):
        from papp_noop.storage import DeclarativeBase
        DeclarativeBase.__unused="Testing imports, after sys.path.pop() in register"

        if self._startLaterCall:
            self._startLaterCall.cancel()
        logger.info( "stopped")

    def unload(self):
        logger.info("unloaded")

    @property
    def dbOrmSession(self):
        return self._dbConn.getPappOrmSession()

    @property
    def dbEngine(self):
        return self._dbConn._dbEngine

    @property
    def celeryApp(self):
        from papp_noop.worker.NoopCeleryApp import celeryApp
        return celeryApp


def pappServerMain():
    return PappServerMain._instance
