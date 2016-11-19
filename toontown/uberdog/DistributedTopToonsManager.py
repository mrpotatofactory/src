from direct.distributed.DistributedObject import *
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.distributed.PyDatagram import PyDatagram
import TopToonsGlobals, time

class DistributedTopToonsManager(DistributedObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        
        self.currentSeed = 0
        self.currentChallenge = None
        self.history = []
        self.ranking = []
        self.startTime = 0

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.cr.topToonsMgr = self
        self.sendUpdate('requestData', [])
        
    def setData(self, challengeSeed, ranking, history, startTime):
        self.currentSeed = challengeSeed
        self.currentChallenge = TopToonsGlobals.getChallenge(self.currentSeed)
        self.ranking = ranking
        self.history = history
        self.startTime = startTime
        
        messenger.send('topToonsUpdated')
        
    def notifyWinner(self, name, doId):
        if doId == TopToonsGlobals.DOID_SITE_INFO:
            msg = 'Toon HQ: This month\'s top toons list is now available on the website!'
        
        else:
            try:
                localAvatar
            
            except:
                return
        
            if doId == localAvatar.doId:
                msg = 'Toon HQ: Congratulations, %s! You won the current challenge and %d jellybeans!'
            
            else:
                msg = 'Toon HQ: %s won the current challenge and %d jellybeans!'
            
            msg %= (name, self.currentChallenge.reward)
        
        dg = PyDatagram()
        dg.addString(msg)
        dgi = PyDatagramIterator(dg)
        self.cr.handleSystemMessage(dgi)
        
        taskMgr.doMethodLater(2, self.__doTask, self.taskName('dohptext'), extraArgs=[doId, self.currentChallenge.reward])
        
    def __doTask(self, doId, reward):
        if doId in self.cr.doId2do:
            av = self.cr.doId2do[doId]
            av.showHpText('Challenge won!\n+%d jellybeans!' % reward)
        
    def getElapsedTime(self):
        seconds = time.time()
        
    def delete(self):
        DistributedObject.delete(self)
        del self.cr.topToonsMgr
        