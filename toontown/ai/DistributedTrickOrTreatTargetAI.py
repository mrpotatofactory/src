from direct.directnotify import DirectNotifyGlobal
from toontown.ai.DistributedScavengerHuntTargetAI import DistributedScavengerHuntTargetAI
from toontown.toonbase import ToontownGlobals
from toontown.toon import NPCToons
import time, datetime, random

expire = datetime.date(2014, 11, 4)
unix_time = int(time.mktime(expire.timetuple()) / 60.0)

class DistributedTrickOrTreatTargetAI(DistributedScavengerHuntTargetAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedTrickOrTreatTargetAI")

    def __init__(self, air):
        DistributedScavengerHuntTargetAI.__init__(self, air)
        self.targetZones = [2649, 1834, 5620, 4835, 3707, 9619]
        self.air.huntId = unix_time
        
        for zone in self.targetZones:
            npcIdList = NPCToons.zone2NpcDict.get(zone, [])
            if npcIdList:
                id = npcIdList[0]
                npc = list(NPCToons.NPCToonDict[id])
                npc[-2] = 1
                NPCToons.NPCToonDict[id] = npc
        
    def registerToon(self, avId):
        av = self.air.doId2do.get(avId)
        if not av:
            return
            
        if av.getCheesyEffect()[0] == ToontownGlobals.CEPumpkin:
            return
            
        return av
        
    def attemptScavengerHunt(self):
        avId = self.air.getAvatarIdFromSender()            
        av = self.registerToon(avId)
        if not av:
            return
        
        zoneId = av.zoneId
        if zoneId in self.targetZones:
            if av.addScavengerHuntProgress(zoneId):                
                am = random.randint(30, 150)
                av.addMoney(am)
                self.sendUpdateToAvatarId(avId, 'score', [am])

                if not av.isScavengerHuntComplete(self.targetZones):
                    return
                        
                self.notify.info('%s completed trick or treat!' % avId)
                av.b_setCheesyEffect(ToontownGlobals.CEPumpkin, 0, unix_time)
        