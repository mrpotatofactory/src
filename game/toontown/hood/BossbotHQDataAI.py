# File: B (Python 2.4)

from pandac.PandaModules import Point3
from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.toonbase import ToontownGlobals
from toontown.coghq import DistributedCogHQDoorAI
from toontown.building import DistributedDoorAI
from toontown.building import DoorTypes
from toontown.coghq import LobbyManagerAI
from toontown.building import DistributedBossElevatorAI
from toontown.suit import DistributedBossbotBossAI
from toontown.building import DistributedBBElevatorAI
from toontown.building import DistributedBoardingPartyAI
from toontown.building import DistributedTowerBuildingAI
from toontown.building import FADoorCodes
from toontown.coghq import DistributedCogKartAI

class BossbotHQDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('BossbotHQDataAI')
    
    zoneId = ToontownGlobals.BossbotHQ
    wantTrolley = False
    
    def startup(self):
        self.lobbyMgr = LobbyManagerAI.LobbyManagerAI(self.air, DistributedBossbotBossAI.DistributedBossbotBossAI)
        self.lobbyMgr.generateWithRequired(ToontownGlobals.BossbotLobby)
        self.lobbyElevator = DistributedBBElevatorAI.DistributedBBElevatorAI(self.air, self.lobbyMgr, ToontownGlobals.BossbotLobby, antiShuffle = 1)
        self.lobbyElevator.generateWithRequired(ToontownGlobals.BossbotLobby)
        if simbase.config.GetBool('want-boarding-groups', 1):
            self.boardingParty = DistributedBoardingPartyAI.DistributedBoardingPartyAI(self.air, [
                self.lobbyElevator.doId], 8)
            self.boardingParty.generateWithRequired(ToontownGlobals.BossbotLobby)
        
        
        def makeDoor(destinationZone, intDoorIndex, extDoorIndex, lock = 0):
            intDoor = DistributedCogHQDoorAI.DistributedCogHQDoorAI(self.air, 0, DoorTypes.INT_COGHQ, self.zoneId, doorIndex = intDoorIndex, lockValue = lock)
            intDoor.zoneId = destinationZone
            extDoor = DistributedCogHQDoorAI.DistributedCogHQDoorAI(self.air, 0, DoorTypes.EXT_COGHQ, destinationZone, doorIndex = extDoorIndex, lockValue = lock)
            extDoor.setOtherDoor(intDoor)
            intDoor.setOtherDoor(extDoor)
            intDoor.generateWithRequired(destinationZone)
            intDoor.sendUpdate('setDoorIndex', [
                intDoor.getDoorIndex()])
            extDoor.generateWithRequired(self.zoneId)
            extDoor.sendUpdate('setDoorIndex', [
                extDoor.getDoorIndex()])

        makeDoor(ToontownGlobals.BossbotLobby, 0, 0, FADoorCodes.BB_DISGUISE_INCOMPLETE)
        kartIdList = self.createCogKarts()
        if simbase.config.GetBool('want-boarding-groups', 1):
            self.courseBoardingParty = DistributedBoardingPartyAI.DistributedBoardingPartyAI(self.air, kartIdList, 4)
            self.courseBoardingParty.generateWithRequired(self.zoneId)
            
        self.createTowerBuildings()
        self.notify.info('Started up')
        
    def createTowerBuildings(self):
        self.towers = []
        for i in xrange(32):
            t = DistributedTowerBuildingAI.DistributedTowerBuildingAI(self.air, i, ToontownGlobals.TowersLobby, None)
            t.generateWithRequired(ToontownGlobals.TowersLobby)
            self.towers.append(t)
    
    def createCogKarts(self):
        self.cogKarts = []
        posList = ((154.762, 37.168999999999997, 0), (141.40299999999999, -81.887, 0), (-48.439999999999998, 15.308, 0))
        hprList = ((110.815, 0, 0), (61.231000000000002, 0, 0), (-105.48099999999999, 0, 0))
        mins = ToontownGlobals.FactoryLaffMinimums[3]
        kartIdList = []
        for cogCourse in xrange(len(posList)):
            pos = posList[cogCourse]
            hpr = hprList[cogCourse]
            cogKart = DistributedCogKartAI.DistributedCogKartAI(self.air, cogCourse, pos[0], pos[1], hpr[0], self.air.countryClubMgr, mins[cogCourse])
            cogKart.generateWithRequired(self.zoneId)
            self.cogKarts.append(cogKart)
            kartIdList.append(cogKart.doId)
        
        return kartIdList


