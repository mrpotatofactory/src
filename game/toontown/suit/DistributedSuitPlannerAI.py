from otp.ai.AIBaseGlobal import *
from direct.distributed import DistributedObjectAI
import SuitPlannerBase
import DistributedSuitAI
from toontown.battle import BattleManagerAI
from direct.task import Task
from direct.directnotify import DirectNotifyGlobal
import SuitDNA
from toontown.battle import SuitBattleGlobals
import SuitTimings
from toontown.toon import NPCToons
from toontown.building import HQBuildingAI
from toontown.hood import ZoneUtil
from toontown.building import SuitBuildingGlobals
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals
import math
import time
import random

from SuitLegList import *

def debugs(f):
    def w(*args, **kw):
        fn = f.func_name
        print 'SP.%s called' % fn
        x = f(*args, **kw)
        print 'SP.%s returned %s' % (fn, x)
        return x
    
    return w

NUM_BLDG_TT = .1
NUM_BLDG_DD = .4
NUM_BLDG_DG = .48
NUM_BLDG_MM = .57
NUM_BLDG_BR = .69
NUM_BLDG_DL = .73
NUM_BLDG_FF = .75

ALLOWED_FO_TRACKS = 's'
if config.GetBool('want-lawbot-cogdo', True):
    ALLOWED_FO_TRACKS += 'l'

DEFAULT_COGDO_RATIO = .2

class DistributedSuitPlannerAI(DistributedObjectAI.DistributedObjectAI, SuitPlannerBase.SuitPlannerBase):
    CogdoRatio = min(1.0, max(0.0, config.GetFloat('cogdo-ratio', DEFAULT_COGDO_RATIO)))
    
    # zoneId: (minCogs, maxCogs, bldgRatio, track, levels)
    SuitHoodInfo = {
                    # TT
                    2100: (5, 15, NUM_BLDG_TT, (25, 25, 25, 25), (1, 2, 3)),
                    2200: (3, 10, NUM_BLDG_TT, (10, 70, 10, 10), (1, 2, 3)),
                    2300: (3, 10, NUM_BLDG_TT, (10, 10, 40, 40), (1, 2, 3)),
                    
                    # DD
                    1100: (1, 5, NUM_BLDG_DD, (90, 10, 0, 0), (2, 3, 4)),
                    1200: (1, 5, NUM_BLDG_DD, (0, 0, 90, 10), (3, 4, 5, 6)),
                    1300: (1, 5, NUM_BLDG_DD, (40, 40, 10, 10), (3, 4, 5, 6)),
                    
                    # BR
                    3100: (1, 5, NUM_BLDG_BR, (90, 10, 0, 0), (5, 6, 7)),
                    3200: (1, 5, NUM_BLDG_BR, (10, 20, 30, 40), (5, 6, 7)),
                    3300: (1, 5, NUM_BLDG_DL, (5, 85, 5, 5), (7, 8, 9)),
                    
                    # MM
                    4100: (1, 5, NUM_BLDG_MM, (0, 0, 50, 50), (2, 3, 4)),
                    4200: (1, 5, NUM_BLDG_MM, (0, 0, 90, 10), (3, 4, 5, 6)),
                    4300: (1, 5, NUM_BLDG_MM, (50, 50, 0, 0), (3, 4, 5, 6)),
                    
                    # DG
                    5100: (1, 5, NUM_BLDG_DG, (0,20,10, 70), (2, 3, 4)),
                    5200: (1, 5, NUM_BLDG_DG, (10, 70,0,20), (3, 4, 5, 6)),
                    5300: (1, 5, NUM_BLDG_DG, (5, 5, 5, 85), (3, 4, 5, 6)),
                    
                    # DL
                    9100: (1, 5, NUM_BLDG_DL, (25, 25, 25, 25), (6, 7, 8, 9)),
                    9200: (1, 5, NUM_BLDG_DL, (5, 5, 85, 5), (6, 7, 8, 9)),
                    
                    # HQs
                    11000: (3, 15, 0, (0, 0, 0, 100), (4, 5, 6)),
                    11200: (10, 20, 0, (0, 0, 0, 100), (4, 5, 6)),
                    12000: (10, 20, 0, (0, 0, 100, 0), (7, 8, 9)),
                    13000: (10, 20, 0, (0, 100, 0, 0), (8, 9, 10)),
                    
                    # FF
                    7100: (3, 9, NUM_BLDG_FF, (25, 25, 25, 25), range(1, 11))
                  }
                   
    SUIT_HOOD_INFO_MIN = 0
    SUIT_HOOD_INFO_MAX = 1
    SUIT_HOOD_INFO_BRATIO = 2
    SUIT_HOOD_INFO_TRACK = 3
    SUIT_HOOD_INFO_LVL = 4
    
    MAX_SUIT_TYPES = 6
    POP_UPKEEP_DELAY = 10
    PATH_COLLISION_BUFFER = 5
    
    MIN_PATH_LEN = 40
    MAX_PATH_LEN = 300
    MIN_TAKEOVER_PATH_LEN = 2
    
    SUITS_ENTER_BUILDINGS = config.GetBool('want-suit-buildings', 1)
    JOIN_CHANCES = (1, 5, 10, 40, 60, 80)
    
    defaultSuitName = config.GetString('suit-type', 'random')
    if defaultSuitName == 'random':
        defaultSuitName = None
    
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSuitPlannerAI')
    
    def __init__(self, air, zoneId):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        SuitPlannerBase.SuitPlannerBase.__init__(self)
        self.zoneId = zoneId
        self.canonicalZoneId = ZoneUtil.getCanonicalZoneId(zoneId)

        self.suitInfo = DistributedSuitPlannerAI.SuitHoodInfo[self.zoneId][:]
        
        if ZoneUtil.isWelcomeValley(self.zoneId):
            self.suitInfo[self.SUIT_HOOD_INFO_BRATIO] = 0

        self.suitList = []
        self.zoneInfo = {}
        self.zoneIdToPointMap = None
        self.cogHQDoors = []
        
        self.numAttemptingTakeover = 0
        self.bldgCount = 0
        
        self.battleList = []
        self.battleMgr = BattleManagerAI.BattleManagerAI(self.air)
        self.setupDNA()
        
        self.buildingMgr = self.air.buildingManagers.get(self.zoneId)
        if self.buildingMgr:
            blocks, hqBlocks, gagshopBlocks, petshopBlocks, kartshopBlocks, bankBlocks, libraryBlocks, animBldgBlocks = self.buildingMgr.getDNABlockLists()
            
            for currBlock in blocks:
                bldg = self.buildingMgr.getBuilding(currBlock)
                bldg.setSuitPlannerExt(self)
            
            for currBlock in animBldgBlocks:
                bldg = self.buildingMgr.getBuilding(currBlock)
                bldg.setSuitPlannerExt(self)
                                
        else:
            self.notify.debug('No building manager at %s' % self.zoneId)
        
        self.dnaStore.resetBlockNumbers()
        self.initBuildingsAndPoints()

    def isBlockSuitTarget(self, block):
        for suit in self.suitList:
            if suit.buildingDestination == block:
                return 1
                
        return 0
    
    def cleanup(self):
        taskMgr.remove(self.taskName('sptUpkeepPopulation'))
        for suit in self.suitList:
            suit.stopTasks()
            if suit.isGenerated():
                self.zoneChange(suit, suit.zoneId)
                suit.requestDelete()
        
        self.suitList = []
    
    def delete(self):
        self.cleanup()
        DistributedObjectAI.DistributedObjectAI.delete(self)
    
    def initBuildingsAndPoints(self):
        if not self.buildingMgr:
            return None

        self.buildingFrontDoors = {}
        self.buildingSideDoors = {}
        
        for p in self.frontdoorPointList:
            blockNumber = p.getLandmarkBuildingIndex()
            if blockNumber < 0:
                self.notify.debug('No landmark building for point %d in zone %d' % (p.getIndex(), self.zoneId))
                continue
                
            if blockNumber in self.buildingFrontDoors:
                self.notify.debug('Multiple front doors for building %d in zone %d' % (blockNumber, self.zoneId))
                continue
                
            self.buildingFrontDoors[blockNumber] = p
        
        for p in self.sidedoorPointList:
            blockNumber = p.getLandmarkBuildingIndex()
            if blockNumber < 0:
                self.notify.debug('No landmark building for point %d in zone %d' % (p.getIndex(), self.zoneId))
                continue
                
            self.buildingSideDoors.setdefault(blockNumber, []).append(p)
        
        for bldg in self.buildingMgr.getBuildings():
            if isinstance(bldg, HQBuildingAI.HQBuildingAI):
                continue
            
            blockNumber = bldg.getBlock()[0]
            if blockNumber not in self.buildingFrontDoors:
                self.notify.debug('No front door for building %d in zone %d' % (blockNumber, self.zoneId))
            
            if blockNumber not in self.buildingSideDoors:
                self.notify.debug('No side door for building %d in zone %d' % (blockNumber, self.zoneId))
                
            extZoneId, intZoneId = bldg.getExteriorAndInteriorZoneId()
            if not NPCToons.isZoneProtected(intZoneId):
                self.bldgCount += 1
    
    def countNumBuildingsPerTrack(self):
        count = {dept: 0 for dept in SuitDNA.suitDepts}
        if self.buildingMgr:
            for building in self.buildingMgr.getBuildings():
                if building.isSuitBuilding():
                    count[building.track] += 1
                        
        return count

    def calcDesiredNumBuildings(self):        
        return int(self.suitInfo[self.SUIT_HOOD_INFO_BRATIO] * self.bldgCount)

    def getZoneIdToPointMap(self):
        if self.zoneIdToPointMap != None:
            return self.zoneIdToPointMap
        
        self.zoneIdToPointMap = {}
        for point in self.streetPointList:
            points = self.dnaStore.getAdjacentPoints(point)
            for i in xrange(points.getNumPoints() - 1):
                pi = points.getPointIndex(i)
                p = self.pointIndexes[pi]
                zoneId = self.dnaStore.getSuitEdgeZone(point.getIndex(), p.getIndex())
                self.zoneIdToPointMap.setdefault(zoneId, []).append(point)
        
        return self.zoneIdToPointMap
    
    def getStreetPointsForBuilding(self, blockNumber):
        pointList = []
        if blockNumber in self.buildingSideDoors:
            for doorPoint in self.buildingSideDoors[blockNumber]:
                points = self.dnaStore.getAdjacentPoints(doorPoint)
                for i in xrange(points.getNumPoints() - 1):
                    pi = points.getPointIndex(i)
                    point = self.pointIndexes[pi]
                    if point.getPointType() == DNASuitPoint.STREETPOINT:
                        pointList.append(point)
            
        
        if blockNumber in self.buildingFrontDoors:
            doorPoint = self.buildingFrontDoors[blockNumber]
            points = self.dnaStore.getAdjacentPoints(doorPoint)
            for i in xrange(points.getNumPoints() - 1):
                pi = points.getPointIndex(i)
                pointList.append(self.pointIndexes[pi])
        
        return pointList

    def createNewSuit(self, blockNumbers, streetPoints, suitName=None, skelecog=False, v2=False):
        startPoint = None
        blockNumber = None
        
        origin = random.choice(('sky', 'building'))
        if origin == 'building':
            random.shuffle(blockNumbers)
            
            while startPoint is None and len(blockNumbers) > 0:
                bn = blockNumbers.pop()
                if bn in self.buildingSideDoors:
                    for doorPoint in self.buildingSideDoors[bn]:
                        points = self.dnaStore.getAdjacentPoints(doorPoint)
                    
                        i = points.getNumPoints() - 1
                        while blockNumber is None and i >= 0:
                            pi = points.getPointIndex(i)
                            p = self.pointIndexes[pi]
                            i -= 1
                            startTime = SuitTimings.fromSuitBuilding
                            startTime += self.dnaStore.getSuitEdgeTravelTime(doorPoint.getIndex(), pi, self.suitWalkSpeed)
                            if not self.pointCollision(p, doorPoint, startTime):
                                startTime = SuitTimings.fromSuitBuilding
                                startPoint = doorPoint
                                blockNumber = bn
                                break
                
        while startPoint is None and len(streetPoints) > 0:
            p = random.choice(streetPoints)
            streetPoints.remove(p)
            if not self.pointCollision(p, None, SuitTimings.fromSky):
                startPoint = p
                startTime = SuitTimings.fromSky
                break
                
        if startPoint is None:
            return
        
        newSuit = DistributedSuitAI.DistributedSuitAI(self.air, self)
        newSuit.startPoint = startPoint
        if blockNumber != None:
            newSuit.buildingSuit = 1
            suitTrack = self.buildingMgr.getBuildingTrack(blockNumber)
            if suitTrack == "x":
               suitTrack = random.choice("cmls")
            
        else:
            newSuit.flyInSuit = 1
            newSuit.attemptingTakeover = self.newSuitShouldAttemptTakeover()
        
        dept = None
        if suitName is None:
            suitName, skelecog, v2, dept = self.air.suitInvasionManager.getInvadingCog()
            if suitName is None:
                suitName = self.defaultSuitName
        
        if suitName is not None:
            suitType = SuitDNA.getSuitType(suitName)
            suitTrack = SuitDNA.getSuitDept(suitName)
            
        else:
            suitType = None
            suitTrack = dept
        
        suitLevel, suitType, suitTrack = self.pickLevelTypeAndTrack(None, suitType, suitTrack)
        newSuit.setupSuitDNA(suitLevel, suitType, suitTrack)
        newSuit.buildingHeight = self.generateHeight(suitLevel)

        gotDestination = self.chooseDestination(newSuit, startTime)
        if not gotDestination:
            self.notify.debug("Couldn't get a destination in %d!" % self.zoneId)
            newSuit.doNotDeallocateChannel = None
            newSuit.delete()
            return

        newSuit.initializePath()
        self.zoneChange(newSuit, None, newSuit.zoneId)
        if skelecog:
            newSuit.setSkelecog(skelecog)
            
        if v2:
            newSuit.setSkeleRevives(1)
        
        newSuit.generateWithRequired(newSuit.zoneId)
        newSuit.moveToNextLeg(None)
        self.suitList.append(newSuit)
        
        if newSuit.attemptingTakeover:
            self.numAttemptingTakeover += 1
        
        return newSuit
       
    def newSuitShouldAttemptTakeover(self):
        if not self.SUITS_ENTER_BUILDINGS:
            return 0

        desired = self.calcDesiredNumBuildings()
        commited = self.numAttemptingTakeover
        
        if self.buildingMgr:
            commited += len(self.buildingMgr.getSuitBlocks())

        if commited >= desired:
            return 0
        
        self.notify.debug('DSP %d is planning a takeover attempt in zone %d' % (self.getDoId(), self.zoneId))
        return 1

    def chooseDestination(self, suit, startTime):
        possibles = []
        backup = []
        
        cogdoTakeover = False

        if suit.attemptingTakeover:
            for blockNumber in self.buildingMgr.getToonBlocks():
                building = self.buildingMgr.getBuilding(blockNumber)
                extZoneId, intZoneId = building.getExteriorAndInteriorZoneId()
                if not NPCToons.isZoneProtected(intZoneId):
                    if blockNumber in self.buildingFrontDoors:
                        if not self.isBlockSuitTarget(blockNumber):
                            # HACK: Forbid Animated Sign Factory
                            if self.zoneId != 2100 or blockNumber != 5:
                                possibles.append((blockNumber, self.buildingFrontDoors[blockNumber]))
                                
            if suit.dna.dept in ALLOWED_FO_TRACKS:
                cogdoTakeover = random.random() < self.CogdoRatio
                
        elif self.buildingMgr:
            for blockNumber in self.buildingMgr.getSuitBlocks():
                track = self.buildingMgr.getBuildingTrack(blockNumber)
                if track == suit.track and blockNumber in self.buildingSideDoors:
                    for doorPoint in self.buildingSideDoors[blockNumber]:
                        possibles.append((blockNumber, doorPoint))
 
        backup = []
        for p in self.streetPointList:
            backup.append((None, p))
        
        if len(possibles) == 0:
            possibles = backup
            backup = []
       
        maxPathLen = self.MAX_PATH_LEN       
        if suit.attemptingTakeover:
            minPathLen = self.MIN_TAKEOVER_PATH_LEN
        else:
            minPathLen = self.MIN_PATH_LEN
        
        retryCount = 0
        while len(possibles) > 0 and retryCount < 50:
            p = random.choice(possibles)
            possibles.remove(p)
            if len(possibles) == 0:
                possibles = backup
                backup = []
            
            try:
                path = self.genPath(suit.startPoint, p[1], minPathLen, maxPathLen)
                
            except Exception as e:
                print self.zoneId, e
                exit()
            
            if path and not self.pathCollision(path, startTime):                   
                suit.endPoint = p[1]
                suit.minPathLen = minPathLen
                suit.maxPathLen = maxPathLen
                suit.buildingDestination = p[0]
                
                #if self.zoneId == 3300:
                #    if p[1].getPointType() == DNASuitPoint.FRONTDOORPOINT:
                #        print 'DSP assigned %r buildingDestination to %s/%s (%s)' % (suit, p[0], p[1].getIndex(), p[1].getPointType())
                    
                suit.buildingDestinationIsCogdo = cogdoTakeover
                suit.setPath(path)
                return 1
            
            retryCount += 1
            
        return 0

    def pathCollision(self, path, elapsedTime):
        pathLength = path.getNumPoints()
        i = 0
        pi = path.getPointIndex(i)
        point = self.pointIndexes[pi]
        adjacentPoint = self.pointIndexes[path.getPointIndex(i + 1)]
        while point.getPointType() in (DNASuitPoint.SIDEDOORPOINT, DNASuitPoint.FRONTDOORPOINT):
            i += 1
            lastPi = pi
            pi = path.getPointIndex(i)
            adjacentPoint = point
            point = self.pointIndexes[pi]
            elapsedTime += self.dnaStore.getSuitEdgeTravelTime(lastPi, pi, self.suitWalkSpeed)
        result = self.pointCollision(point, adjacentPoint, elapsedTime)
        return result

    def pointCollision(self, point, adjacentPoint, elapsedTime):
        for suit in self.suitList:
            if suit.pointInMyPath(point, elapsedTime):
                return 1
        
        if adjacentPoint != None:
            return self.battleCollision(point, adjacentPoint)
            
        else:
            points = self.dnaStore.getAdjacentPoints(point)
            for i in xrange(points.getNumPoints() - 1):
                pi = points.getPointIndex(i)
                p = self.pointIndexes[pi]
                if self.battleCollision(point, p):
                    return 1

        return 0
    
    def battleCollision(self, point, adjacentPoint):
        zoneId = self.dnaStore.getSuitEdgeZone(point.getIndex(), adjacentPoint.getIndex())
        return self.battleMgr.cellHasBattle(zoneId)
    
    def removeSuit(self, suit):
        self.zoneChange(suit, suit.zoneId)
        if suit in self.suitList:
            self.suitList.remove(suit)
            
            if suit.attemptingTakeover:
                self.numAttemptingTakeover -= 1
               
        suit.requestDelete()
        
    def __waitForNextUpkeep(self):
        t = (random.random() * 2.0 + self.POP_UPKEEP_DELAY)
        taskMgr.doMethodLater(t, self.upkeepSuitPopulation, self.taskName('sptUpkeepPopulation'))
    
    def upkeepSuitPopulation(self, task):
        if self.buildingMgr:
            suitBuildings = self.buildingMgr.getEstablishedSuitBlocks()
            
        else:
            suitBuildings = []
            
        desiredSuits = random.randint(self.suitInfo[self.SUIT_HOOD_INFO_MIN], self.suitInfo[self.SUIT_HOOD_INFO_MAX])
        suitDeficit = min(4, desiredSuits - len(self.suitList))
            
        while suitDeficit > 0:
            if not self.createNewSuit(suitBuildings, self.streetPointList[:]):
                break
                
            suitDeficit -= 1
 
        self.__waitForNextUpkeep()
        return Task.done
    
    def suitTakeOver(self, blockNumber, suitTrack, difficulty, buildingHeight):        
        building = self.buildingMgr.getBuilding(blockNumber)
        building.suitTakeOver(suitTrack, difficulty, buildingHeight)
    
    def cogdoTakeOver(self, blockNumber, difficulty, buildingHeight, dept):        
        building = self.buildingMgr.getBuilding(blockNumber)
        building.cogdoTakeOver(difficulty, buildingHeight, dept)
    
    def recycleBuilding(self):
        return
    
    def chooseSuitLevel(self, possibleLevels, buildingHeight=None):        
        return random.choice(choices)
    
    def initTasks(self):            
        self.__waitForNextUpkeep()

    def resyncSuits(self):
        for suit in self.suitList:
            suit.resync()
    
    def flySuits(self):
        for suit in self.suitList:
            if suit.pathState == 1:
                suit.flyAwayNow()
            
    def requestBattle(self, zoneId, suit, toonId):
        self.notify.debug('requestBattle() - zone: %d suit: %d toon: %d' % (zoneId, suit.doId, toonId))
        canonicalZoneId = ZoneUtil.getCanonicalZoneId(zoneId)
        if canonicalZoneId not in self.battlePosDict:
            return 0
        
        toon = self.air.doId2do.get(toonId)
        if toon.getBattleId() > 0:
            self.notify.warning('We tried to request a battle when the toon was already in battle')
            return 0
        
        if toon:
            if hasattr(toon, 'doId'):
                toon.b_setBattleId(toonId)
        
        pos = self.battlePosDict[canonicalZoneId]
        interactivePropTrackBonus = -1
        if config.GetBool('props-buff-battles', True) and canonicalZoneId in self.cellToGagBonusDict:
            tentativeBonusTrack = self.cellToGagBonusDict[canonicalZoneId]
            trackToHolidayDict = {
                ToontownBattleGlobals.SQUIRT_TRACK: ToontownGlobals.HYDRANTS_BUFF_BATTLES,
                ToontownBattleGlobals.THROW_TRACK: ToontownGlobals.MAILBOXES_BUFF_BATTLES,
                ToontownBattleGlobals.HEAL_TRACK: ToontownGlobals.TRASHCANS_BUFF_BATTLES }
                
            if tentativeBonusTrack in trackToHolidayDict:
                holidayId = trackToHolidayDict[tentativeBonusTrack]
                if self.air.holidayManager.isHolidayRunning(holidayId):
                    interactivePropTrackBonus = tentativeBonusTrack
        
        self.battleMgr.newBattle(zoneId, zoneId, pos, suit, toonId,
                                 self.__battleFinished, 4,
                                 interactivePropTrackBonus)
                                 
        for currOther in self.zoneInfo[zoneId]:
            self.notify.debug('Found suit %d in this new battle zone %d' % (currOther.getDoId(), zoneId))
            if currOther != suit:
                if currOther.pathState == 1 and currOther.legType == SuitLeg.TWalk:
                    self.checkForBattle(zoneId, currOther)
        
        return 1

    def __battleFinished(self, zoneId):
        self.notify.debug('battle in zone %s finished' % zoneId)
        for battle in self.battleList[:]:
            if battle[0] == zoneId:
                self.notify.debug('battle removed')
                self.battleList.remove(currBattle)

    def __suitCanJoinBattle(self, zoneId):
        battle = self.battleMgr.getBattle(zoneId)
        if len(battle.suits) >= 4:
            return 0
        
        if battle:
            if config.GetBool('suits-always-join', 0):
                return 1
            
            ratioIdx = (len(battle.toons) - battle.numSuitsEver) + 2
            if ratioIdx >= 0:
                if ratioIdx < len(self.JOIN_CHANCES):
                    if random.randint(0, 99) < self.JOIN_CHANCES[ratioIdx]:
                        return 1
                    
                else:
                    self.notify.warning('__suitCanJoinBattle idx out of range!')
                    return 1
                    
        return 0
    
    def checkForBattle(self, zoneId, suit):
        if self.battleMgr.cellHasBattle(zoneId):
            if not (self.__suitCanJoinBattle(zoneId) and self.battleMgr.requestBattleAddSuit(zoneId, suit)):
                suit.flyAwayNow()
                return 1
        
        return 0
      
    def zoneChange(self, suit, oldZone, newZone=None):
        if oldZone in self.zoneInfo and suit in self.zoneInfo[oldZone]:
            self.zoneInfo[oldZone].remove(suit)
        
        if newZone != None:            
            self.zoneInfo.setdefault(newZone, []).append(suit)
    
    def d_setZoneId(self, zoneId):
        self.sendUpdate('setZoneId', [self.zoneId])

    def suitListQuery(self):
        suitIndexList = []
        for suit in self.suitList:
            suitIndexList.append(SuitDNA.suitHeadTypes.index(suit.dna.name))
        
        self.sendUpdateToAvatarId(self.air.getAvatarIdFromSender(), 'suitListResponse', [suitIndexList])
    
    def buildingListQuery(self):
        buildingDict = self.countNumBuildingsPerTrack()
        buildingList = [0, 0, 0, 0]
        for dept in SuitDNA.suitDepts:
            if dept in buildingDict:
                buildingList[SuitDNA.suitDepts.index(dept)] = buildingDict[dept]
        
        self.sendUpdateToAvatarId(self.air.getAvatarIdFromSender(), 'buildingListResponse', [buildingList])
    
    def pickLevelTypeAndTrack(self, level=None, type=None, track=None):
        if level is None:
            level = random.choice(self.suitInfo[self.SUIT_HOOD_INFO_LVL])
        
        if type is None:
            typeChoices = range(max(level - 4, 1), min(level, self.MAX_SUIT_TYPES) + 1)
            type = random.choice(typeChoices)
            
        else:
            level = min(max(level, type), type + 4)
            
        if track is None:
            track = SuitDNA.suitDepts[SuitBattleGlobals.pickFromFreqList(self.suitInfo[self.SUIT_HOOD_INFO_TRACK])]
        
        self.notify.debug('pickLevelTypeAndTrack: %d %d %s' % (level, type, track))
        return level, type, track

    def generateHeight(self, level):
        return random.choice(SuitBuildingGlobals.SuitBuildingInfo[level - 1][0])
        
from otp.ai.MagicWordGlobal import *
@magicWord(types=[int, str, int])
def suitfrom(blockNumber, name=None, skel=0):
    av = spellbook.getTarget()
    air = av.air
    zoneId = av.zoneId
    zoneId = zoneId - zoneId % 100
    return repr(air.suitPlanners[zoneId].createNewSuit([blockNumber], [], suitName=name, skelecog=skel))
 
@magicWord()
def rcb(): # recover closest building
    av = spellbook.getTarget()
    air = av.air
    
    zoneId = av.zoneId
    streetId = ZoneUtil.getBranchZone(zoneId)
    sp = air.suitPlanners.get(streetId)
    if not sp:
       return 'not found'
       
    bm = sp.buildingMgr
    if not bm:
        return 'not found'
        
    zones = [zoneId, zoneId - 1, zoneId + 1, zoneId - 2, zoneId + 2]
    for zone in zones:
        for i in bm.getSuitBlocks():
            building = bm.getBuilding(i)
            if building.getExteriorAndInteriorZoneId()[0] == zone:
                if hasattr(building, 'elevator'):
                    if building.fsm.getCurrentState().getName() in ('suit', 'cogdo'):
                        if building.elevator.fsm.getCurrentState().getName() == 'waitEmpty':
                            if building.fsm.getCurrentState().getName() == 'suit':
                                building.setState('becomingToon')
                            else:
                                building.setState('becomingToonFromCogdo')
                            return building.getBlock()
                        
    return 'not found'
    
@magicWord(types=[str, int]) 
def summoncogdo(track="s", difficulty=5):
    tracks = ['s']
    if config.GetBool('want-lawbot-cogdo', True):
        tracks.append('l')
    if track not in tracks:
        return "Invalid track!"
        
    av = spellbook.getInvoker()
    building = av.findClosestDoor()
    if building == None:
        return "No bldg found!"
        
    building.cogdoTakeOver(difficulty, 2, track)
    
