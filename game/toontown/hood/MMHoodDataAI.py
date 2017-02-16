from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars import DistributedMinnieAI, DistributedWitchMinnieAI
from toontown.safezone import MMTreasurePlannerAI, DistributedMMPianoAI
from toontown.toonbase import ToontownGlobals
import HoodDataAI

class MMHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('MMHoodDataAI')
    
    zoneId = ToontownGlobals.MinniesMelodyland
    treasurePlannerClass = MMTreasurePlannerAI.MMTreasurePlannerAI
    classicCharClass = {'noevent': DistributedMinnieAI.DistributedMinnieAI,
                        'halloween': DistributedWitchMinnieAI.DistributedWitchMinnieAI}
    
    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)
        piano = DistributedMMPianoAI.DistributedMMPianoAI(self.air)
        piano.generateWithRequired(self.zoneId)
