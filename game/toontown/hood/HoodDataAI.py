from direct.directnotify import DirectNotifyGlobal
from pandac.PandaModules import *

from toontown.dna.DNASpawnerAI import DNASpawnerAI
from toontown.building import DistributedBuildingMgrAI
from toontown.suit import DistributedSuitPlannerAI
from toontown.safezone import ButterflyGlobals
from toontown.safezone import DistributedButterflyAI
from toontown.safezone import DistributedTrolleyAI
from toontown.toonbase import ToontownGlobals
import ZoneUtil

class HoodDataAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('HoodDataAI')
    numStreets = 3
    
    zoneId = -1
    wantTrolley = True
    spawnSz = True
    butterflyCode = -1
    treasurePlannerClass = None
    classicCharClass = {'noevent': None, 'halloween': None}
    
    def __init__(self, air):
        self.air = air        
        self.startup()
    
    def startup(self):
        self.createBuildingManagers()
        self.createSuitPlanners()
        
        if self.wantTrolley:
            trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
            trolley.generateWithRequired(self.zoneId)
            trolley.start()
            
        if self.butterflyCode != -1:
            self.createButterflies(self.butterflyCode)
            
        if self.treasurePlannerClass:
            self.treasurePlannerClass(self.zoneId).start()
            
        if config.GetBool('want-classic-chars', True):
            self.createClassicChar()
        
        for i in xrange(self.numStreets + 1):
            if i == 0 and not self.spawnSz:
                continue
                
            zoneId = self.zoneId + i * 100
            DNASpawnerAI().spawnObjects(self.air.genDNAFileName(zoneId), zoneId)
        
        self.notify.info('Started up')

    def createBuildingManagers(self):
        for zone in self.air.zoneTable[self.zoneId]:
            if zone[1]:
                zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
                dnaStore = self.air.getStorage(zone[0])
                mgr = DistributedBuildingMgrAI.DistributedBuildingMgrAI(self.air, zoneId, dnaStore, self.air.trophyMgr)
                self.air.buildingManagers[zoneId] = mgr

    def createSuitPlanners(self):
        for zone in self.air.zoneTable[self.zoneId]:
            if zone[2]:
                zoneId = ZoneUtil.getTrueZoneId(zone[0], self.zoneId)
                sp = DistributedSuitPlannerAI.DistributedSuitPlannerAI(self.air, zoneId)
                sp.generateWithRequired(zoneId)
                sp.d_setZoneId(zoneId)
                sp.acceptOnce('startShardActivity', sp.initTasks)
                self.air.suitPlanners[zoneId] = sp

    def createButterflies(self, playground):
        ButterflyGlobals.generateIndexes(self.zoneId, playground)
        for i in xrange(ButterflyGlobals.NUM_BUTTERFLY_AREAS[playground]):
            for j in xrange(ButterflyGlobals.NUM_BUTTERFLIES[playground]):
                bfly = DistributedButterflyAI.DistributedButterflyAI(self.air, playground, i, self.zoneId)
                bfly.generateWithRequired(self.zoneId)
                bfly.start()
                
    def createClassicChar(self):
        dclass = self.classicCharClass.get('noevent')
        if ToontownGlobals.HALLOWEEN_COSTUMES in self.air.holidayManager.currentHolidays:
            dclass = self.classicCharClass.get('halloween', dclass)
            
        if not dclass:
            return
            
        classicChar = dclass(self.air)
        classicChar.generateWithRequired(self.zoneId)
        classicChar.start()
        