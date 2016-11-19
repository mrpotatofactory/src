from MarginPopup import *
from ClickablePopup import *
from otp.nametag import NametagGlobals
from otp.nametag.NametagConstants import *

class WhisperPopup(MarginPopup, ClickablePopup):
    WTNormal = WTNormal
    WTQuickTalker = WTQuickTalker
    WTSystem = WTSystem
    WTBattleSOS = WTBattleSOS
    WTEmote = WTEmote
    WTToontownBoardingGroup = WTToontownBoardingGroup

    WORDWRAP = 7.5
    SCALE_2D = 0.3

    def __init__(self, text, font, whisperType, timeout=10.0):
        ClickablePopup.__init__(self)
        MarginPopup.__init__(self)

        self.innerNP = NodePath.anyPath(self).attachNewNode('innerNP')
        self.innerNP.setScale(self.SCALE_2D)

        self.text = text
        self.font = font
        self.whisperType = whisperType
        self.timeout = timeout

        self.setClickRegionEvent(None)
        self.updateContents()

        self.setPriority(2)
        self.setVisible(True)

    def updateContents(self):
        if self.whisperType in WHISPER_COLORS:
            cc = self.whisperType
        else:
            cc = WTSystem
        fgColor, bgColor = WHISPER_COLORS[cc][self.getClickState()]

        balloon = NametagGlobals.speechBalloon2d.generate(
            self.text, self.font, textColor=fgColor, balloonColor=bgColor,
            wordWrap=self.WORDWRAP)
        balloon.reparentTo(self.innerNP)

        # Calculate the center of the TextNode.
        text = balloon.find('**/+TextNode')
        t = text.node()
        left, right, bottom, top = t.getFrameActual()
        center = self.innerNP.getRelativePoint(text,
                                               ((left+right)/2., 0, (bottom+top)/2.))

        # Next translate the balloon along the inverse.
        balloon.setPos(balloon, -center)
        self.considerUpdateClickRegion()

    def setClickable(self, senderName, fromId, todo=0):
        self.__click = (senderName, fromId, None)
        ev = 'whisper-click-%x' % id(self)
        self.setClickRegionEvent(ev)
        self.slaveObject.accept(ev, self.__clicked)
        self.updateContents()
        
    def __clicked(self):
        self.unmanage(self.getManager())
        localAvatar.chatMgr.whisperTo(*self.__click)
        
    def marginVisibilityChanged(self):
        self.considerUpdateClickRegion()

    def clickStateChanged(self):
        self.updateContents()
        
    def considerUpdateClickRegion(self):
        if self.isDisplayed():
            self.updateClickRegion(-1, 0, -1, 0)#            self.updateClickRegion(-1, 1, -1, 1)

    def manage(self, manager):
        MarginPopup.manage(self, manager)
        self.considerUpdateClickRegion()

        taskMgr.doMethodLater(self.timeout, lambda: self.unmanage(self.getManager()),
                              'whisper-timeout-%d' % id(self), [])
                              
    def unmanage(self, manager):
        MarginPopup.unmanage(self, manager)
        if manager:
            self.destroy()
            self.setClickRegionEvent(None)
        
