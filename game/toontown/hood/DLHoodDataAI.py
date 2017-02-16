from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars import DistributedDonaldAI, DistributedFrankenDonaldAI
from toontown.safezone import DLTreasurePlannerAI
from toontown.toonbase import ToontownGlobals
import HoodDataAI

class DLHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DLHoodDataAI')
    numStreets = 2
    
    zoneId = ToontownGlobals.DonaldsDreamland
    treasurePlannerClass = DLTreasurePlannerAI.DLTreasurePlannerAI
    classicCharClass = {'noevent': DistributedDonaldAI.DistributedDonaldAI,
                        'halloween': DistributedFrankenDonaldAI.DistributedFrankenDonaldAI}
    