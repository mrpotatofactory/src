import toontown.minigame.MinigameCreatorAI
from toontown.distributed.ToontownInternalRepository import ToontownInternalRepository
from direct.distributed.PyDatagram import *
from otp.distributed.DistributedDirectoryAI import DistributedDirectoryAI
from otp.distributed.OtpDoGlobals import *

from ShardAPIManagerUD import ShardAPIManagerUD
import ShardAPIWebServer
import sys

from toontown.dna.DNAParser import DNAStorage

from BanManagerUD import BanManagerUD
from DistributedTopToonsManagerUD import DistributedTopToonsManagerUD
from DistributedPartyManagerUD import DistributedPartyManagerUD
from toontown.catalog.CatalogManagerUD import CatalogManagerUD
from otp.friends.FriendManagerUD import FriendManagerUD

class ToontownUberRepository(ToontownInternalRepository):
    def __init__(self, baseChannel, serverId):
        ToontownInternalRepository.__init__(self, baseChannel, serverId, dcSuffix='UD')
        self.__dnaMap = {}
        
        self.__closeServerData = [0, '']
        self.__csdIval = 0
        self.accept('GLOBAL_MSG_CLOSING_FOR_UPDATE', self.__handleCloseServer)
        
    def __handleCloseServer(self, time, type):
        resp = ''
        
        if time == 0: # Abort
            if self.__closeServerData[1]:
                self.__closeServerData = [0, '']
                taskMgr.remove('close-server')
                resp = 'Aborted'
                
            else:
                resp = 'Cannot abort: not set'
                
        elif time == 1: # Get
            if not self.__closeServerData[1]:
                resp = 'Not closing'
                
            else:
                resp = 'Closing: ' + self.__closeServerData[1]
                
        else:
            self.__closeServerData = [time * 60, type]
            self.__csdIval = 180 if time < 60 else 1800
            self.__updateCloseStatus()
            taskMgr.doMethodLater(self.__csdIval, self.__updateCloseStatus, 'close-server')
                
        self.sendNetEvent('GLOBAL_MSG_CLOSING_FOR_UPDATE_RESP', [resp])
        
    def __updateCloseStatus(self, task=None):
        ret = None
        
        if task:
            ret = task.again
            self.__closeServerData[0] -= self.__csdIval
            self.__closeServerData[0] = max(0, self.__closeServerData[0])
            
        if not self.__closeServerData[0]:
            msg = 'ADMIN: Toontown is going down for %s right now!' % self.__closeServerData[1]
            
            # Do shutdown next minute
            def do_shutdown():
                self.sendNetEvent('GLOBAL_MSG_CLOSING_FOR_UPDATE_NOW')
                sys.exit(1024)
                
            taskMgr.doMethodLater(60, do_shutdown, 'close-server', extraArgs=[])
            ret = task.done
            
        else:
            msg = 'ADMIN: Toontown is going down for %s in %d minutes!' % (self.__closeServerData[1], self.__closeServerData[0] / 60)
                
        self.sendSysMsgToAll(msg)
  
        return ret
        
    def getDnaStore(self, zoneId):
        if zoneId in self.__dnaMap:
            return self.__dnaMap[zoneId]
            
        x = DNAStorage()
        filename = self.genDNAFileName(zoneId)
        
        print 'Loading dna file', self.genDNAFileName(zoneId)
        self.loadDNAFileAI(x, filename)
        
        self.__dnaMap[zoneId] = x
        
        return x
        
    def handleConnected(self):
        ToontownInternalRepository.handleConnected(self)
        
        self.addExitEvent('uberdogExit')
        
        rootObj = DistributedDirectoryAI(self)
        rootObj.generateWithRequiredAndId(self.getGameDoId(), 0, 0)
        
        self.apiMgr = ShardAPIManagerUD(self)
        self.banMgr = BanManagerUD(self)
        self.catalogManager = CatalogManagerUD(self)
        self.friendManager = FriendManagerUD(self)
        
        self.createGlobals()

        self.removeAtExit(self.partyMgr.doId)
        
        self.apiWS = ShardAPIWebServer.start(self.apiMgr)

    def createGlobals(self):
        self.csm = self.generateGlobalObject(OTP_DO_ID_CLIENT_SERVICES_MANAGER,
                                             'ClientServicesManager')

        self.chatAgent = self.generateGlobalObject(OTP_DO_ID_CHAT_MANAGER,
                                                   'ChatAgent')
        
        self.friendsManager = self.generateGlobalObject(OTP_DO_ID_TT_FRIENDS_MANAGER,
                                                        'TTFriendsManager')

        self.partyMgr = DistributedPartyManagerUD(self)
        self.partyMgr.generateWithRequiredAndId(100004, 0, 0)
        
        if config.GetBool('want-top-toons', True):
            if OTP_DO_ID_TOONTOWN_TOP_TOONS_MGR == 100003:
                self.topToonsMgr = DistributedTopToonsManagerUD(self)
                self.topToonsMgr.generateWithRequiredAndId(100003, self.getGameDoId(), 2)
                
                dg = PyDatagram()
                dg.addServerHeader(100003, self.ourChannel, STATESERVER_OBJECT_SET_AI)
                dg.addChannel(self.ourChannel)
                self.send(dg)
            
            else:
                self.topToonsMgr = self.generateGlobalObject(OTP_DO_ID_TOONTOWN_TOP_TOONS_MGR, 'DistributedTopToonsManager')
                
            self.removeAtExit(self.topToonsMgr.doId)
            
