from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedResistanceEmoteMgrAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedResistanceEmoteMgrAI")

    def addResistanceEmote(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av: return

        emotes = av.getEmoteAccess()
        if not emotes[15]: 
            emotes[15] = 1
            av.b_setEmoteAccess(emotes)
