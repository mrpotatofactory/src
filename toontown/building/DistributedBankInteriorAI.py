from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObjectAI
 
class DistributedBankInteriorAI(DistributedObjectAI.DistributedObjectAI):
    
    def __init__(self, block, air, zoneId):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.block = block
        self.zoneId = zoneId

    def generate(self):
        DistributedObjectAI.DistributedObjectAI.generate(self)

    def getZoneIdAndBlock(self):
        r = [ self.zoneId, self.block]
        return r
