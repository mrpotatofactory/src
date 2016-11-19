from direct.distributed.DistributedObjectAI import *
import TopToonsGlobals

class DistributedTopToonsManagerAI(DistributedObjectAI):
    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
                
        self.currentSeed = 0
        self.currentChallenge = None
        self.accept('topToonsManager-UD-newChallenge', self.setData)
        self.accept('topToonsManager-UD-apply-%d' % self.air.ourChannel, self.applyReward)
        
        self.accept('topToonsManager-event', self.__handleEvent)
    
    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        self.air.sendNetEvent('topToonsManager-AI-request')
        
    def setData(self, challengeSeed, ranking, history, startTime):
        self.notify.debug('DistributedTopToonsManagerAI: setData %d' % challengeSeed)
        self.currentSeed = challengeSeed
        self.currentChallenge = TopToonsGlobals.getChallenge(self.currentSeed)
        self.ranking = ranking
        
    def d_score(self, avId, score):
        av = self.air.doId2do.get(avId)
        if not av:
            return
            
        self.air.sendNetEvent('topToonsManager-AI-score', [self.currentSeed, avId, score, av.getName()])
        
    def applyReward(self, avId, amount):
        av = self.air.doId2do.get(avId)
        if not av:
            return
        
        av.addMoney(amount)

    def toonKilledCogs(self, av, suits):
        score = sum(1 for suit in suits if self.currentChallenge.doesCogCount(suit))
        if score:
            self.d_score(av.doId, score)
            
        self.__handleEvent(av.doId, TopToonsGlobals.CAT_COGS, len(suits))
        
    def toonKilledBldg(self, av, track, height):
        bldg = {'track': track, 'height': height}
        if self.currentChallenge.doesBuildingCount(bldg):
            self.d_score(av.doId, 1)
            
        self.__handleEvent(av.doId, TopToonsGlobals.CAT_BLDG, 1)
            
    def toonKilledOffice(self, av, track):
        if self.currentChallenge.doesOfficeCount(track):
            self.d_score(av.doId, 1)
            
        self.__handleEvent(av.doId, TopToonsGlobals.CAT_BLDG, 1)
            
    def toonKilledFactory(self, av, factory):
        if self.currentChallenge.doesFactoryCount(factory):
            self.d_score(av.doId, 1)
            
    def toonKilledBoss(self, av, boss):
        if self.currentChallenge.doesBossCount(boss):
            self.d_score(av.doId, 1)
          
        cat = {'VP': TopToonsGlobals.CAT_VP,
               'CFO': TopToonsGlobals.CAT_CFO,
               'CJ': TopToonsGlobals.CAT_CJ,
               'CEO': TopToonsGlobals.CAT_CEO}.get(boss, 0)
        self.__handleEvent(av.doId, cat, 1)
            
    def __handleEvent(self, *args): # avId, categories, score
        self.air.sendNetEvent('topToonsManager-AI-score-site', list(args))
            
from otp.ai.MagicWordGlobal import *
@magicWord(chains=[CHAIN_HEAD], types=[int])
def chs(score):
    av = spellbook.getTarget()
    mgr = av.air.topToonsMgr
    if not mgr:
        return 'No manager!'
        
    mgr.d_score(av.doId, score)
    
from otp.ai.MagicWordGlobal import *
@magicWord(chains=[CHAIN_HEAD, CHAIN_DISABLED_ON_LIVE], types=[int, int], access=1000)
def topToon(score, cat=TopToonsGlobals._CAT_ALL):
    av = spellbook.getTarget()
    mgr = av.air.topToonsMgr
    if not mgr:
        return 'No manager!'
        
    if cat > TopToonsGlobals._CAT_ALL:
        return 'Max value: %d' % TopToonsGlobals._CAT_ALL
        
    messenger.send('topToonsManager-event', [av.doId, cat, score])
    