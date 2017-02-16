from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars import DistributedGoofySpeedwayAI, DistributedSuperGoofyAI
from toontown.toonbase import ToontownGlobals
import HoodDataAI

class GSHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('GSHoodDataAI')
    numStreets = 0
    
    zoneId = ToontownGlobals.GoofySpeedway
    wantTrolley = False
    classicCharClass = {'noevent': DistributedGoofySpeedwayAI.DistributedGoofySpeedwayAI,
                        'halloween': DistributedSuperGoofyAI.DistributedGoofySpeedwayAI}
    
    cycleDuration = 10
    
    def startup(self):
        HoodDataAI.HoodDataAI.startup(self)
        self.__cycleLeaderBoards()
    
    def __cycleLeaderBoards(self, task=None):
        messenger.send('GS_LeaderBoardSwap%d' % self.zoneId)
        taskMgr.doMethodLater(self.cycleDuration, self.__cycleLeaderBoards, 'leaderBoardSwitch')
    