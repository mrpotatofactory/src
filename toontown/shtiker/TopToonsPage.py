from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import *
from toontown.uberdog import TopToonsGlobals
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.toontowngui import TTDialog
from panda3d.core import *
import ShtikerPage
import datetime, random

class PageMode:
    Current = 0
    History = 1

class TopToonsPage(ShtikerPage.ShtikerPage):
    notify = DirectNotifyGlobal.directNotify.newCategory('TopToonsPage')

    def load(self):
        ShtikerPage.ShtikerPage.load(self)
        self.currentTabPage = CurrentTabPage(self)
        self.currentTabPage.hide()
        self.historyTabPage = HistoryTabPage(self)
        self.historyTabPage.hide()
        titleHeight = 0.61
        self.title = DirectLabel(parent=self, relief=None, text=TTLocalizer.TopToonsPageTitle, text_scale=0.12, pos=(0, 0, titleHeight))
        normalColor = (1, 1, 1, 1)
        clickColor = (0.8, 0.8, 0, 1)
        rolloverColor = (0.15, 0.82, 1.0, 1)
        diabledColor = (1.0, 0.98, 0.15, 1)
        gui = loader.loadModel('phase_3.5/models/gui/fishingBook')
        tabScale = (.05, .05)
        ss = 0.04
        self.currentTab = DirectButton(parent=self, relief=None, text=TTLocalizer.TopToonsPageCurTab, text_scale=tabScale,
                                       text_align=TextNode.ALeft, text_pos=(0.01, 0.0, 0.0), image=gui.find('**/tabs/polySurface1'),
                                       image_pos=(0.68, 1, -0.91), image_hpr=(0, 0, -90), image_scale=(0.033, 0.033, ss),
                                       image_color=normalColor, image1_color=clickColor, image2_color=rolloverColor,
                                       image3_color=diabledColor, text_fg=Vec4(0.2, 0.1, 0, 1), command=self.setMode,
                                       extraArgs=[PageMode.Current], pos=(-0.5, 0, 0.77))
        self.historyTab = DirectButton(parent=self, relief=None, text=TTLocalizer.TopToonsPageHistoryTab, text_scale=tabScale,
                                       text_align=TextNode.ALeft, text_pos=(-0.035, 0.0, 0.0), image=gui.find('**/tabs/polySurface2'),
                                       image_pos=(0.16, 1, -0.91), image_hpr=(0, 0, -90), image_scale=(0.033, 0.033, ss),
                                       image_color=normalColor, image1_color=clickColor, image2_color=rolloverColor,
                                       image3_color=diabledColor, text_fg=Vec4(0.2, 0.1, 0, 1), command=self.setMode,
                                       extraArgs=[PageMode.History], pos=(0.2, 0, 0.77))

    def enter(self):
        self.setMode(PageMode.Current, updateAnyways=1)
        ShtikerPage.ShtikerPage.enter(self)

    def exit(self):
        self.currentTabPage.exit()
        self.historyTabPage.exit()
        ShtikerPage.ShtikerPage.exit(self)

    def unload(self):
        self.currentTabPage.unload()
        del self.title
        ShtikerPage.ShtikerPage.unload(self)

    def setMode(self, mode, updateAnyways = 0):
        messenger.send('wakeup')
        if not updateAnyways:
            if self.mode == mode:
                return
            else:
                self.mode = mode
                
        if mode == PageMode.Current:
            self.currentTab['state'] = DGG.DISABLED
            self.currentTabPage.enter()
            self.historyTab['state'] = DGG.NORMAL
            self.historyTabPage.exit()
            
        elif mode == PageMode.History:
            self.currentTab['state'] = DGG.NORMAL
            self.currentTabPage.exit()
            self.historyTab['state'] = DGG.DISABLED
            self.historyTabPage.enter()
            
        self.mode = mode

class CurrentTabPage(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('CurrentTabPage')
    
    def __init__(self, parent = aspect2d):
        self.parent = parent
        DirectFrame.__init__(self, parent=self.parent, relief=None, pos=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))
        self.mgr = base.cr.topToonsMgr
        self.scrollList = None
        self.rankingLabels = []
        self.__localIndex = -1
        self.textRolloverColor = Vec4(1, 1, 0, 1)
        self.textDownColor = Vec4(0.5, 0.9, 1, 1)
        self.textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)
        self.listXorigin = -0.02
        self.listFrameSizeX = 1.5
        self.listZorigin = -0.96
        self.listFrameSizeZ = .92
        self.arrowButtonScale = 1.3
        self.itemFrameXorigin = -0.237
        self.itemFrameZorigin = 0.365
        self.buttonXstart = .5
        self.load()

    def destroy(self):
        self.parent = None
        DirectFrame.destroy(self)

    def load(self):
        self.gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        
        self.curText = OnscreenText(parent=self, text=self.__getCurrentChallengeText(),
                                    scale=0.07, pos=(0, .52), wordwrap = 1.5 / .07)
    
    def __getCurrentChallengeText(self):
        curText = TTLocalizer.TopToonsPageCurTab
        curText = curText[0].upper() + curText[1:].lower()
        curText += ": "
        curText += repr(self.mgr.currentChallenge)
        curText = curText[:-len(TTLocalizer.Period)]
        curText += " and win %d jellybeans." % self.mgr.currentChallenge.reward
        return curText

    def enter(self):
        self.show()
        self.updateTab()
        self.accept("topToonsUpdated", self.updateTab)

    def exit(self):
        self.hide()
        self.ignore("topToonsUpdated")

    def unload(self):
        self.curText.destroy()
        del self.curText
        
        if self.scrollList:
            self.scrollList.destroy()
        del self.scrollList

    def regenerateScrollList(self):
        if self.scrollList:
            self.scrollList.destroy()
            
        self.scrollList = DirectScrolledList(parent=self, relief=None, pos=(-0.5, 0, 0),
                                             incButton_image=(self.gui.find('**/FndsLst_ScrollUp'),
                                                              self.gui.find('**/FndsLst_ScrollDN'),
                                                              self.gui.find('**/FndsLst_ScrollUp_Rllvr'),
                                                              self.gui.find('**/FndsLst_ScrollUp')),
                                             incButton_relief=None,
                                             incButton_scale=(self.arrowButtonScale, self.arrowButtonScale, -self.arrowButtonScale),
                                             incButton_pos=(self.buttonXstart, 0, self.itemFrameZorigin - 0.999),
                                             incButton_image3_color=Vec4(1, 1, 1, 0.2),
                                             decButton_image=(self.gui.find('**/FndsLst_ScrollUp'),
                                                              self.gui.find('**/FndsLst_ScrollDN'),
                                                              self.gui.find('**/FndsLst_ScrollUp_Rllvr'),
                                                              self.gui.find('**/FndsLst_ScrollUp')),
                                             decButton_relief=None,
                                             decButton_scale=(self.arrowButtonScale, self.arrowButtonScale, self.arrowButtonScale),
                                             decButton_pos=(self.buttonXstart, 0, self.itemFrameZorigin),
                                             decButton_image3_color=Vec4(1, 1, 1, 0.2),
                                             itemFrame_pos=(self.itemFrameXorigin, 0, self.itemFrameZorigin),
                                             itemFrame_scale=1.0, itemFrame_relief=DGG.SUNKEN,
                                             itemFrame_frameSize=(self.listXorigin,
                                                                  self.listXorigin + self.listFrameSizeX,
                                                                  self.listZorigin,
                                                                  self.listZorigin + self.listFrameSizeZ),
                                             itemFrame_frameColor=(0.85, 0.95, 1, 1), itemFrame_borderWidth=(0.01, 0.01),
                                             numItemsVisible=13, forceHeight=0.065, items=self.rankingLabels)
        self.scrollList.scrollTo(self.__localIndex)
        
    def updateTab(self):
        self.curText.setText(self.__getCurrentChallengeText())
        for x in self.rankingLabels:
            x.destroy()
            
        self.rankingLabels = []
            
        def makeLabel(index, name, score):
            label = DirectLabel(text="%s. %s: %d" % (index, name, score), text_scale=.085,
                                relief=None, text_pos=(-self.itemFrameXorigin / 2., -self.itemFrameZorigin / 2. + 0.05),
                                text_align=TextNode.ALeft)
            self.rankingLabels.append(label)
            
        self.__localIndex = -1
        hasLocal = 0
        
        for index, (avId, name, score) in enumerate(self.mgr.ranking[::-1]):
            if avId == localAvatar.doId:
                self.__localIndex = index
                hasLocal = 1
                
            makeLabel(index + 1, name, score)
            
        if not hasLocal:
            self.__localIndex += len(self.rankingLabels)
            makeLabel("-", localAvatar.getName(), 0)
            
        self.regenerateScrollList()
        
class HistoryTabPage(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('HistoryTabPage')

    def __init__(self, parent = aspect2d):
        self.parent = parent
        DirectFrame.__init__(self, parent=self.parent, relief=None, pos=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))
        self.mgr = base.cr.topToonsMgr
        self.scrollList = None
        self.historyLabels = []
        self.textRolloverColor = Vec4(1, 1, 0, 1)
        self.textDownColor = Vec4(0.5, 0.9, 1, 1)
        self.textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)
        self.listXorigin = -0.02
        self.listFrameSizeX = 1.5
        self.listZorigin = -0.96
        self.listFrameSizeZ = 1
        self.arrowButtonScale = 1.3
        self.itemFrameXorigin = -0.237
        self.itemFrameZorigin = 0.365
        self.buttonXstart = .5
        self.load()

    def destroy(self):
        self.parent = None
        DirectFrame.destroy(self)

    def load(self):
        self.gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')

    def enter(self):
        self.show()
        self.updateTab()
        self.accept("topToonsUpdated", self.updateTab)

    def exit(self):
        self.hide()
        self.ignore("topToonsUpdated")

    def unload(self):
        if self.scrollList:
            self.scrollList.destroy()  
        del self.scrollList

    def __makeFrame(self, index, seed, name, time):
        r = random.Random()
        r.seed(seed)
        
        R = r.random()
        G = r.random()
        B = r.random()
        
        ch = TopToonsGlobals.getChallenge(seed)
        timestr = str(datetime.timedelta(seconds=time))
        frame = DirectFrame(parent=hidden, relief=None, frameSize=(-.75, .75, -.2, .2), frameColor=(R, G, B, 1))
        s = .06
        OnscreenText(text='%d. %s completed: %s in %s and won %d jellybeans.' % (index, name, repr(ch)[:-len(TTLocalizer.Period)],
                                                                                 timestr, ch.reward),
                     parent=frame, scale=s, align=TextNode.ALeft, pos = (0, s - .1), wordwrap=1.5 / s)
        return frame
        
    def regenerateScrollList(self):
        if self.scrollList:
            self.scrollList.destroy()
            
        self.scrollList = DirectScrolledList(parent=self, relief=None, pos=(-0.5, 0, 0),
                                             incButton_image=(self.gui.find('**/FndsLst_ScrollUp'),
                                                              self.gui.find('**/FndsLst_ScrollDN'),
                                                              self.gui.find('**/FndsLst_ScrollUp_Rllvr'),
                                                              self.gui.find('**/FndsLst_ScrollUp')),
                                             incButton_relief=None,
                                             incButton_scale=(self.arrowButtonScale, self.arrowButtonScale, -self.arrowButtonScale),
                                             incButton_pos=(self.buttonXstart, 0, self.itemFrameZorigin - 0.999),
                                             incButton_image3_color=Vec4(1, 1, 1, 0.2),
                                             decButton_image=(self.gui.find('**/FndsLst_ScrollUp'),
                                                              self.gui.find('**/FndsLst_ScrollDN'),
                                                              self.gui.find('**/FndsLst_ScrollUp_Rllvr'),
                                                              self.gui.find('**/FndsLst_ScrollUp')),
                                             decButton_relief=None,
                                             decButton_scale=(self.arrowButtonScale, self.arrowButtonScale, self.arrowButtonScale),
                                             decButton_pos=(self.buttonXstart, 0, self.itemFrameZorigin + .1),
                                             decButton_image3_color=Vec4(1, 1, 1, 0.2),
                                             itemFrame_pos=(self.itemFrameXorigin, 0, self.itemFrameZorigin),
                                             itemFrame_scale=1.0, itemFrame_relief=DGG.SUNKEN,
                                             itemFrame_frameSize=(self.listXorigin,
                                                                  self.listXorigin + self.listFrameSizeX,
                                                                  self.listZorigin,
                                                                  self.listZorigin + self.listFrameSizeZ),
                                             itemFrame_frameColor=(0.85, 0.95, 1, 1), itemFrame_borderWidth=(0.01, 0.01),
                                             numItemsVisible=5, forceHeight=.2, items=self.historyLabels)
        
    def updateTab(self):
        for x in self.historyLabels:
            x.destroy()
            
        self.historyLabels = []
        
        for index, (name, time, seed) in enumerate(self.mgr.history[::-1]):
            self.historyLabels.append(self.__makeFrame(index + 1, seed, name, time))
            
        self.regenerateScrollList()
        