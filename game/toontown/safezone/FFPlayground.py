from pandac.PandaModules import *
import Playground
from direct.task.Task import Task
import random
from direct.fsm import ClassicFSM, State
from direct.actor import Actor
from toontown.toonbase import ToontownGlobals
from direct.directnotify import DirectNotifyGlobal
from toontown.hood import Place
from toontown.safezone import PicnicBasket

class FFPlayground(Playground.Playground):
    notify = DirectNotifyGlobal.directNotify.newCategory('FFPlayground')

    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)
        self.parentFSM = parentFSM
        self.picnicBasketBlockDoneEvent = 'picnicBasketBlockDone'
        self.fsm.addState(State.State('picnicBasketBlock', self.enterPicnicBasketBlock, self.exitPicnicBasketBlock, ['walk']))
        state = self.fsm.getStateNamed('walk')
        state.addTransition('picnicBasketBlock')
        self.picnicBasketDoneEvent = 'picnicBasketDone'
        self.cameraSubmerged = -1
        self.toonSubmerged = -1
    
    def load(self):
        Playground.Playground.load(self)

    def unload(self):
        Playground.Playground.unload(self)

    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)

    def exit(self):
        Playground.Playground.exit(self)
        taskMgr.remove('ff-check-toon-underwater')
        taskMgr.remove('ff-check-cam-underwater')

    def enterStart(self):
        self.cameraSubmerged = 0
        self.toonSubmerged = 0
        taskMgr.add(self.__checkToonUnderwater, 'ff-check-toon-underwater')
        taskMgr.add(self.__checkCameraUnderwater, 'ff-check-cam-underwater')

    def __checkCameraUnderwater(self, task):
        if camera.getZ(render) < -1.2:
            self.__submergeCamera()
        else:
            self.__emergeCamera()
        return Task.cont

    def __checkToonUnderwater(self, task):
        if base.localAvatar.getZ() < -4.00:
            self.__submergeToon()
        else:
            self.__emergeToon()
        return Task.cont

    def __submergeCamera(self):
        if self.cameraSubmerged == 1:
            return
        base.playSfx(self.loader.underwaterSound, looping=1, volume=0.8)
        self.cameraSubmerged = 1
        self.walkStateData.setSwimSoundAudible(1)

    def __emergeCamera(self):
        if self.cameraSubmerged == 0:
            return
        self.loader.underwaterSound.stop()
        self.cameraSubmerged = 0
        self.walkStateData.setSwimSoundAudible(0)

    def __submergeToon(self):
        if self.toonSubmerged == 1:
            return
        base.playSfx(self.loader.submergeSound)
        if base.config.GetBool('disable-flying-glitch') == 0:
            self.fsm.request('walk')
        self.walkStateData.fsm.request('swimming', [self.loader.swimSound])
        pos = base.localAvatar.getPos(render)
        base.localAvatar.d_playSplashEffect(pos[0], pos[1], -2.3)
        self.toonSubmerged = 1

    def __emergeToon(self):
        if self.toonSubmerged == 0:
            return
        self.walkStateData.fsm.request('walking')
        self.toonSubmerged = 0

    def enterPicnicBasketBlock(self, picnicBasket):
        base.localAvatar.laffMeter.start()
        base.localAvatar.b_setAnimState('off', 1)
        base.localAvatar.cantLeaveGame = 1
        self.accept(self.picnicBasketDoneEvent, self.handlePicnicBasketDone)
        self.trolley = PicnicBasket.PicnicBasket(self, self.fsm, self.picnicBasketDoneEvent, picnicBasket.getDoId(), picnicBasket.seatNumber)
        self.trolley.load()
        self.trolley.enter()

    def exitPicnicBasketBlock(self):
        base.localAvatar.laffMeter.stop()
        base.localAvatar.cantLeaveGame = 0
        self.ignore(self.trolleyDoneEvent)
        self.trolley.unload()
        self.trolley.exit()
        del self.trolley

    def detectedPicnicTableSphereCollision(self, picnicBasket):
        self.fsm.request('picnicBasketBlock', [picnicBasket])

    def handleStartingBlockDone(self, doneStatus):
        self.notify.debug('handling StartingBlock done event')
        where = doneStatus['where']
        if where == 'reject':
            self.fsm.request('walk')
        elif where == 'exit':
            self.fsm.request('walk')
        elif where == 'racetrack':
            self.doneStatus = doneStatus
            messenger.send(self.doneEvent)
        else:
            self.notify.error('Unknown mode: ' + where + ' in handleStartingBlockDone')

    def handlePicnicBasketDone(self, doneStatus):
        self.notify.debug('handling picnic basket done event')
        mode = doneStatus['mode']
        if mode == 'reject':
            self.fsm.request('walk')
        elif mode == 'exit':
            self.fsm.request('walk')
        else:
            self.notify.error('Unknown mode: ' + mode + ' in handlePicnicBasketDone')

    def enterDoorOut(self):
        taskMgr.remove('ff-check-toon-underwater')

    def exitDoorOut(self):
        pass

    def enterDoorIn(self, requestStatus):
        Playground.Playground.enterDoorIn(self, requestStatus)
        taskMgr.add(self.__checkToonUnderwater, 'ff-check-toon-underwater')

    def enterTeleportIn(self, requestStatus):
        self.toonSubmerged = -1
        taskMgr.remove('ff-check-toon-underwater')
        Playground.Playground.enterTeleportIn(self, requestStatus)

    def teleportInDone(self):
        self.toonSubmerged = -1
        taskMgr.add(self.__checkToonUnderwater, 'ff-check-toon-underwater')
        Playground.Playground.teleportInDone(self)

    def enterOff(self):
        return None

    def exitOff(self):
        return None

        