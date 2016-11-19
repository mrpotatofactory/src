from direct.distributed.AstronInternalRepository import *

from ToontownNetMessengerAI import ToontownNetMessengerAI
from toontown.dna.DNAParser import DNALoader
from toontown.toonbase import ToontownGlobals
from toontown.hood import ZoneUtil

from otp.distributed.OtpDoGlobals import *

import sys, traceback, time, datetime, os

airDBBackend = config.GetString('air-db-backend', 'sqlite3')
if airDBBackend == 'mongodb':
    import pymongo
    
elif airDBBackend == 'sqlite3':
    import sqlite3
    
else:
    raise ValueError('unknown db: %s' % airDBBackend)

class ForceExit(Exception):
    pass

class ToontownInternalRepository(AstronInternalRepository):
    GameGlobalsId = OTP_DO_ID_TOONTOWN
    dbId = 4003
    serverDataFolder = config.GetString('server-data-folder', 'databases')
    
    def __init__(self, baseChannel, serverId=None, dcFileNames = None,
                 dcSuffix = 'AI', connectMethod = None, threadedNet = None):
        if connectMethod is None:
            connectMethod = self.CM_NATIVE
            
        AstronInternalRepository.__init__(self, baseChannel, serverId, dcFileNames, dcSuffix, connectMethod, threadedNet)
            
        self.__loader = DNALoader()
        
    def handleConnected(self):
        self.__messenger = ToontownNetMessengerAI(self)
        
        self.dbConnType = airDBBackend
        
        if airDBBackend == 'sqlite3':
            self.dbConn = sqlite3.connect('%s/%s.db' % (self.serverDataFolder, self.ourChannel))
            self.dbCursor = self.dbConn.cursor()
            
        elif airDBBackend == 'mongodb':
            self.dbConn = pymongo.MongoClient(config.GetString('mongodb-url', 'localhost'))
            self.dbGlobalCursor = self.dbConn.toontown
            self.dbCursor = self.dbGlobalCursor['air-%d' % self.ourChannel]
        
    def readerPollOnce(self):
        try:
            return AstronInternalRepository.readerPollOnce(self)
            
        except SystemExit, KeyboardInterrupt:
            raise
            
        except ForceExit:
            os._exit(0)
            
        except Exception as e:
            if config.GetBool('want-kick-crasher', True):
                if self.getAvatarIdFromSender() > 100000000:
                    # remove the av that caused the exception
                    # since it could be a harmful hacker
                    # or simply because it could break some logic
                    dg = PyDatagram()
                    dg.addServerHeader(self.getMsgSender(), self.ourChannel, CLIENTAGENT_EJECT)
                    dg.addUint16(166)
                    dg.addString('You were disconnected to prevent a district reset.')
                    self.send(dg)
                
            self.writeServerEvent('INTERNAL-EXCEPTION', self.getAvatarIdFromSender(), self.getAccountIdFromSender(), repr(e), traceback.format_exc())
            self.notify.warning('INTERNAL-EXCEPTION: %s (%s)' % (repr(e), self.getAvatarIdFromSender()))
            print traceback.format_exc()
            sys.exc_clear()
            
        return 1

    def getAvatarIdFromSender(self):
        return self.getMsgSender() & 0xFFFFFFFF

    def getAccountIdFromSender(self):
        return (self.getMsgSender()>>32) & 0xFFFFFFFF

    def _isValidPlayerLocation(self, parentId, zoneId):
        if zoneId < 1000 and zoneId != 1:
            return False

        return True

    def sendSysMsg(self, message, channel):
        msgDg = PyDatagram()
        msgDg.addUint16(6)
        msgDg.addString(message)

        dg = PyDatagram()
        dg.addServerHeader(channel, self.ourChannel, CLIENTAGENT_SEND_DATAGRAM)
        dg.addString(msgDg.getMessage())
        self.send(dg)
        
    def sendSysMsgToAll(self, message):
        self.sendSysMsg(message, 10)
    
    def getApiKey(self):
        try:
            f = open('../api.key', 'rb')
            key = f.read()
            f.close()
        
            return key.strip()
        
        except:
            return 'dev'
            
    def genDNAFileName(self, zoneId):
        zoneId = ZoneUtil.getCanonicalZoneId(zoneId)
        hoodId = ZoneUtil.getCanonicalHoodId(zoneId)
        hood = ToontownGlobals.dnaMap[hoodId]
        if hoodId == zoneId:
            zoneId = 'sz'
            phase = ToontownGlobals.phaseMap[hoodId]
        else:
            phase = ToontownGlobals.streetPhaseMap[hoodId]

        return 'phase_%s/dna/%s_%s.dna' % (phase, hood, zoneId)

    def loadDNAFileAI(self, dnastore, filename):
        f = Filename('../resources/' + str(filename))
        f.setExtension('pdna')
        return self.__loader.loadDNAFileAI(dnastore, f)
        
    def sendNetEvent(self, message, sentArgs=[]):
        self.__messenger.send(message, sentArgs)
        
    def addExitEvent(self, message):
        dg = self.__messenger.prepare(message)
        self.addPostRemove(dg)
        
    def handleDatagram(self, di):
        msgType = self.getMsgType()
        
        if msgType == self.__messenger.msgType:
            self.__messenger.handle(msgType, di)
            return
        
        AstronInternalRepository.handleDatagram(self, di)
        
    def removeAtExit(self, doId):
        dg = PyDatagram()
        dg.addServerHeader(doId, self.ourChannel, STATESERVER_OBJECT_DELETE_RAM)
        dg.addUint32(doId)
        self.addPostRemove(dg)
        