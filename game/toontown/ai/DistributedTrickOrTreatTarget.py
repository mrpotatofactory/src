from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from toontown.effects.ScavengerHuntEffects import TrickOrTreatTargetEffect
from otp.speedchat import SpeedChatGlobals
import DistributedScavengerHuntTarget

class DistributedTrickOrTreatTarget(DistributedScavengerHuntTarget.DistributedScavengerHuntTarget):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedTrickOrTreatTarget')
    neverDisable = 1
    
    def __init__(self, cr):
        DistributedScavengerHuntTarget.DistributedScavengerHuntTarget.__init__(self, cr)

    def score(self, beanAmount):
        TrickOrTreatTargetEffect(beanAmount).play()