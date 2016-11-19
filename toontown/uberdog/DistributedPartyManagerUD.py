from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectUD import DistributedObjectUD
from datetime import datetime
from toontown.parties.PartyGlobals import *

class DistributedPartyManagerUD(DistributedObjectUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPartyManagerUD')

    def announceGenerate(self):
        DistributedObjectUD.announceGenerate(self)
        self.partyId2PubInfo = {}

        self.accept('PARTY_query', self.__handleQueryParty)
        self.accept('PARTY_start', self.__handlePartyHasStarted)
        self.accept('PARTY_end', self.__handlePartyDone)
        self.accept('PARTY_toon_joined', self.__handleToonJoinedParty)
        self.accept('PARTY_toon_left', self.__handleToonLeftParty)
        self.accept('PARTY_gate', self.__handleToonAtGate)
        self.accept('PARTY_request_slot', self.__handleRequestPartySlot)
        
        self.accept('shardDied', self.__handleShardDeath)
       
    def __handleQueryParty(self):
        self.air.sendNetEvent('PARTY_queryRes', [self.partyId2PubInfo])

    def _formatParty(self, partyDict):
        return [partyDict['hostId'],
                partyDict['isPrivate'],
                partyDict['activities'],
                partyDict['decorations']]

    def __handlePartyHasStarted(self, partyId, isPrivate, shardId, zoneId, hostName, activities, decorations):
        partyDict = {'hostId': partyId, 'shardId': shardId, 'zoneId': zoneId, 'hostName': hostName,
                     'numGuests': 0, 'maxGuests': MaxToonsAtAParty, 'started': datetime.now(),
                     'activities': activities, 'decorations': decorations, 'isPrivate': isPrivate}           
        self.partyId2PubInfo[partyId] = partyDict
        self.air.writeServerEvent('party-start', partyId=partyId)
        self.__handleQueryParty()
        
        # Notify friends
        hostName = self.air.friendsManager.getToonName(partyId)
        msg = '%s is hosting a party right now! Head yourself to a party gate and join it!' % hostName
        
        friends = self.air.friendsManager.friendsLists.get(partyId, [])
        nf = set()
        for f in friends:
            if f[0] not in nf:
                self.air.sendSysMsg(msg, self.GetPuppetConnectionChannel(f[0]))
                nf.add(f[0])

    def __handlePartyDone(self, partyId):
        if partyId not in self.partyId2PubInfo:
            self.notify.warning("didn't find details for ending party id %d" % partyId)
            return
            
        del self.partyId2PubInfo[partyId]
        self.air.writeServerEvent('party-done', partyId=partyId)
        self.__handleQueryParty()

    def __handleToonJoinedParty(self, partyId, avId):
        party = self.partyId2PubInfo.get(partyId)
        if party:
            party['numGuests'] += 1

    def __handleToonLeftParty(self, partyId, avId):
        party = self.partyId2PubInfo.get(partyId)
        if party:
            party['numGuests'] = max(0, party['numGuests'] - 1)
        
    def __handleRequestPartySlot(self, partyId, avId, gateId):
        shardId = self.air.getMsgSender()
        recepient = self.GetPuppetConnectionChannel(avId)
        
        def _doDeny(reason):
            field = self.air.dclassesByName['DistributedPartyGateAI'].getFieldByName('partyRequestDenied')
            dg = field.aiFormatUpdate(gateId, recepient, shardId, [reason])
            self.air.send(dg)
        
        if partyId not in self.partyId2PubInfo:
            return self._doDeny(PartyGateDenialReasons.Unavailable)
            
        party = self.partyId2PubInfo[partyId]
        if party['numGuests'] >= party['maxGuests']:
            return self._doDeny(PartyGateDenialReasons.Full)

        actIds = []
        for activity in party['activities']:
            actIds.append(activity[0])
            
        info = [party['shardId'], party['zoneId'], party['numGuests'], party['hostName'], actIds, 0]
        field = self.air.dclassesByName['DistributedPartyGateAI'].getFieldByName('setParty')
        dg = field.aiFormatUpdate(gateId, recepient, shardId, [info, partyId])
        self.air.send(dg)

    def __handleToonAtGate(self, avId, gateId):
        shardId = self.air.getMsgSender()
        recepient = self.GetPuppetConnectionChannel(avId)
        
        parties = []
        for pid, party in self.partyId2PubInfo.items():
            if party.get('isPrivate', 0) and pid != avId:
                friends = self.air.friendsManager.friendsLists.get(pid, [])
                if not any(f[0] == avId for f in friends):
                    continue
               
            elapsed = (datetime.now() - party['started']).seconds
            minLeft = int((PARTY_DURATION - elapsed) / 60)
            guests = max(0, min(255, party.get('numGuests', 0)))
            actIds = []
            for activity in party['activities']:
                actIds.append(activity[0])
            
            parties.append([party['shardId'],
                            party['zoneId'],
                            guests,
                            party.get('hostName', ''),
                            actIds,
                            minLeft])
                
        field = self.air.dclassesByName['DistributedPartyGateAI'].getFieldByName('listAllPublicParties')
        dg = field.aiFormatUpdate(gateId, recepient, shardId, [parties])
        self.air.send(dg)
        
    def __handleShardDeath(self):
        shardId = self.air.getMsgSender()
        
        partiesToKill = set()
        for partyId, party in self.partyId2PubInfo.items():
            if party['shardId'] == shardId:
                partiesToKill.add(partyId)
        
        for partyId in partiesToKill:
            self.__handlePartyDone(partyId)
        