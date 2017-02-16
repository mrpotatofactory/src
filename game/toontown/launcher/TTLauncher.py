from direct.showbase.DirectObject import DirectObject
from direct.directnotify import DirectNotifyGlobal

from panda3d.core import *

import os, sys, time, datetime

class LogAndOutput:
    def __init__(self, orig, log):
        self.orig = orig
        self.log = log

    def write(self, str):
        self.log.write(str)
        self.log.flush()
        self.orig.write(str)
        self.orig.flush()

    def flush(self):
        self.log.flush()
        self.orig.flush()

class LauncherBase(DirectObject):
    def getProductName(self):
        config = getConfigExpress()
        productName = config.GetString('product-name', '')
        if productName and productName != 'DisneyOnline-US':
            productName = '_%s' % productName
        else:
            productName = ''
        return productName

    def isDownloadComplete(self):
        return 1

    def isTestServer(self):
        return 0

    def recordPeriodTimeRemaining(self, secondsRemaining):
        pass

    def setPandaWindowOpen(self):
        pass

    def getPandaErrorCode(self):
        return 0

    def setDisconnectDetailsNormal(self):
        self.notify.info('Setting Disconnect Details normal')
        self.disconnectCode = 0
        self.disconnectMsg = 'normal'

    def setDisconnectDetails(self, newCode, newMsg):
        self.notify.info('New Disconnect Details: %s - %s ' % (newCode, newMsg))
        self.disconnectCode = newCode
        self.disconnectMsg = newMsg

    def setServerVersion(self, version):
        self.ServerVersion = version

    def getServerVersion(self):
        return self.ServerVersion

    def getIsNewInstallation(self):
        return 0

    def setIsNotNewInstallation(self):
        pass

    def getPhaseComplete(self, phase):
        return 1

    def getPercentPhaseComplete(self, phase):
        return 100

    def cleanup(self):
        pass

    def getBlue(self):
        return None

    def getPlayToken(self):
        return None

    def getDISLToken(self):
        return None

class TTLauncher(LauncherBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToontownDummyLauncher')

    def __init__(self):
        self.http = HTTPClient()

        self.logPrefix = 'toontown-'

        ltime = 1 and time.localtime()
        logSuffix = datetime.datetime.now().strftime("%d-%b-%Y_%H_%M_%S")
        
        if not os.path.exists('logs/'):
            os.mkdir('logs/')
            self.notify.info('Made new directory to save logs.')
        
        logfile = os.path.join('logs', self.logPrefix + logSuffix + '.log')

        log = open(logfile, 'a')
        logOut = LogAndOutput(sys.stdout, log)
        logErr = LogAndOutput(sys.stderr, log)
        sys.stdout = logOut
        sys.stderr = logErr

    def getPlayToken(self):
        return self.getValue('TTN_PLAYCOOKIE')

    def getGameServer(self):
        return self.getValue('TTN_GAMESERVER')

    def setPandaErrorCode(self, code):
        pass

    def getGame2Done(self):
        return True

    def getLogFileName(self):
        return 'toontown'

    def getValue(self, key, default=None):
        return os.environ.get(key, default)

    def setValue(self, key, value):
        os.environ[key] = str(value)

    def getVerifyFiles(self):
        return config.GetInt('launcher-verify', 0)

    def getTestServerFlag(self):
        return self.getValue('IS_TEST_SERVER', 0)

    def isDownloadComplete(self):
        return 1

    def isTestServer(self):
        return 0

    def isDummy(self):
        return 0
        