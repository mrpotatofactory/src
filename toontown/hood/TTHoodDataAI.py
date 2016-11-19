from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars import DistributedMickeyAI, DistributedVampireMickeyAI
from toontown.safezone import TTTreasurePlannerAI, ButterflyGlobals
from toontown.toonbase import ToontownGlobals
import HoodDataAI

class TTHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('TTHoodDataAI')
    
    zoneId = ToontownGlobals.ToontownCentral
    treasurePlannerClass = TTTreasurePlannerAI.TTTreasurePlannerAI
    butterflyCode = ButterflyGlobals.TTC
    classicCharClass = {'noevent': DistributedMickeyAI.DistributedMickeyAI,
                        'halloween': DistributedVampireMickeyAI.DistributedVampireMickeyAI}
    