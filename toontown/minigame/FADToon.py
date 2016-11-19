from direct.interval.IntervalGlobal import *
from panda3d.core import *

class FADToon:
    def __init__(self, avatar):
        self.avatar = avatar
        self.jellybean = loader.loadModel('phase_4/models/props/jellybean4')
        self.throwSfx = base.loadSfx('phase_6/audio/sfx/KART_getGag.mp3')
        self.eatSfx = base.loadSfx('phase_5.5/audio/sfx/beg_eat_swallow.mp3')
        self.eatSfx.setTime(6.0)
        
    def feedDoodle(self, doodle):
        endThrowPos = Vec3(*doodle.getPos())
        endThrowPos.setZ(1.0)
        throwJbTrack = Sequence(
            Func(base.playSfx, self.throwSfx, node = self.avatar),
            Func(doodle.loop, 'beg'),
            ProjectileInterval(self.jellybean, endPos = endThrowPos, duration = 1.5),
            Func(self.resetJellybean),
            Func(base.playSfx, self.eatSfx, time = 6.0, node = doodle),
            ActorInterval(doodle, 'fromBeg'),
            ActorInterval(doodle, 'eat', playRate = 2.0, endFrame = doodle.getNumFrames('eat') - 30),
            Func(self.eatSfx.stop),
            Func(doodle.loop, 'neutral')
        )
        otherSeq = Sequence(Wait(self.avatar.getDuration('feedPet')), Func(self.avatar.loop, 'neutral'))
        feedTrack = Sequence(
            Func(self.avatar.play, 'feedPet'),
            Func(otherSeq.start),
            Func(self.attachJellybean),
            Wait(2.3),
            Func(self.attachJellybeanToRenderSpace),
            throwJbTrack,
        )
        return feedTrack
        
    def stopAll(self):
        self.jellybean.removeNode()
        self.jellybean = None
        
    def attachJellybean(self):
        if self.jellybean:
            self.jellybean.reparentTo(self.avatar.rightHand)
            self.jellybean.setP(90)
            self.jellybean.setScale(1.1)
            self.jellybean.setX(0.1)
        
    def attachJellybeanToRenderSpace(self):
        if self.jellybean:
            self.jellybean.reparentTo(render)
            self.jellybean.setPos(self.avatar.rightHand, 0, 0, 0)
            self.jellybean.setH(90)
        
    def resetJellybean(self):
        if self.jellybean:
            self.jellybean.reparentTo(hidden)
            self.jellybean.setPosHprScale(0,0,0,0,0,0,0,0,0)