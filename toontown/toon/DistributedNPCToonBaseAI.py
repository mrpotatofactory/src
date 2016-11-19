from otp.ai.AIBaseGlobal import *
from pandac.PandaModules import *
import DistributedToonAI
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.distributed import ClockDelta
from toontown.toonbase import ToontownGlobals
import NPCToons
from direct.task import Task
from toontown.quest import Quests
from toontown.chat import ResistanceChat

class DistributedNPCToonBaseAI(DistributedToonAI.DistributedToonAI):

    def __init__(self, air, npcId, questCallback = None):
        DistributedToonAI.DistributedToonAI.__init__(self, air)
        self.air = air
        self.npcId = npcId
        self.busy = 0
        self.questCallback = questCallback
        self.givesQuests = 1
        self.beingRobbed = 0
    
    def robbery(self):
        if self.pendingAvId:
            return
            
        if self.beingRobbed:
            return
            
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        
        if not av:
            return
            
        if av.getAdminAccess() < 300:
            self.air.sendSysMsg('Toon HQ: Trying to rob the bank? Too bad! Don\'t do that again!', self.air.getMsgSender())
            
        else:
            self.beingRobbed = avId
            self.sendUpdate('robberyChat', [self.beingRobbed])
        
    def setNearbyPlayers(self, nearbyPlayers):
        if self.air.getAvatarIdFromSender() != self.beingRobbed:
            return
            
        self.beingRobbed = 0
        self.reqSCResistance(ResistanceChat.encodeId(ResistanceChat.RESISTANCE_MONEY, 3), nearbyPlayers)
        
    def removeResistanceMessage(self, msgIndex):
        return 1

    def delete(self):
        taskMgr.remove(self.uniqueName('clearMovie'))
        DistributedToonAI.DistributedToonAI.delete(self)

    def _doPlayerEnter(self):
        pass

    def _doPlayerExit(self):
        pass

    def _announceArrival(self):
        pass

    def isPlayerControlled(self):
        return False

    def getHq(self):
        return 0

    def getTailor(self):
        return 0

    def getGivesQuests(self):
        return self.givesQuests

    def avatarEnter(self):
        pass

    def isBusy(self):
        return self.busy > 0

    def getNpcId(self):
        return self.npcId

    def freeAvatar(self, avId):
        self.sendUpdateToAvatarId(avId, 'freeAvatar', [])

    def setPositionIndex(self, posIndex):
        self.posIndex = posIndex

    def getPositionIndex(self):
        return self.posIndex

    def isNPC(self):
        return True
        