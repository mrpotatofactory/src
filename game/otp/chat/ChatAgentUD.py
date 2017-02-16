from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import *
from toontown.chat.TTWhiteList import TTWhiteList
from toontown.toonbase import TTLocalizer

BLACKLIST = TTLocalizer.MakeAToonNameBlacklist
OFFENSE_MSGS = ('-- DEV CHAT -- word blocked: %s', 'Watch your language! This is your first offense. You said "%s".',
                'Watch your language! This is your second offense. Next offense you\'ll get banned for 24 hours. You said "%s".')

class ChatAgentUD(DistributedObjectGlobalUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('ChatAgentUD')
    WantWhitelist = config.GetBool('want-whitelist', True)
    
    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)

        self.whiteList = TTWhiteList()
        self.offenses = {}

    def chatMessage(self, message):
        sender = self.air.getAvatarIdFromSender()
        if sender == 0:
            self.air.writeServerEvent('suspicious', self.air.getAccountIdFromSender(),
                                      'Account sent chat without an avatar', message)
            return
        
        if self.detectBadWords(self.air.getMsgSender(), message):
            return
 
        modifications = self.calcModifications(sender, message)
        
        self.air.writeServerEvent('chat-said', sender, message)

        DistributedAvatar = self.air.dclassesByName['DistributedAvatarUD']
        dg = DistributedAvatar.aiFormatUpdate('setTalk', sender, sender,
                                              self.air.ourChannel,
                                              [0, 0, '', message, modifications, 0])
        self.air.send(dg)
        
    def calcModifications(self, sender, message):
        modifications = []
        words = message.split()
        wantWhitelist = self.WantWhitelist and self.air.friendsManager.getToonAccess(sender) < 400
        for i, word in enumerate(words):
            if word and not self.whiteList.isWord(word):
                modifications.append((i, wantWhitelist))
                
        return modifications

    def detectBadWords(self, sender, message):
        words = message.split()
        for word in words:
            if word.lower() in BLACKLIST:
                accountId = (sender >> 32) & 0xFFFFFFFF
                avId = sender & 0xFFFFFFFF
                
                if not sender in self.offenses:
                    self.offenses[sender] = 0
                    
                if self.air.friendsManager.getToonAccess(avId) < 400:
                    self.offenses[sender] += 1
               
                if self.offenses[sender] >= 3:
                    # Ban the offender
                    msg = 'banned'
                    self.air.banMgr.banUD(1, avId, accountId, 24, 'Chat Abuse')
                    
                else:
                    msg = OFFENSE_MSGS[self.offenses[sender]] % word
                    self.air.sendSysMsg(msg, sender)
                    
                self.air.writeServerEvent('chat-offense', accountId, word=word, num=self.offenses[sender], msg=msg)
                if self.offenses[sender] >= 3:
                    del self.offenses[sender]
                    
                return 1
                
        return 0
        