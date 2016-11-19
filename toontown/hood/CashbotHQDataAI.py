# File: C (Python 2.4)

from direct.directnotify import DirectNotifyGlobal
import HoodDataAI
from toontown.toonbase import ToontownGlobals
from toontown.coghq import DistributedMintElevatorExtAI
from toontown.coghq import DistributedCogHQDoorAI
from toontown.building import DoorTypes
from toontown.coghq import LobbyManagerAI
from toontown.building import DistributedCFOElevatorAI
from toontown.suit import DistributedCashbotBossAI, DistributedSuitPlannerAI
from toontown.building import FADoorCodes
from toontown.building import DistributedBoardingPartyAI

class CashbotHQDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('CashbotHqDataAI')
     
    zoneId = ToontownGlobals.CashbotHQ
    wantTrolley = False
    
    def startup(self):
        mins = ToontownGlobals.FactoryLaffMinimums[1]
        self.testElev0 = DistributedMintElevatorExtAI.DistributedMintElevatorExtAI(self.air, self.air.mintMgr, ToontownGlobals.CashbotMintIntA, antiShuffle = 0, minLaff = mins[0])
        self.testElev0.generateWithRequired(ToontownGlobals.CashbotHQ)
        self.testElev1 = DistributedMintElevatorExtAI.DistributedMintElevatorExtAI(self.air, self.air.mintMgr, ToontownGlobals.CashbotMintIntB, antiShuffle = 0, minLaff = mins[1])
        self.testElev1.generateWithRequired(ToontownGlobals.CashbotHQ)
        self.testElev2 = DistributedMintElevatorExtAI.DistributedMintElevatorExtAI(self.air, self.air.mintMgr, ToontownGlobals.CashbotMintIntC, antiShuffle = 0, minLaff = mins[2])
        self.testElev2.generateWithRequired(ToontownGlobals.CashbotHQ)
        self.lobbyMgr = LobbyManagerAI.LobbyManagerAI(self.air, DistributedCashbotBossAI.DistributedCashbotBossAI)
        self.lobbyMgr.generateWithRequired(ToontownGlobals.CashbotLobby)
        self.lobbyElevator = DistributedCFOElevatorAI.DistributedCFOElevatorAI(self.air, self.lobbyMgr, ToontownGlobals.CashbotLobby, antiShuffle = 1)
        self.lobbyElevator.generateWithRequired(ToontownGlobals.CashbotLobby)
        if simbase.config.GetBool('want-boarding-groups', 1):
            self.boardingParty = DistributedBoardingPartyAI.DistributedBoardingPartyAI(self.air, [
                self.lobbyElevator.doId], 8)
            self.boardingParty.generateWithRequired(ToontownGlobals.CashbotLobby)
        
        destinationZone = ToontownGlobals.CashbotLobby
        extDoor0 = DistributedCogHQDoorAI.DistributedCogHQDoorAI(self.air, 0, DoorTypes.EXT_COGHQ, destinationZone, doorIndex = 0, lockValue = FADoorCodes.CB_DISGUISE_INCOMPLETE)
        extDoorList = [
            extDoor0]
        intDoor0 = DistributedCogHQDoorAI.DistributedCogHQDoorAI(self.air, 0, DoorTypes.INT_COGHQ, ToontownGlobals.CashbotHQ, doorIndex = 0)
        intDoor0.setOtherDoor(extDoor0)
        intDoor0.zoneId = ToontownGlobals.CashbotLobby
        mintIdList = [
            self.testElev0.doId,
            self.testElev1.doId,
            self.testElev2.doId]
        if simbase.config.GetBool('want-boarding-groups', 1):
            self.mintBoardingParty = DistributedBoardingPartyAI.DistributedBoardingPartyAI(self.air, mintIdList, 4)
            self.mintBoardingParty.generateWithRequired(self.zoneId)
        
        for extDoor in extDoorList:
            extDoor.setOtherDoor(intDoor0)
            extDoor.zoneId = ToontownGlobals.CashbotHQ
            extDoor.generateWithRequired(ToontownGlobals.CashbotHQ)
            extDoor.sendUpdate('setDoorIndex', [
                extDoor.getDoorIndex()])
        
        intDoor0.generateWithRequired(ToontownGlobals.CashbotLobby)
        intDoor0.sendUpdate('setDoorIndex', [
            intDoor0.getDoorIndex()])

        sp = DistributedSuitPlannerAI.DistributedSuitPlannerAI(self.air, ToontownGlobals.CashbotHQ)
        sp.generateWithRequired(ToontownGlobals.CashbotHQ)
        sp.d_setZoneId(ToontownGlobals.CashbotHQ)
        sp.initTasks()
        self.air.suitPlanners[ToontownGlobals.CashbotHQ] = sp
        self.notify.debug('Created new SuitPlanner at %s' % ToontownGlobals.CashbotHQ)

        self.notify.info('Started up')
        