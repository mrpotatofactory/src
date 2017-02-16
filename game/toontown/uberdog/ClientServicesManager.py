from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from direct.directnotify.DirectNotifyGlobal import directNotify
from otp.distributed.PotentialAvatar import PotentialAvatar
from pandac.PandaModules import *
import hashlib
import sys

try:
    # N.B. libchallenge is not available in dev source
    # This is only built in public client
    sys.path.append('..')
    import libchallenge
    sys.path.remove('..')
    
except ImportError:
    class libchallenge:
        @staticmethod
        def solve(a, b, c):
            return 'dev'

class ClientServicesManager(DistributedObjectGlobal):
    notify = directNotify.newCategory('ClientServicesManager')

    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)
        self.__secret = config.GetString('csm-secret', 'dev')
        loadPrcFileData('', 'csm-secret dev')
    
    def performLogin(self, doneEvent):
        self.doneEvent = doneEvent
        self.sendUpdate('requestChallenge', [])

    def challenge(self, data):
        cookie = self.cr.playToken or 'dev'
        hash = hashlib.sha512()
        hash.update(cookie + self.__secret)
                
        challengeResp = libchallenge.solve(cookie, data, self.__secret)
        
        self.__secret = "dev"
        
        self.notify.debug('Sending login cookie: ' + cookie)
        self.sendUpdate('login', [cookie, hash.digest(), challengeResp])

    def acceptLogin(self, access):
        self.cr.setIsPaid(access)
        messenger.send(self.doneEvent, [{'mode': 'success'}])
        
        if not __debug__:
            # set token to _launcher
            # fixes "try again leads to login issue" error
            base.cr.playToken = "_launcher"

    def requestAvatars(self):
        self.sendUpdate('requestAvatars')

    def setAvatars(self, avatars):
        avList = []
        for avNum, avName, avDNA, avPosition, nameState, hp, maxHp, lastHood in avatars:
            nameOpen = int(nameState == 1)
            names = [avName, '', '', '']
            if nameState == 2: # PENDING
                names[1] = avName
            elif nameState == 3: # APPROVED
                names[2] = avName
            elif nameState == 4: # REJECTED
                names[3] = avName
            av = PotentialAvatar(avNum, names, avDNA, avPosition, nameOpen)
            av.hp = maxHp
            av.maxHp = maxHp
            av.lastHood = lastHood
            avList.append(av)

        self.cr.handleAvatarsList(avList)

    # --- AVATAR CREATION/DELETION ---
    def sendCreateAvatar(self, avDNA, name, index, tf):
        self.notify.info('sendChooseAvatar: %s' % tf)
        self.sendUpdate('createAvatar', [avDNA.makeNetString(), name, index, tf])

    def createAvatarResp(self, avId):
        messenger.send('nameShopCreateAvatarDone', [avId])

    def sendDeleteAvatar(self, avId):
        self.sendUpdate('deleteAvatar', [avId])

    # No deleteAvatarResp; it just sends a setAvatars when the deed is done.

    # --- AVATAR NAMING ---
    def updateAvatarName(self, avId, name, callback):
        self._callback = callback
        self.sendUpdate('updateName', [avId, name])

    def updateNameResp(self):
        self._callback()

    def sendAcknowledgeAvatarName(self, avId, callback):
        self._callback = callback
        self.sendUpdate('acknowledgeAvatarName', [avId])

    def acknowledgeAvatarNameResp(self):
        self._callback()

    # --- AVATAR CHOICE ---
    def sendChooseAvatar(self, avId):
        self.sendUpdate('chooseAvatar', [avId])

    # No response: instead, an OwnerView is sent or deleted.
