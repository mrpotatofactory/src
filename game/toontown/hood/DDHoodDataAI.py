from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars import DistributedDonaldDockAI
from toontown.safezone import DDTreasurePlannerAI, DistributedBoatAI
from toontown.toonbase import ToontownGlobals
import HoodDataAI

class DDHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DDHoodDataAI')
    
    zoneId = ToontownGlobals.DonaldsDock
    treasurePlannerClass = DDTreasurePlannerAI.DDTreasurePlannerAI
    classicCharClass = {'noevent': DistributedDonaldDockAI.DistributedDonaldDockAI}

    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)
        boat = DistributedBoatAI.DistributedBoatAI(self.air)
        boat.generateWithRequired(self.zoneId)
        boat.start()