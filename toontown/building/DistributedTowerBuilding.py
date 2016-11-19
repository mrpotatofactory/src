from DistributedBuilding import *
from toontown.battle import SuitBattleGlobals

class DistributedTowerBuilding(DistributedBuilding):    
    def getBuildingTitle(self):
        suitName = SuitDNA.suitHeadTypes[self.block]
        return '%s Towers' % SuitBattleGlobals.SuitAttributes[suitName]['pluralname']
