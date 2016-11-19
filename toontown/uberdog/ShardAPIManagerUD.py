from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject
from direct.distributed.PyDatagramIterator import *
from direct.distributed.PyDatagram import *

from toontown.toonbase import ToontownGlobals
from toontown.suit import SuitDNA

import time

blockNames = {}
cogNames = {}
langAliasMap = {'English': 'en', '_portuguese': 'pt', '_leet': 'l3', '_yolo': 'ys'}

def __extractCogNames(m):
    y = ['MrHollywood', 'TheMingler', 'TwoFace', 'MoverShaker', 'GladHander', 'NameDropper', 'Telemarketer', 'ColdCaller',
         'RobberBaron', 'LoanShark', 'MoneyBags', 'NumberCruncher', 'BeanCounter', 'Tightwad', 'PennyPincher', 'ShortChange',
         'BigWig', 'LegalEagle', 'SpinDoctor', 'BackStabber', 'AmbulanceChaser', 'DoubleTalker', 'Bloodsucker', 'BottomFeeder',
         'TheBigCheese', 'CorporateRaider', 'HeadHunter', 'Downsizer', 'Micromanager', 'Yesman', 'PencilPusher', 'Flunky']
         
    res = {}    
    for x in SuitDNA.suitHeadTypes:
        c = y.pop()
        res[x] = (getattr(m, 'Suit%s' % c), getattr(m, 'Suit%sS' % c), getattr(m, 'Suit%sP' % c))
        
    return res

languages = config.GetString('shard-api-block-languages', 'English _portuguese _leet _yolo').split()
for lang in languages:
    m = __import__('toontown.toonbase.TTLocalizer%s' % lang, {}, {}, ['toontown.toonbase'])
    
    zoneDict = m.zone2TitleDict.copy()
    blockNames[langAliasMap[lang]] = zoneDict
    cogNames[langAliasMap[lang]] = __extractCogNames(m)
    
    del m

CURRENT_LANG_CONTEXT = 'en'

def setLanguageContext(lang):
    global CURRENT_LANG_CONTEXT
    
    if lang is None:
        CURRENT_LANG_CONTEXT = 'en'
        return True
        
    if not lang in blockNames:
        return False
        
    CURRENT_LANG_CONTEXT = lang
    return True
    
class Block:
    def __init__(self, number, branchZone):
        self.number = number
        self.branchZone = branchZone
     
        self.setToToon(None)
        
    def setToToon(self, args):
        self.type = 'toon'
        self.track = ''
        self.height = 0
        self.difficulty = -1
        
    def setToSuit(self, args):
        self.type = 'suit'
        self.track = args['track']
        self.height = args['height']
        self.difficulty = args['difficulty']
        
    def setToCogdo(self, args):
        self.setToSuit(args)
        self.type = 'cogdo'
        
    def update(self, mode, args):
        if mode == 'toon':
            self.setToToon(args)
            
        if mode == 'suit':
            self.setToSuit(args)
            
        if mode == 'cogdo':
            self.setToCogdo(args)
        
    def writeDict(self):
        return {'title': self.getName(), 'type': self.type, 'track': self.track,
                'height': self.height, 'difficulty': self.difficulty}
                                                                                                     
    def getName(self):
        zoneId = self.number + self.branchZone + 500
        return blockNames[CURRENT_LANG_CONTEXT].get(zoneId, ['???', ''])[0]
        
class StreetHandle:
    def __init__(self, hood, streetId):
        self.hood = hood
        self.streetId = streetId
        self.dnaStore = self.hood.shard.mgr.air.getDnaStore(self.streetId)
        self.blocks = {}

        for i in xrange(self.dnaStore.getNumBlockNumbers()):
            blockNumber = self.dnaStore.getBlockNumberAt(i)
            buildingType = self.dnaStore.getBlockBuildingType(blockNumber)
            
            if buildingType != 'hq':
                self.blocks[blockNumber] = Block(blockNumber, self.streetId)
                        
class HoodHandle:
    def __init__(self, shard, hoodId, numStreets):
        self.shard = shard
        self.hoodId = hoodId
        self.streets = {}
        
        for i in xrange(numStreets):
            z = self.hoodId + (i + 1) * 100
            self.streets[z] = StreetHandle(self, z)

class ShardHandle:
    def __init__(self, mgr, name):
        self.mgr = mgr
        self.name = name
        self.hoods = {}
        
        self.duration = 0
        self.start = 0
        self.cogName = ''
        self.skel = 0
        self.numCogs = 0
        
        self.addHood(ToontownGlobals.ToontownCentral)
        self.addHood(ToontownGlobals.DonaldsDock)
        self.addHood(ToontownGlobals.DaisyGardens)
        self.addHood(ToontownGlobals.MinniesMelodyland)
        self.addHood(ToontownGlobals.TheBrrrgh)
        self.addHood(ToontownGlobals.DonaldsDreamland, 2)
        
    def addHood(self, hoodId, numStreets=3):
        self.hoods[hoodId] = HoodHandle(self, hoodId, numStreets)
        
    def writeDict(self):
        d = {}
        for i, hood in self.hoods.items():
            d[i] = hood.writeDict()
            
        return {'hoods': d}
        
    def updateInvasion(self, name, skel, start, duration, numCogs, v2, dept):
        self.cogName = name
        self.skel = skel
        self.start = start
        self.duration = duration
        self.numCogs = numCogs
        self.v2 = v2
        self.dept = dept
        
    def readInvasion(self):
        r = 0
        if self.duration != 0:
            elapsed = int(int(time.time()) - self.start)
            r = self.duration - elapsed
            
        cogFullName = cogNames[CURRENT_LANG_CONTEXT].get(self.cogName, ('', '', ''))
        
        return {'duration': self.duration, 'remaining': r, 'cogName': self.cogName,
                'skel': bool(self.skel), 'districtName': self.name, 'numCogs': self.numCogs,
                'cogFullName': cogFullName, 'v2': bool(self.v2), 'dept': self.dept}

class ShardAPIManagerUD(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('ShardAPIManagerUD')
    
    def __init__(self, air):
        self.air = air
        self.shards = {}
        
        self.accept('invasionEvent', self.__handleInvasionEvent)
        self.accept('buildingEvent', self.__handleBuildingEvent)
        self.accept('shardDied', self.__killShard)
        
        self.accept('API_setShardData', self.setShardData)
        
    def newShard(self, districtName='unknown'):
        shardId = self.air.getMsgSender() + 1
        
        self.shards[shardId] = ShardHandle(self, districtName)
        
    def _doUpdateShard(self, dgi):
        shardId = self.air.getMsgSender() + 1
        shard = self.shards[shardId]
            
        updateType = dgi.getString()
            
        if updateType == 'block':
            hoodId = dgi.getUint16()
            streetId = dgi.getUint16()
            blockNumber = dgi.getUint8()
            
            args = {}
            type = dgi.getString()
            
            args['track'] = chr(dgi.getUint8())
            args['difficulty'] = dgi.getUint8()
            args['height'] = dgi.getInt8()
            
            hood = shard.hoods[hoodId]
            street = hood.streets[streetId]
            block = street.blocks[blockNumber]
            block.update(type, args)
            
        elif updateType == 'inv':
            start = dgi.getUint32()
            duration = dgi.getUint16()
            cogName = dgi.getString()
            skel = dgi.getUint8()
            v2 = dgi.getUint8()
            dept = dgi.getString()
            
            shard.updateInvasion(cogName, skel, start, duration, 0, v2, dept)
            
        else:
            print 'WARNING: Unknown or not implemented updateType %s from %d' % (updateType[:10], shardId)
            
    def setShardData(self, districtName, data):
        shardId = self.air.getMsgSender() + 1
        if shardId not in self.shards:
            self.newShard(districtName)
            
        self.shards[shardId].name = districtName
            
        dg = PyDatagram(data)
        di = PyDatagramIterator(dg)
        context = di.getUint8()
        
        while di.getRemainingSize():
            self._doUpdateShard(di)
            
        if context > 0:
            self.air.sendNetEvent('API_setShardDataRes', [self.air.getMsgSender(), context])
        
    def listInvasions(self):
        if not self.shards:
            return {}
            
        invData = {}
        for i, shard in self.shards.items():
            invData[i] = shard.readInvasion()
            
        return invData
        
    def __killShard(self):
        shardId = self.air.getMsgSender() + 1
        if shardId not in self.shards:
            return
            
        self.notify.info('%d died, removing from shard list...' % shardId)
        del self.shards[shardId]
            
    def __handleInvasionEvent(self, data):
        shardId = self.air.getMsgSender() + 1
        if shardId not in self.shards:
            self.newShard()
            
        shard = self.shards[shardId]
        shard.updateInvasion(data['suitName'], data['skel'], data['startTime'], data['duration'],
                             data['numCogs'], data['v2'], data['dept'])
        
    def __handleBuildingEvent(self, data):        
        shardId = self.air.getMsgSender() + 1
        if shardId not in self.shards:
            self.newShard()
            
        shard = self.shards[shardId]
        
        hoodId = data['hoodId']
        streetId = data['zoneId']
        
        if hoodId == streetId:
            # SZ bldg
            return
        
        blockNumber = data['block']
            
        args = {}
        type = data['state']
            
        args['track'] = data['track']
        args['difficulty'] = data['difficulty']
        args['height'] = data['numFloors']
            
        hood = shard.hoods[hoodId]
        street = hood.streets[streetId]
        block = street.blocks[int(blockNumber)]
        block.update(type, args)
    