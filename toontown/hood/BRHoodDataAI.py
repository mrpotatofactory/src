from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars import DistributedPlutoAI, DistributedWesternPlutoAI
from toontown.safezone import BRTreasurePlannerAI
from toontown.toonbase import ToontownGlobals
import HoodDataAI

class BRHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('BRHoodDataAI')
    
    zoneId = ToontownGlobals.TheBrrrgh
    treasurePlannerClass = BRTreasurePlannerAI.BRTreasurePlannerAI
    classicCharClass = {'noevent': DistributedPlutoAI.DistributedPlutoAI,
                        'halloween': DistributedWesternPlutoAI.DistributedWesternPlutoAI}
                        