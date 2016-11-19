from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars import DistributedDaisyAI, DistributedSockHopDaisyAI
from toontown.safezone import DGTreasurePlannerAI, DistributedDGFlowerAI, ButterflyGlobals
from toontown.toonbase import ToontownGlobals
import HoodDataAI

class DGHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DGHoodDataAI')
    
    zoneId = ToontownGlobals.DaisyGardens
    treasurePlannerClass = DGTreasurePlannerAI.DGTreasurePlannerAI
    butterflyCode = ButterflyGlobals.DG
    classicCharClass = {'noevent': DistributedDaisyAI.DistributedDaisyAI,
                        'halloween': DistributedSockHopDaisyAI.DistributedSockHopDaisyAI}
    
    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)
        flower = DistributedDGFlowerAI.DistributedDGFlowerAI(self.air)
        flower.generateWithRequired(self.zoneId)
