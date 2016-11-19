from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject
from direct.distributed.PyDatagram import *
import time

from toontown.building import DistributedAnimBuildingAI, DistributedBuildingAI

class ShardAPIManagerAI(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('ShardAPIManagerAI')
    
    def __init__(self, air):
        self.air = air
        self.context = 0
        
        self.bldgs = set()
        self.accept('API_setShardDataRes', self.setShardDataRes)
            
    def d_setShardData(self):
        dg = PyDatagram()
        
        self.context += 1
        self.context %= 200
        dg.addUint8(self.context)
        
        buildings = self.air.doFindAllInstances(DistributedBuildingAI.DistributedBuildingAI)
        for bldg in buildings:
            if bldg.__class__ in (DistributedBuildingAI.DistributedBuildingAI, DistributedAnimBuildingAI.DistributedAnimBuildingAI):
                if not bldg.zoneId % 1000:
                    # sz bldg, ignore
                    continue
                    
                if bldg.zoneId // 1000 == 7:
                    # ff bldg, ignore now
                    continue
                    
                data = bldg.getPickleData()

                dg.addString('block')
                dg.addUint16(bldg.zoneId - (bldg.zoneId % 1000))
                dg.addUint16(bldg.zoneId)
                dg.addUint8(int(data['block']))
                dg.addString(data['state'].lower())
                dg.addUint8(ord(data['track']))
                dg.addUint8(int(data['difficulty']))
                dg.addInt8(int(data['numFloors']))
                
                self.bldgs.add(bldg)
                    
        self.writeInvasion(dg)
        self.air.sendNetEvent('API_setShardData', [self.air.districtName, dg.getMessage()])
                            
        self.air.notify.info('Sent shard data to UD')
        taskMgr.doMethodLater(60, self.__timeout, 'UD-sync-timeout')
        
    def __timeout(self, task):
        self.notify.error('Timeout waiting for UD sync, leaving...')
        return task.done
            
    def setShardDataRes(self, shardId, context):
        if shardId != self.air.ourChannel:
            return
            
        if self.context == 0:
            self.air.notify.warning('got unexpected setShardDataRes')
            
        elif context != self.context:
            self.air.notify.warning('got bad context for setShardDataRes (%d), expecting %d' % (context, self.context))

        self.air.gotUberdogAPISync()
        taskMgr.remove('UD-sync-timeout')
        
    def writeInvasion(self, dg):
        name, skel, _, startTime, duration, v2, dept = self.air.suitInvasionManager.getCurrentInvasion()

        dg.addString('inv')
        dg.addUint32(int(time.time()))
        dg.addUint16(duration)
        dg.addString(name)
        dg.addUint8(0 if not skel else 1)
        dg.addUint8(0 if not v2 else 1)
        dg.addString(dept)
        