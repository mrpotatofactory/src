from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from direct.interval.IntervalGlobal import *
from toontown.effects import DustCloud
from otp.speedchat import SpeedChatGlobals

def getDustCloudIval(toon):
    dustCloud = DustCloud.DustCloud(fBillboard=0)
    dustCloud.setBillboardAxis(2.0)
    dustCloud.setZ(3)
    dustCloud.setScale(0.4)
    dustCloud.createTrack()
    if getattr(toon, 'laffMeter', None):
        toon.laffMeter.color = toon.style.getBlackColor()
    seq = Sequence(Wait(0.5), Func(dustCloud.reparentTo, toon), dustCloud.track, Func(dustCloud.destroy))
    seq.append(Func(messenger.send, 'blackcat-transformed'))
    if getattr(toon, 'laffMeter', None):
        seq.append(Func(toon.laffMeter.adjustFace, toon.hp, toon.maxHp))
    return seq


class DistributedBlackCatMgr(DistributedObject.DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBlackCatMgr')
    ActivateEvent = 'DistributedBlackCatMgr-activate'

    def announceGenerate(self):
        DistributedBlackCatMgr.notify.debug('announceGenerate')
        DistributedObject.DistributedObject.announceGenerate(self)
        self.dustCloudIval = None
        self.accept(SpeedChatGlobals.SCStaticTextMsgEvent, self.phraseSaid)

    def phraseSaid(self, phraseId):
        self.notify.debug('Checking if phrase was said')
        helpPhrase = 315

        if phraseId == helpPhrase:
            dna = localAvatar.style
            if dna.getAnimal() == 'cat' and dna.headColor != 0x1a:
                self.d_requestBlackCatTransformation()
            
    def delete(self):
        if self.dustCloudIval:
            self.dustCloudIval.finish()
        del self.dustCloudIval
        self.ignore(SpeedChatGlobals.SCStaticTextMsgEvent)
        DistributedObject.DistributedObject.delete(self)

    def d_requestBlackCatTransformation(self):
        self.sendUpdate('requestBlackCatTransformation', [])

    def doBlackCatTransformation(self, avId):
        DistributedBlackCatMgr.notify.debug('doBlackCatTransformation')
        toon = self.cr.doId2do.get(avId)
        if not toon:
            DistributedBlackCatMgr.notify.warning("couldn't find Toon %s" % self.avId)
            return
        if toon.style.getAnimal() != 'cat':
            DistributedBlackCatMgr.notify.warning('not a cat: %s' % self.avId)
            return
        self.dustCloudIval = getDustCloudIval(toon)
        self.dustCloudIval.start()
