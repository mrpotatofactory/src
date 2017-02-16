from otp.avatar.Avatar import teleportNotify
from toontown.toonbase import ToontownGlobals
from toontown.chat import ToonChatGarbler

class FriendHandle:

    def __init__(self, doId, name, style, petId, isAPet = False):
        self.doId = doId
        self.style = style
        self.commonChatFlags = 0
        self.whitelistChatFlags = 0
        self.petId = petId
        self.isAPet = isAPet
        self.chatGarbler = ToonChatGarbler.ToonChatGarbler()
        self.name = name

    def getDoId(self):
        return self.doId

    def getPetId(self):
        return self.petId

    def hasPet(self):
        return self.getPetId() != 0

    def isPet(self):
        return self.isAPet

    def getName(self):
        return self.name

    def getFont(self):
        return ToontownGlobals.getToonFont()

    def getStyle(self):
        return self.style

    def uniqueName(self, idString):
        return idString + '-' + str(self.getDoId())

    def d_battleSOS(self, requesterId):
        base.localAvatar.sendUpdate('battleSOS', [requesterId], sendToId=self.doId)

    def d_teleportQuery(self, requesterId):
        teleportNotify.debug('sending d_teleportQuery(%s)' % (requesterId,))
        base.cr.ttFriendsManager.d_teleportQuery(self.doId)

    def d_teleportResponse(self, avId, available, shardId, hoodId, zoneId):
        teleportNotify.debug('sending teleportResponse%s' % ((avId,
          available,
          shardId,
          hoodId,
          zoneId),))
        base.cr.ttFriendsManager.sendUpdate('routeTeleportResponse', [avId,
         available,
         shardId,
         hoodId,
         zoneId])

    def d_teleportGiveup(self, requesterId):
        teleportNotify.debug('sending d_teleportGiveup(%s)' % (requesterId,))
        base.localAvatar.sendUpdate('teleportGiveup', [requesterId], sendToId=self.doId)

    def isUnderstandable(self):
        if self.commonChatFlags & base.localAvatar.commonChatFlags & ToontownGlobals.CommonChat:
            understandable = 1
        elif self.commonChatFlags & ToontownGlobals.SuperChat:
            understandable = 1
        elif base.localAvatar.commonChatFlags & ToontownGlobals.SuperChat:
            understandable = 1
        elif base.cr.getFriendFlags(self.doId) & ToontownGlobals.FriendChat:
            understandable = 1
        elif self.whitelistChatFlags & base.localAvatar.whitelistChatFlags:
            understandable = 1
        else:
            understandable = 0
        return understandable

    def scrubTalk(self, message, mods):
        scrub = self is not localAvatar
        
        if scrub:
            for friendId, flags in localAvatar.friendsList:
                if friendId == self.doId:
                    if flags & 1:
                        # True friends detected
                        scrub = 0
 
        words = message.split()
        mods = [m[0] for m in mods]
        
        for i in xrange(len(words)):
            if i in mods:
                if scrub:
                    words[i] = self.chatGarbler.garbleSingle(self, words[i])
                    
                else:
                    words[i] = '\x01WLDisplay\x01%s\x02' % words[i]

        newText = ' '.join(words)
        return (newText, scrub)

    def replaceBadWords(self, text):
        words = text.split(' ')
        newwords = []
        for word in words:
            if word == '':
                newwords.append(word)
            elif word[0] == '\x07':
                newwords.append('\x01WLRed\x01' + self.chatGarbler.garbleSingle(self, word) + '\x02')
            elif base.whiteList.isWord(word):
                newwords.append(word)
            else:
                newwords.append('\x01WLRed\x01' + word + '\x02')

        newText = ' '.join(newwords)
        return newText

    def setCommonAndWhitelistChatFlags(self, commonChatFlags, whitelistChatFlags):
        self.commonChatFlags = commonChatFlags
        self.whitelistChatFlags = whitelistChatFlags
