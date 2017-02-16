from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from otp.otpbase import OTPGlobals
import time

class DistributedPolarPlaceEffectMgrAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedPolarPlaceEffectMgrAI")

    def addPolarPlaceEffect(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av: return

        if av.getCheesyEffect()[0] != OTPGlobals.CEBigWhite:
        	expireTime = int(time.time() / 60 + 0.5) + 60
        	av.b_setCheesyEffect(OTPGlobals.CEBigWhite, 3000, expireTime)