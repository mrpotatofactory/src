from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from toontown.toonbase import ToontownGlobals

class DistributedTrophyMgrAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedTrophyMgrAI")
    
    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.aiLeaderInfo = []
        self.points = ToontownGlobals.TrophyStarLevels
        
    def __sortInfo(self):
        def key(x):
            return -sum(x[2].values())
            
        self.aiLeaderInfo.sort(key=key)
        
    def addTrophy(self, bldg, avId, name, numFloors):
        if numFloors < 1:
            return
            
        index = self.locateAvatar(avId)
        if index != -1:
            self.aiLeaderInfo[index][2][bldg.getBuildingHash()] = numFloors
            
        else:
            d = {bldg.getBuildingHash(): numFloors}
            self.aiLeaderInfo.append([avId, name, d])
        
        self.__sortInfo()
        self.d_setScore(avId, self.getScore(avId))
        
        messenger.send('leaderboardChanged')
        messenger.send('leaderboardFlush')
        
    def removeTrophy(self, bldg, avId):
        # print 'removeTrophy', bldg.getBuildingHash(), avId, self.locateAvatar(avId), self.getScore(avId)
        index = self.locateAvatar(avId)
        if index != -1:
            scoreMap = self.aiLeaderInfo[index][2]
            hash = bldg.getBuildingHash()
            if hash in scoreMap:
                del scoreMap[hash]
                
            self.__sortInfo()
            self.d_setScore(avId, self.getScore(avId))
                        
            messenger.send('leaderboardChanged')
            messenger.send('leaderboardFlush')
            
            if avId in self.air.doId2do:
                self.air.newsManager.sendUpdateToAvatarId(avId, "sendSystemMessage", ["Toon HQ: The COGs have taken over one of the buildings you rescued!", 0])
    
    def d_setScore(self, avId, score):
        av = self.air.doId2do.get(avId)
        if av:
            av.d_setTrophyScore(score)
    
    def getLeaderInfo(self):
        info = [[], [], []]
        for i in xrange(min(len(self.aiLeaderInfo), 10)):
            avId, name, scoreMap = self.aiLeaderInfo[i]
            info[0].append(avId)
            info[1].append(name)
            info[2].append(sum(scoreMap.values()))
            
        return info

    def requestTrophyScore(self):
        avId = self.air.getAvatarIdFromSender()
        self.d_setScore(avId, self.getScore(avId))
        
    def locateAvatar(self, needle):
        for index, (avId, _, _) in enumerate(self.aiLeaderInfo):
            if avId == needle:
                return index
                
        return -1
        
    def getScore(self, avId):
        index = self.locateAvatar(avId)
        if index == -1:
            return 0
            
        return sum(self.aiLeaderInfo[index][2].values())

    def updateToonData(self):
        self.aiLeaderInfo = []
        
        for manager in self.air.buildingManagers.values():
            for block in manager.getBuildings():
                if hasattr(block, 'savedBy') and block.savedBy:
                    for (avId, name, dna) in block.savedBy:
                        self.addTrophy(block, avId, name, block.numFloors)
        
class HackBuilding:
    def getBuildingHash(self):
        return 420 << 16 | 42069
    
from otp.ai.MagicWordGlobal import *
@magicWord(types=[int], accessOther=ACCESS_ADMIN)
def star(score=10):
    av = spellbook.getTarget()
    av.air.trophyMgr.addTrophy(HackBuilding(), av.doId, av.getName(), score)
    