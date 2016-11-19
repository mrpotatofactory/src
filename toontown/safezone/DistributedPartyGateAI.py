from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from toontown.parties import PartyGlobals

class DistributedPartyGateAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedPartyGateAI")

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.area = None

    def setArea(self, area):
        self.area = area

    def getArea(self):
        return self.area

    def getPartyList(self, avId):
        # Let the UD handle this shit
        self.air.sendNetEvent('PARTY_gate', [self.air.getAvatarIdFromSender(), self.doId])

    def partyChoiceRequest(self, avId, shardId, zoneId):
        # Try to get a spot for them in the party
        # find partyId
        avId = self.air.getAvatarIdFromSender()
        
        for partyId in self.air.partyManager.partyId2PubInfo:
            p = self.air.partyManager.partyId2PubInfo[partyId]
            if p.get('shardId', 0) == shardId and p.get('zoneId', 0) == zoneId:
                pid = partyId
                break
                
        else:
            self.air.writeServerEvent('suspicious', avId, 'Tried to request non-existing party')
            self.sendUpdateToAvatarId(avId, 'partyRequestDenied', [PartyGlobals.PartyGateDenialReasons.Unavailable])
            return
        
        # Let the UD handle this shit yet again      
        self.air.sendNetEvent('PARTY_request_slot', [pid, avId, self.doId])
        