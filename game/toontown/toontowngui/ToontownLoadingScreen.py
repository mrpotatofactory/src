from direct.gui.DirectGui import *
from pandac.PandaModules import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
import random

COLORS = (Vec4(0.917, 0.164, 0.164, 1),
 Vec4(0.152, 0.75, 0.258, 1),
 Vec4(0.598, 0.402, 0.875, 1),
 Vec4(0.133, 0.59, 0.977, 1),
 Vec4(0.895, 0.348, 0.602, 1),
 Vec4(0.977, 0.816, 0.133, 1))

class ToontownLoadingScreen():
    __module__ = __name__

    def __init__(self):
        self.__expectedCount = 0
        self.__count = 0
        screen = loader.loadModel('phase_3/models/gui/progress-background')
        self.gui = screen.find('**/gui')
        self.bg = screen.find('**/background')
        self.banner = screen.find('**/paper_note')
        
        self.tip = DirectLabel(guiId='ToontownLoadingScreenTip', parent = self.banner, relief = None,
                                 text='', text_scale = TTLocalizer.TLStip, textMayChange = 1, pos=(-0.41, 0.0, 0.235),
                                 text_fg = (0.4, 0.3, 0.2, 1), text_wordwrap = 9, text_align = TextNode.ALeft)
                                 
        self.title = DirectLabel(guiId = 'ToontownLoadingScreenTitle', parent = self.gui, relief = None,
                                 pos = (-1.06, 0, -0.77), text = '', textMayChange = 1, text_scale = 0.08,
                                 text_fg = (0, 0, 0.5, 1), text_align = TextNode.ALeft)
                                 
        self.waitBar = DirectWaitBar(guiId = 'ToontownLoadingScreenWaitBar', parent = self.gui,
                                     frameSize = (-1.06, 1.06, -0.03, 0.03), pos = (0, 0, -0.85),
                                     text = '')

    def destroy(self):
        self.tip.destroy()
        self.title.destroy()
        self.waitBar.destroy()
        self.gui.removeNode()

    def getTip(self, tipCategory):
        return TTLocalizer.TipTitle + '\n' + random.choice(TTLocalizer.TipDict.get(tipCategory))

    def begin(self, range, label, gui, tipCategory):
        self.waitBar['range'] = range
        self.title['text'] = label
        self.tip['text'] = self.getTip(tipCategory)
        self.__count = 0
        self.__expectedCount = range
        if gui:
            if hasattr(base, 'localAvatar'):
                for av in base.cr.avList:
                    if av.id == int(base.localAvatar.doId):
                        self.bg.setColor(COLORS[av.position])
            else:
                self.bg.setColor(COLORS[3])
                
            self.bg.reparentTo(render2dp, NO_FADE_SORT_INDEX)
            self.gui.reparentTo(aspect2dp, NO_FADE_SORT_INDEX)
        else:
            self.waitBar.reparentTo(aspect2dp, NO_FADE_SORT_INDEX)
            self.title.reparentTo(aspect2dp, NO_FADE_SORT_INDEX)
            self.gui.reparentTo(hidden)
        self.waitBar.update(self.__count)

    def end(self):
        self.waitBar.finish()
        self.waitBar.reparentTo(self.gui)
        self.title.reparentTo(self.gui)
        self.gui.reparentTo(hidden)
        self.bg.reparentTo(hidden)
        return (self.__expectedCount, self.__count)

    def abort(self):
        self.gui.reparentTo(hidden)

    def tick(self):
        self.__count = self.__count + 1
        self.waitBar.update(self.__count)