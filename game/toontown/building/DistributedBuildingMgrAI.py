from direct.directnotify import DirectNotifyGlobal
from toontown.hood import ZoneUtil

import DistributedBuildingAI
import HQBuildingAI
import GagshopBuildingAI
import PetshopBuildingAI
import BankBuildingAI
import LibraryBuildingAI
import KartShopBuildingAI
import DistributedAnimBuildingAI

import cPickle
import time
import random

class DistributedBuildingMgrAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBuildingMgrAI')
    
    def __init__(self, air, branchID, dnaStore, trophyMgr):
        self.branchID = branchID
        self.canonicalBranchID = ZoneUtil.getCanonicalZoneId(branchID)
        self.air = air
        self.__buildings = {}
        self.dnaStore = dnaStore
        self.trophyMgr = trophyMgr
        self.tableName = 'buildings_%s' % self.branchID
        self.findAllLandmarkBuildings()
        self.doLaterTask = None

    def cleanup(self):
        for building in self.__buildings.values():
            building.cleanup()
        
        self.__buildings = {}
    
    def isValidBlockNumber(self, blockNumber):
        return self.__buildings.has_key(blockNumber)
    
    def delayedSaveTask(self, task):
        self.save()
        self.doLaterTask = None
        return Task.done
    
    def isSuitBlock(self, blockNumber):
        return self.__buildings[blockNumber].isSuitBlock()
    
    def getSuitBlocks(self):
        blocks = []
        for i in self.__buildings.values():
            if i.isSuitBlock():
                blocks.append(i.getBlock()[0])
        
        return blocks
    
    def getEstablishedSuitBlocks(self):
        blocks = []
        for i in self.__buildings.values():
            if i.isEstablishedSuitBlock():
                blocks.append(i.getBlock()[0])

        return blocks
    
    def getToonBlocks(self):
        blocks = []
        for i in self.__buildings.values():
            if isinstance(i, HQBuildingAI.HQBuildingAI):
                continue
            
            if not i.isSuitBlock():
                blocks.append(i.getBlock()[0])
                continue
        
        return blocks
    
    def getBuildings(self):
        return self.__buildings.values()

    def getFrontDoorPoint(self, blockNumber):
        return self.__buildings[blockNumber].getFrontDoorPoint()
    
    def getBuildingTrack(self, blockNumber):
        return self.__buildings[blockNumber].track
    
    def getBuilding(self, blockNumber):
        return self.__buildings[blockNumber]
    
    def setFrontDoorPoint(self, blockNumber, point):
        return self.__buildings[blockNumber].setFrontDoorPoint(point)
    
    def getDNABlockLists(self):
        blocks = []
        hqBlocks = []
        gagshopBlocks = []
        petshopBlocks = []
        kartshopBlocks = []
        bankBlocks = []
        libraryBlocks = []
        animBldgBlocks = []
        for i in range(self.dnaStore.getNumBlockNumbers()):
            blockNumber = self.dnaStore.getBlockNumberAt(i)
            buildingType = self.dnaStore.getBlockBuildingType(blockNumber)
            if buildingType == 'hq':
                hqBlocks.append(blockNumber)
                continue
            if buildingType == 'gagshop':
                gagshopBlocks.append(blockNumber)
                continue
            if buildingType == 'petshop':
                petshopBlocks.append(blockNumber)
                continue
            if buildingType == 'kartshop':
                kartshopBlocks.append(blockNumber)
                continue
            if buildingType == 'bank':
                bankBlocks.append(blockNumber)
                continue
            if buildingType == 'library':
                libraryBlocks.append(blockNumber)
                continue
            if buildingType == 'animbldg':
                animBldgBlocks.append(blockNumber)
                continue
            blocks.append(blockNumber)
        return (blocks, hqBlocks, gagshopBlocks, petshopBlocks, kartshopBlocks, bankBlocks, libraryBlocks, animBldgBlocks)
    
    def findAllLandmarkBuildings(self):
        buildings = self.load()
        blocks, hqBlocks, gagshopBlocks, petshopBlocks, kartshopBlocks, bankBlocks, libraryBlocks, animBldgBlocks = self.getDNABlockLists()
        for block in blocks:
            self.newBuilding(block, buildings.get(block, None))
        
        for block in animBldgBlocks:
            self.newAnimBuilding(block, buildings.get(block, None))
        
        for block in hqBlocks:
            self.newHQBuilding(block)
        
        for block in gagshopBlocks:
            self.newGagshopBuilding(block)
 
        if config.GetBool('want-bank-interior', True):
            for block in bankBlocks:
                self.newBankBuilding(block)
 
        if config.GetBool('want-library-interior', True):
            for block in libraryBlocks:
                self.newLibraryBuilding(block)
        
        if simbase.wantPets:
            for block in petshopBlocks:
                self.newPetshopBuilding(block)
                    
        if simbase.wantKarts:
            for block in kartshopBlocks:
                self.newKartShopBuilding(block)

    def newBuilding(self, blockNumber, blockData = None):
        building = DistributedBuildingAI.DistributedBuildingAI(self.air, blockNumber, self.branchID, self.trophyMgr)
        if blockData:
            building.difficulty = int(blockData.get('difficulty', 1))
            building.track = blockData.get('track', 'c')
            building.numFloors = int(blockData.get('numFloors', 1))
            building.numFloors = max(0, min(5, building.numFloors))
            if not ZoneUtil.isWelcomeValley(building.zoneId):
                building.updateSavedBy(blockData.get('savedBy'))
            else:
                self.notify.warning('we had a cog building in welcome valley %d' % building.zoneId)
            building.becameSuitTime = blockData.get('becameSuitTime', time.time())
            building.generateWithRequired(self.branchID)
            if blockData['state'] == 'suit':
                building.setState('suit')
            elif blockData['state'] == 'cogdo':
                building.setState('cogdo')
            else:
                building.setState('toon')
        else:
            building.generateWithRequired(self.branchID)
            building.setState('toon')
        self.__buildings[blockNumber] = building
        return building
    
    def newAnimBuilding(self, blockNumber, blockData = None):
        building = DistributedAnimBuildingAI.DistributedAnimBuildingAI(self.air, blockNumber, self.branchID, self.trophyMgr)
        building.generateWithRequired(self.branchID)
        if blockData:
            building.track = blockData.get('track', 'c')
            building.difficulty = int(blockData.get('difficulty', 1))
            building.numFloors = int(blockData.get('numFloors', 1))
            if not ZoneUtil.isWelcomeValley(building.zoneId):
                building.updateSavedBy(blockData.get('savedBy'))
            else:
                self.notify.warning('we had a cog building in welcome valley %d' % building.zoneId)
            building.becameSuitTime = blockData.get('becameSuitTime', time.time())
            if blockData['state'] == 'suit':
                building.setState('suit')
            else:
                building.setState('toon')
        else:
            building.setState('toon')
        self.__buildings[blockNumber] = building
        return building
    
    def newHQBuilding(self, blockNumber):
        dnaStore = self.air.getStorage(self.canonicalBranchID)
        exteriorZoneId = dnaStore.getZoneFromBlockNumber(blockNumber)
        exteriorZoneId = ZoneUtil.getTrueZoneId(exteriorZoneId, self.branchID)
        interiorZoneId = (self.branchID - self.branchID % 100) + 500 + blockNumber
        building = HQBuildingAI.HQBuildingAI(self.air, exteriorZoneId, interiorZoneId, blockNumber)
        self.__buildings[blockNumber] = building
        return building
    
    def newGagshopBuilding(self, blockNumber):
        dnaStore = self.air.getStorage(self.canonicalBranchID)
        exteriorZoneId = dnaStore.getZoneFromBlockNumber(blockNumber)
        exteriorZoneId = ZoneUtil.getTrueZoneId(exteriorZoneId, self.branchID)
        interiorZoneId = (self.branchID - self.branchID % 100) + 500 + blockNumber
        building = GagshopBuildingAI.GagshopBuildingAI(self.air, exteriorZoneId, interiorZoneId, blockNumber)
        self.__buildings[blockNumber] = building
        return building
    
    def newPetshopBuilding(self, blockNumber):
        dnaStore = self.air.getStorage(self.canonicalBranchID)
        exteriorZoneId = dnaStore.getZoneFromBlockNumber(blockNumber)
        exteriorZoneId = ZoneUtil.getTrueZoneId(exteriorZoneId, self.branchID)
        interiorZoneId = (self.branchID - self.branchID % 100) + 500 + blockNumber
        building = PetshopBuildingAI.PetshopBuildingAI(self.air, exteriorZoneId, interiorZoneId, blockNumber)
        self.__buildings[blockNumber] = building
        return building
    
    def newKartShopBuilding(self, blockNumber):
        dnaStore = self.air.getStorage(self.canonicalBranchID)
        exteriorZoneId = dnaStore.getZoneFromBlockNumber(blockNumber)
        exteriorZoneId = ZoneUtil.getTrueZoneId(exteriorZoneId, self.branchID)
        interiorZoneId = (self.branchID - self.branchID % 100) + 500 + blockNumber
        building = KartShopBuildingAI.KartShopBuildingAI(self.air, exteriorZoneId, interiorZoneId, blockNumber)
        self.__buildings[blockNumber] = building
        return building
    
    def newBankBuilding(self, blockNumber):
        dnaStore = self.air.getStorage(self.canonicalBranchID)
        exteriorZoneId = dnaStore.getZoneFromBlockNumber(blockNumber)
        exteriorZoneId = ZoneUtil.getTrueZoneId(exteriorZoneId, self.branchID)
        interiorZoneId = (self.branchID - self.branchID % 100) + 500 + blockNumber
        building = BankBuildingAI.BankBuildingAI(self.air, exteriorZoneId, interiorZoneId, blockNumber)
        self.__buildings[blockNumber] = building
        return building
    
    def newLibraryBuilding(self, blockNumber):
        dnaStore = self.air.getStorage(self.canonicalBranchID)
        exteriorZoneId = dnaStore.getZoneFromBlockNumber(blockNumber)
        exteriorZoneId = ZoneUtil.getTrueZoneId(exteriorZoneId, self.branchID)
        interiorZoneId = (self.branchID - self.branchID % 100) + 500 + blockNumber
        building = LibraryBuildingAI.LibraryBuildingAI(self.air, exteriorZoneId, interiorZoneId, blockNumber)
        self.__buildings[blockNumber] = building
        return building
        
    def __save_sqlite3(self):
        cursor = self.air.dbCursor
        
        for i in self.__buildings.values():
            if isinstance(i, HQBuildingAI.HQBuildingAI):
                continue
            
            args = [i.fsm.getCurrentState().getName(), i.track, i.difficulty,
                    i.numFloors, cPickle.dumps(i.savedBy), i.becameSuitTime,
                    i.block]
            command = "UPDATE %s SET state=?, track=?, difficulty=?, numFloors=?, savedBy=?, becameSuitTime=? WHERE block=?"
            cursor.execute("SELECT * FROM %s WHERE block=?" % self.tableName, (i.block,))
            if not cursor.fetchone():
                command = "INSERT INTO %s VALUES (?, ?, ?, ?, ?, ?, ?)"
                args.insert(0, args.pop())
                
            command2 = command[:]
            args2 = args[:]
            while '?' in command2:
                pos = command2.find('?')
                command2 = command2[:pos] + str(args2[0]) + command2[pos+1:]
                args2 = args2[1:]
        
            cursor.execute(command % self.tableName, args)
        
        self.air.dbConn.commit()
        
    def __save_mongodb(self):
        cursor = self.air.dbCursor
        collection = cursor['buildings'][self.tableName]
        
        for i in self.__buildings.values():
            if isinstance(i, HQBuildingAI.HQBuildingAI):
                continue
                
            args = {'state': i.fsm.getCurrentState().getName(),
                    'track': i.track,
                    'difficulty': i.difficulty,
                    'numFloors': i.numFloors,
                    'savedBy': cPickle.dumps(i.savedBy),
                    'becameSuitTime': i.becameSuitTime,
                    'block': i.block}
                    
            collection.update({'block': i.block}, {'$set': args}, upsert=True)
            
    def save(self):
        if self.air.dbConnType == 'sqlite3':
            self.__save_sqlite3()
            
        elif self.air.dbConnType == 'mongodb':
            self.__save_mongodb()
        
    def __load_sqlite3(self):
        cursor = self.air.dbCursor
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.tableName,))
        if not cursor.fetchone():
            cursor.execute("CREATE TABLE %s (block INTEGER, state TEXT, track TEXT, difficulty INTEGER, \
                            numFloors INTEGER, savedBy BLOB, becameSuitTime REAL)" % self.tableName)
            self.air.dbConn.commit()
        
        cursor.execute("SELECT * FROM %s" % (self.tableName,))
        data = cursor.fetchall()
        
        res = {}
        
        for block in data:
            blockId, state, track, difficulty, numFloors, savedBy, becameSuitTime = block
            res[blockId] = {'state': str(state), 'track': str(track), 'difficulty': difficulty,
                            'numFloors': numFloors, 'savedBy': cPickle.loads(str(savedBy)),
                            'becameSuitTime': becameSuitTime}
            
        return res

    def __load_mongodb(self):
        cursor = self.air.dbCursor
        collection = cursor['buildings'][self.tableName]
        
        res = {}
        for x in collection.find():
            x['savedBy'] = cPickle.loads(str(x['savedBy']))
            res[x['block']] = x
            
        return res
        
    def load(self):
        if self.air.dbConnType == 'sqlite3':
            data = self.__load_sqlite3()
            
        elif self.air.dbConnType == 'mongodb':
            data = self.__load_mongodb()
        
        if self.canonicalBranchID == 2100:
            if 5 in data:
                data[5]['state'] = 'toon'
            
        return data
        