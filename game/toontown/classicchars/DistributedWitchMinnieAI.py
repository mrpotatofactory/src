from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars.DistributedMinnieAI import DistributedMinnieAI
from toontown.toonbase import ToontownGlobals

class DistributedWitchMinnieAI(DistributedMinnieAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedWitchMinnieAI")

    def walkSpeed(self):
        return ToontownGlobals.WitchMinnieSpeed