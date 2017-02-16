from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from toontown.hood import SkyUtil
from toontown.toon import Toon, ToonDNA, LaffMeter
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.toontowngui.TTDialog import *

COLORS = (Vec4(0.917, 0.164, 0.164, 1),
 Vec4(0.152, 0.75, 0.258, 1),
 Vec4(0.598, 0.402, 0.875, 1),
 Vec4(0.133, 0.59, 0.977, 1),
 Vec4(0.895, 0.348, 0.602, 1),
 Vec4(0.977, 0.816, 0.133, 1))
 
PLAY = TTLocalizer.AvatarChoicePlayThisToon.upper().replace('\n', ' ')
MAKE = TTLocalizer.AvatarChoiceMakeAToon.upper().replace('\n', ' ')
DEL = TTLocalizer.PhotoPageDelete + ' %s?'

class NewPickAToon:
    def __init__(self, avList, parentFSM, doneEvent):
        self.toonsList = {i: (i in [x.position for x in avList]) for i in xrange(6)}
        self.avList = avList
        
        self.currentSlot = 0
        self.doneEvent = doneEvent

    def load(self, isPaid=1):
        self.patNode = render.attachNewNode('patNode')
        self.pat2dNode = aspect2d.attachNewNode('pat2dNode')
        
        self.background = loader.loadModel('phase_5.5/models/estate/terrain.bam')
        self.background.reparentTo(self.patNode)
        self.sky = loader.loadModel('phase_3.5/models/props/TT_sky')
        self.sky.reparentTo(self.pat2dNode)

        self.infoText = OnscreenText(font=ToontownGlobals.getSignFont(), text=TTLocalizer.AvatarChooserPickAToon,
                                     scale=TTLocalizer.ACtitle, fg=COLORS[self.currentSlot], pos=(0, .855),
                                     parent=self.pat2dNode)
                                     
        arrow = loader.loadModel('phase_3/models/props/arrow.bam')
        self.arrowRight = DirectButton(geom=arrow, relief=None, command=self.__right)
        self.arrowRight.reparentTo(self.pat2dNode)
        self.arrowRight.setPos(.6, 0, -.2)
        self.arrowRight.setR(0)
        self.arrowRight.setScale(.255)
        self.arrowRight.setColor(1, 1, 0, .95)
        
        self.arrowLeft = DirectButton(geom=arrow, relief=None, command=self.__left)
        self.arrowLeft.reparentTo(self.pat2dNode)
        self.arrowLeft.setPos(-.6, 0, -.2)
        self.arrowLeft.setR(180)
        self.arrowLeft.setScale(.255)
        self.arrowLeft.setColor(1, 0, 0, .95)
        self.arrowLeft.hide()

        self.origin = self.patNode.attachNewNode('toon-origin')
        self.origin.reparentTo(self.patNode)
        self.origin.setPos(-50,-11,3.5)
        self.origin.setHpr(180, 0, 0)
        self.origin.setScale(1.625)
        
        self.matText = OnscreenText(pos=(0, -.155), text=TTLocalizer.AvatarChoiceMakeAToon,
                                    font=ToontownGlobals.getMinnieFont(), fg=(1, 1, 0, 1),
                                    parent=self.pat2dNode, scale=.135, shadow=(0,0,0,1))
                                    
        bdes = loader.loadModel('phase_3/models/gui/quit_button.bam')
        self.play = DirectButton(relief=None, geom=(bdes.find('**/QuitBtn_UP'), bdes.find('**/QuitBtn_DN'),
                                                    bdes.find('**/QuitBtn_RLVR'),bdes.find('**/QuitBtn_UP')),
                                 text=PLAY, text_scale=.050, text_pos=(0, -0.013), scale=1.3,
                                 pos=(.8, 0, -.6), command=self.startGame, parent=self.pat2dNode)
        
        self.name = OnscreenText(pos=(0, -.5), scale=.1, fg=COLORS[self.currentSlot], parent=self.pat2dNode,
                                 shadow=(0,0,0,1), font=ToontownGlobals.getToonFont())
        self.area = OnscreenText(parent=self.pat2dNode, font=ToontownGlobals.getToonFont(),
                                 pos=(-.7, -.855), scale=.075, text='', shadow=(0,0,0,1), fg=COLORS[self.currentSlot])

        trashcanGui = loader.loadModel('phase_3/models/gui/trashcan_gui.bam')
        self.deleteButton = DirectButton(parent=base.a2dBottomRight,
                                         geom=(trashcanGui.find('**/TrashCan_CLSD'),
                                               trashcanGui.find('**/TrashCan_OPEN'),
                                               trashcanGui.find('**/TrashCan_RLVR')),
                                         text=('', TTLocalizer.AvatarChoiceDelete,
                                                   TTLocalizer.AvatarChoiceDelete, ''),
                                         text_scale=.075, text_pos=(0, -0.3), relief=None,
                                         scale=.5, command=self.__handleDelete, pos=(-.2, 0, .2))
                                        
        self.toon = Toon.Toon()
        self.toon.reparentTo(self.origin)
        self.toon.setDNAString(ToonDNA.ToonDNA().makeNetString()) # initialize with garbage
        self.toon.hide()
        self.toon.deleteDropShadow()
        
        self.statusText = OnscreenText(pos=(0, -.8), text='', font=ToontownGlobals.getToonFont(),
                                       fg=(0, 0, 0, 1), parent=self.pat2dNode, scale=.075)
                                       
        self.nameYourToonButton = DirectButton(relief=None, geom=(bdes.find('**/QuitBtn_UP'), bdes.find('**/QuitBtn_DN'),
                                                                  bdes.find('**/QuitBtn_RLVR'),bdes.find('**/QuitBtn_UP')),
                                               text=TTLocalizer.AvatarChoiceNameYourToon.upper().replace('\n', ' '),
                                               text_scale=.045, text_pos=(0, -0.013), scale=1.3, pos=(.8, 0, -.47), command=self.__nameIt,
                                               parent=self.pat2dNode)
    
    def skyTrack(self, task):
        return SkyUtil.cloudSkyTrack(task)
    
    def enter(self):
        base.cam.setPos(-50,-27,6.5)
        base.cam.setHpr(0,4,0)
 
        SkyUtil.startCloudSky(self)
        
        self.patNode.unstash()
        self.pat2dNode.unstash()
        self.deleteButton.unstash()
        
        self.toon.initializeDropShadow()
        self.toon.find('**/lightPath').setPos(2, -5, 8)
        
        self.__updateMainButton()
        self.__updateFunction()
        
    def exit(self):
        base.cam.iPosHpr()
 
        taskMgr.remove('skyTrack')
        self.sky.reparentTo(hidden)
        
        self.toon.deleteDropShadow()
        
        self.patNode.stash()
        self.pat2dNode.stash()
        self.deleteButton.stash()
        
    def unload(self):
        self.patNode.removeNode()
        self.pat2dNode.removeNode()
        self.deleteButton.removeNode()
        
        del self.patNode
        del self.pat2dNode
        
    def __left(self):
        self.currentSlot -= 1
        
        if self.currentSlot == 0:
            self.arrowLeft.hide()
            
        elif self.currentSlot < 0:
            self.currentSlot = 0
            
        else:
            self.arrowRight.show()
            self.arrowRight.setColor(1, 1, 0, 1)
            self.arrowLeft.setColor(1, 1, 0, 1)
            
        self.__updateFunction()
            
    def __right(self):
        self.currentSlot += 1
        
        if self.currentSlot == 5:
            self.arrowRight.hide()
            
        elif self.currentSlot > 5:
            self.currentSlot = 5
            
        else:
            self.arrowLeft.show()
            self.arrowLeft.setColor(1, 1, 0, 1)
            self.arrowRight.setColor(1, 1, 0, 1)
            
        self.__updateFunction()
    
    def __updateFunction(self):
        self.infoText['fg'] = COLORS[self.currentSlot]
        self.name['fg'] = COLORS[self.currentSlot]
        self.area['fg'] = COLORS[self.currentSlot]
                
        if hasattr(self, 'laffmeter'):
            self.laffmeter.destroy()
            del self.laffmeter
            
        hasToon = self.toonsList[self.currentSlot]
        if hasToon:
            self.matText.hide()
            self.showToon()
            self.deleteButton.show()
            
        else:
            self.name['text'] = ''
            self.area['text'] = ''
            self.deleteButton.hide()
            self.matText.show()
            self.toon.hide()
            self.toon.deleteDropShadow()
            self.nameYourToonButton.hide()
            self.statusText['text'] = ''
            
        self.__updateMainButton()
    
    def showToon(self):        
        av = [x for x in self.avList if x.position == self.currentSlot][0]
        dna = av.dna
        
        if av.wantName != '':
            self.nameYourToonButton.hide()
            self.statusText['text'] = TTLocalizer.AvatarChoiceNameReview
        
        elif av.approvedName != '':
            self.nameYourToonButton.hide()
            self.statusText['text'] = TTLocalizer.AvatarChoiceNameApproved
        
        elif av.rejectedName != '':
            self.nameYourToonButton.hide()
            self.statusText['text'] = TTLocalizer.AvatarChoiceNameRejected
        
        elif av.allowedName == 1:
            self.nameYourToonButton.show()
            self.statusText['text'] = ''
                
        else:
            self.nameYourToonButton.hide()
            self.statusText['text'] = ''
               
        self.toon.setDNAString(dna)
        self.toon.loop('neutral')
        self.toon.show()
        self.toon.initializeDropShadow()
        self.toon.find('**/lightPath').setPos(2, -5, 8)
            
        self.laffmeter = LaffMeter.LaffMeter(ToonDNA.ToonDNA(dna), av.hp, av.maxHp)
        self.laffmeter.setPos(-.7, 0, -.655)
        self.laffmeter.setScale(self.laffmeter, .8)
        self.laffmeter.start()
        self.laffmeter.reparentTo(self.pat2dNode)
        
        self.name.setText(av.name.decode('latin-1'))

        lastAreaName = ToontownGlobals.hoodNameMap.get(av.lastHood, [''])[-1]
        self.area.setText(lastAreaName)
        
    def __updateMainButton(self):
        if self.toonsList[self.currentSlot]:
            self.play['text'] = PLAY
            self.play['command'] = self.startGame
            
        else:
            self.play['text'] =  MAKE
            self.play['command'] = self.startMAT
    
    def startGame(self):
        doneStatus = {'mode': 'chose', 'choice': self.currentSlot}
        messenger.send(self.doneEvent, [doneStatus])

    def startMAT(self):
        doneStatus = {'mode': 'create', 'choice': self.currentSlot}
        messenger.send(self.doneEvent, [doneStatus])
        
    def getStatus(self):
        return self.doneStatus
        
    def __handleDelete(self):
        av = [x for x in self.avList if x.position == self.currentSlot][0]
        
        def diagDone():
            mode = delDialog.doneStatus
            delDialog.cleanup()
            base.transitions.noFade()
            if mode == 'ok':
                messenger.send(self.doneEvent, [{'mode': 'delete'}])
        
        base.acceptOnce('pat-del-diag-done', diagDone)
        delDialog = TTGlobalDialog(message=DEL % av.name, style=YesNo,
                                   doneEvent='pat-del-diag-done')
        base.transitions.fadeScreen(.5)
        
    def __nameIt(self):
        doneStatus = {'mode': 'nameIt', 'choice': self.currentSlot}
        messenger.send(self.doneEvent, [doneStatus])
        
    def getChoice(self):
        return self.currentSlot
        