from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.task import Task
from otp.distributed.OtpDoGlobals import *
from pandac.PandaModules import *
from toontown.parties.DistributedPartyAI import DistributedPartyAI
from datetime import datetime
from toontown.parties.PartyGlobals import *
from otp.ai.MagicWordGlobal import *

class DistributedPartyManagerAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedPartyManagerAI")

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        
        def gtfo():
            self.notify.warning('UD died, gotta gtfo...')
            import os
            os._exit(1)
            
        self.accept('uberdogExit', gtfo)
        self.accept('PARTY_queryRes', self.__handlePubInfoUpdate)
        self.air.sendNetEvent('PARTY_query')
        
        self.partyId2PlanningZone = {}
        self.partyId2PubInfo = {}
        self.id2Party = {}
        
        if config.GetBool('parties-want-fake-party', False):
            self.__startParty(100000002, 10,
                         [
                            (5, 9, 10, 0),
                            (7, 8, 7, 0), (8, 6, 14, 6), (9, 6, 12, 6),
                            (1, 7, 14, 12), (2, 8, 13, 0), (6, 7, 5, 6),
                            (3, 3, 8, 6), (10, 14, 8, 18)
                         ],
                         [
                            (0, 10, 14, 0), (1, 10, 13, 12), (2, 11, 13, 18), (3, 4, 12, 6), (4, 12, 12, 18),
                            (5, 1, 11, 6), (6, 2, 11, 6), (7, 3, 11, 6), (8, 4, 11, 6), (9, 12, 11, 18),
                            (10, 13, 11, 18), (11, 6, 10, 6), (12, 7, 10, 0)
                         ]
                        )
        
    def __handlePubInfoUpdate(self, pi):
        self.partyId2PubInfo = pi

    def canBuyParties(self):
        return True

    def addPartyRequest(self, isPrivate, activities, decorations):
        partyId = avId = self.air.getAvatarIdFromSender()
        if avId not in self.air.doId2do:
            self.air.writeServerEvent('suspicious', avId, 'tried to host a party from another shard')
            return
            
        av = self.air.doId2do[avId]
            
        errorCode = AddPartyErrorCode.AllOk
        price = 0
        hasClock = False
        
        # Base sanity check
        for activity in activities:
            activityId = activity[0]
            if activityId >= len(ActivityIds):
                errorCode = AddPartyErrorCode.ValidationError
                self.air.writeServerEvent('suspicious', avId, 'tried to add invalid activity')
                break
            
            if activityId == ActivityIds.PartyClock:
                hasClock = True
                
            price += ActivityInformationDict[activityId]['cost']

        for decor in decorations:
            decorId = decor[0]
            if decorId >= len(DecorationIds):
                errorCode = AddPartyErrorCode.ValidationError
                self.air.writeServerEvent('suspicious', avId, 'tried to add invalid decoration')
                break
                
            price += DecorationInformationDict[decorId]['cost']
            
        if not hasClock:
            errorCode = AddPartyErrorCode.ValidationError
            self.air.writeServerEvent('suspicious', avId, 'tried to host a party without clock')
            
        elif not av.takeMoney(price):
            errorCode = AddPartyErrorCode.ValidationError
            self.air.writeServerEvent('suspicious', avId, 'tried to host a party they cannot afford')
                
        if errorCode != AddPartyErrorCode.AllOk:
            self.sendUpdateToAvatarId(avId, 'addPartyResponse', [avId, errorCode])
            return

        self.notify.info('party requested: host %s, private %s' % (avId, isPrivate))
        self.sendUpdateToAvatarId(avId, 'addPartyResponse', [avId, errorCode])
        
        self.__startParty(avId, isPrivate, activities, decorations)

    def getPartyZone(self, hostId, zoneId, isAvAboutToPlanParty):
        self.notify.debug('getPartyZone(hostId = %s, zoneId = %s, isAboutToPlan = %s' % (hostId, zoneId, isAvAboutToPlanParty))
        avId = self.air.getAvatarIdFromSender()
        if isAvAboutToPlanParty:
            partyId = self.air.ourChannel + self.air.getContext()
            self.partyId2PlanningZone[partyId] = zoneId
            
        else:
            partyId = hostId
            
        self.sendUpdateToAvatarId(avId, 'receivePartyZone', [hostId, partyId, zoneId])
            
    def __startParty(self, avId, isPrivate, activities, decorations):
        av = self.air.doId2do.get(avId)
        if av:
            name = av.getName()
            
        else:
            name = 'Unknown host'
                
        partyDict = {'partyId': avId, 'isPrivate': isPrivate, 'activities': activities,
                     'decorations': decorations}
        
        zoneId = self.air.allocateZone()
        partyAI = DistributedPartyAI(self.air, avId, zoneId, partyDict, name)
        partyAI.generateWithRequired(zoneId)
        self.id2Party[avId] = partyAI

        self.air.sendNetEvent('PARTY_start', [avId, isPrivate, self.air.ourChannel, zoneId, name, activities, decorations])
        
        self.sendUpdateToAvatarId(avId, 'receivePartyZone', [avId, avId, zoneId])
        
        taskMgr.doMethodLater(PARTY_DURATION, self.closeParty, self.taskName('cleanup-%s' % avId), [avId])

    def closeParty(self, partyId):
        self.air.sendNetEvent('PARTY_end', [partyId])
        
        partyAI = self.id2Party[partyId]
        for av in partyAI.avIdsAtParty:
            self.sendUpdateToAvatarId(av, 'sendAvToPlayground', [av, 0])
            
        self.notify.info('closeParty: %s %s' % (partyId, partyAI.avIdsAtParty))
            
        partyAI.b_setPartyState(PartyStatus.Finished)
        taskMgr.doMethodLater(10, self.__deleteParty, 'closeParty%d' % partyId, extraArgs=[partyId])
    
    def __deleteParty(self, partyId):
        partyAI = self.id2Party[partyId]
        for av in partyAI.avIdsAtParty:
            self.sendUpdateToAvatarId(av, 'sendAvToPlayground', [av, 1])
        
        zoneId = partyAI.zoneId
        partyAI.requestDelete()
        
        del self.id2Party[partyId]
        self.air.deallocateZone(zoneId)

    def freeZoneIdFromPlannedParty(self, hostId, zoneId):
        sender = self.air.getAvatarIdFromSender()
        if sender != hostId:
            self.air.writeServerEvent('suspicious', sender, 'Toon tried to free zone for someone else\'s party!')
            return
            
        partyId = hostIdToPartyId(hostId)
        if partyId in self.partyId2PlanningZone:
            self.air.deallocateZone(self.partyId2PlanningZone[partyId])
            del self.partyId2PlanningZone[partyId]

    def exitParty(self, partyZone):
        avId = self.air.getAvatarIdFromSender()
        for party in self.id2Party.values():
            if party.zoneId == partyZone:
                party._removeAvatar(avId)
                break
                