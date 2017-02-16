from direct.distributed.AstronInternalRepository import *
from otp.ai.MagicWordGlobal import *

from DistributedBuildingAI import *
from DistributedTowerInteriorAI import *
from toontown.suit import SuitDNA

class DistributedTowerBuildingAI(DistributedBuildingAI):
    def __init__(self, air, blockNumber, zoneId, trophyMgr):
        DistributedBuildingAI.__init__(self, air, blockNumber, zoneId, trophyMgr)
        self.nextZone = self.air.allocateZone()
        
        self.difficulty = blockNumber % SuitDNA.suitsPerDept
        if self.difficulty != 1:
            self.difficulty += 1
            
        self.track = ('c', 'l', 'm', 's')[blockNumber // SuitDNA.suitsPerDept]
        self.numFloors = SuitBuildingGlobals.SuitBuildingInfo[self.difficulty][0][1]
        
    def announceGenerate(self):
        DistributedBuildingAI.announceGenerate(self)
        self.setState('suit')

    def getPickleData(self):
        raise ValueError('Trying to get storable data from DistributedTowerBuildingAI')

    def getExteriorAndInteriorZoneId(self):
        return (self.zoneId, self.nextZone)

    def b_setVictorList(self, victorList):
        raise ValueError('Trying to set victor list in DistributedTowerBuildingAI')

    def d_setVictorList(self, victorList):
        raise ValueError('Trying to set victor list in DistributedTowerBuildingAI')

    def setVictorList(self, victorList):
        raise ValueError('Trying to set victor list in DistributedTowerBuildingAI')

    def setVictorReady(self):
        avId = self.air.getAvatarIdFromSender()
        self.air.writeServerEvent('suspicious', avId, 'DistributedTowerBuildingAI.setVictorReady')

    def getBuildingHash(self):
        raise ValueError('Trying to get storable data from DistributedTowerBuildingAI')

    def updateSavedBy(self, savedBy):
        return

    def enterWaitForVictors(self, victorList, savedBy):
        raise ValueError('Trying to enter waitForVictors list in DistributedTowerBuildingAI')

    def enterWaitForVictorsFromCogdo(self, victorList, savedBy):
        raise ValueError('Trying to enter waitForVictorsFromCogdo list in DistributedTowerBuildingAI')

    def createExteriorDoor(self):
        raise ValueError('Trying to create ext door in DistributedTowerBuildingAI')

    def enterSuit(self):
        self.sendUpdate('setSuitData', [ord(self.track), self.difficulty, self.numFloors])
        self.d_setState('suit')
        (exteriorZoneId, interiorZoneId) = self.getExteriorAndInteriorZoneId()
        self.elevator = DistributedElevatorExtAI.DistributedElevatorExtAI(self.air, self)
        self.elevator.generateWithRequired(exteriorZoneId)

    def exitSuit(self):
        raise ValueError('Trying to exit suit state in DistributedTowerBuildingAI')

    def _createSuitInterior(self):
        return DistributedTowerInteriorAI(self.air, self.elevator)
        self.nextZone = self.air.allocateZone()

    def broadcastBuildingEvent(self):
        raise ValueError('Trying to broadcastBuildingEvent in DistributedTowerBuildingAI')
        
@magicWord(chains=[CHAIN_HEAD], types=[int])  
def trollNoobLobby(mt=1):
    for x in set([spellbook.getInvoker(), spellbook.getTarget()]):
        if x == spellbook.getInvoker() and not mt:
            continue
            
        msgDg = PyDatagram()
        msgDg.addUint16(42069)

        dg = PyDatagram()
        dg.addServerHeader(x.GetPuppetConnectionChannel(x.doId), x.air.ourChannel, CLIENTAGENT_SEND_DATAGRAM)
        dg.addString(msgDg.getMessage())
        x.air.send(dg)
