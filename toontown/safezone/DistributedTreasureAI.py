from otp.ai.AIBase import *
from direct.distributed.ClockDelta import *
from direct.distributed import DistributedObjectAI

import TreasureGlobals

from toontown.toonbase import ToontownGlobals

class DistributedTreasureAI(DistributedObjectAI.DistributedObjectAI):

    def __init__(self, air, treasurePlanner, treasureType, x, y, z):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.treasurePlanner = treasurePlanner
        self.treasureType = treasureType
        self.pos = (x, y, z)
        
    def requestGrab(self):
        avId = self.air.getAvatarIdFromSender()
        self.treasurePlanner.grabAttempt(avId, self.getDoId())

    def validAvatar(self, av):
        d = []
        if hasattr(self, 'healAmount'): d = [None, self.healAmount]
        heal = TreasureGlobals.SafeZoneTreasureSpawns.get(self.zoneId, d)
        if heal and not av.isToonedUp():
            heal = heal[1]
            if ToontownGlobals.VALENTINES_DAY in simbase.air.holidayManager.currentHolidays:
                heal = heal * 2 #Doubles the HP value
            av.toonUp(heal)
            return 1
            
        else:
            self.notify.warning('Treasure: validAvatar: TreasureGlobals.SafeZoneTreasureSpawns[%d] not found' % self.zoneId)
        
        return 0

    def getTreasureType(self):
        return self.treasureType

    def d_setGrab(self, avId):
        self.sendUpdate('setGrab', [avId])

    def d_setReject(self):
        self.sendUpdate('setReject', [])

    def getPosition(self):
        return self.pos

    def setPosition(self, x, y, z):
        self.pos = (x, y, z)

    def b_setPosition(self, x, y, z):
        self.setPosition(x, y, z)
        self.d_setPosition(x, y, z)

    def d_setPosition(self, x, y, z):
        self.sendUpdate('setPosition', [x, y, z])
