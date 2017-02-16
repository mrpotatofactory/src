from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars import DistributedChipAI, DistributedPoliceChipAI
from toontown.classicchars import DistributedDaleAI, DistributedJailbirdDaleAI
from toontown.distributed import DistributedTimerAI
from toontown.safezone import OZTreasurePlannerAI
from toontown.toonbase import ToontownGlobals
import HoodDataAI

class OZHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('OZHoodDataAI')
    numStreets = 0 # 6100 is special, don't use this
     
    zoneId = ToontownGlobals.OutdoorZone
    wantTrolley = False
    treasurePlannerClass = OZTreasurePlannerAI.OZTreasurePlannerAI

    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)

        timer = DistributedTimerAI.DistributedTimerAI(self.air)
        timer.generateWithRequired(self.zoneId)

    def createClassicChar(self):
        if ToontownGlobals.HALLOWEEN_COSTUMES in self.air.holidayManager.currentHolidays:
            classicCharChip = DistributedPoliceChipAI.DistributedPoliceChipAI(self.air)
            classicCharChip.generateWithRequired(self.zoneId)
            classicCharChip.start()
            
            classicCharDale = DistributedJailbirdDaleAI.DistributedJailbirdDaleAI(self.air, classicCharChip.doId)
            classicCharDale.generateWithRequired(self.zoneId)
            classicCharDale.start()
            
            classicCharChip.setDaleId(classicCharDale.doId)
            
        else:
            classicCharChip = DistributedChipAI.DistributedChipAI(self.air)
            classicCharChip.generateWithRequired(self.zoneId)
            classicCharChip.start()
            
            classicCharDale = DistributedDaleAI.DistributedDaleAI(self.air, classicCharChip.doId)
            classicCharDale.generateWithRequired(self.zoneId)
            classicCharDale.start()
            
            classicCharChip.setDaleId(classicCharDale.doId)
            