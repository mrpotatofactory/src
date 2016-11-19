from pandac.PandaModules import *
from toontown.toonbase.ToonBaseGlobal import *
from DistributedMinigame import *
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from toontown.toonbase import TTLocalizer, ToontownGlobals
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from toontown.toonbase import ToontownTimer
from toontown.toon import ToonHeadFrame

import FADToon, FADDoodle

class DistributedFADGame(DistributedMinigame):
    TIME = 80
    DISTANCE_AVATARS = 6.0
    def __init__(self, cr):
        DistributedMinigame.__init__(self, cr)
        self.gameFSM = ClassicFSM.ClassicFSM('DistributedFADGame', [State.State('off', self.enterOff, self.exitOff, ['play']), State.State('play', self.enterPlay, self.exitPlay, ['cleanup']), State.State('cleanup', self.enterCleanup, self.exitCleanup, [])], 'off', 'cleanup')
        self.addChildGameFSM(self.gameFSM)
        self.fadToons = {}
        self.fadDoodles = {}
        self.otherFeed = {}
        self.otherScores = {}
        self.blinkFeedIv = None
        self.scores = {}
        
    def enterOff(self):
        pass
    def exitOff(self):
        pass
    def enterCleanup(self):
        pass
    def exitCleanup(self):
        pass

    def getTitle(self):
        return TTLocalizer.MinigameFADTitle

    def getInstructions(self):
        return TTLocalizer.MinigameFADInstructions

    def getMaxDuration(self):
        return self.TIME + 3

    def load(self):
        DistributedMinigame.load(self)
        self.sky = loader.loadModel('phase_3.5/models/props/TT_sky')
        self.environment = loader.loadModel('phase_6/models/golf/hole1.bam')
        self.environment.find('**/golfGreen1*').removeNode()
        self.environment.reparentTo(render)
        self.clockSfx1 = base.loadSfx('phase_4/audio/sfx/clock09.mp3')
        self.clockSfx2 = base.loadSfx('phase_4/audio/sfx/AA_sound_whistle.mp3')
        feedBt = loader.loadModel('phase_4/models/gui/cannon_game_gui')
        feedBtGeom = (feedBt.find('**/Fire_Btn_UP'), feedBt.find('**/Fire_Btn_DN'), feedBt.find('**/Fire_Btn_RLVR'), feedBt.find('**/Fire_Btn_DN'))
        self.feedButton = DirectButton(parent=hidden, relief=None, geom=feedBtGeom, command=self.__handleFeedButton)
        self.feedButton.setPos(-0.320,0,0.340)
        self.intervalMeter = DirectWaitBar(parent=hidden, value=100, borderWidth = (0.040,0.040))
        self.intervalMeter.setScale(0.3,1,0.5)
        self.intervalMeter.setPos(-0.320,0,0.165)
        
        self.timer = ToontownTimer.ToontownTimer()
        self.timer.posInTopRightCorner()
        self.timer.hide()

    def unload(self):
        self.notify.debug('unload')
        DistributedMinigame.unload(self)
        self.removeChildGameFSM(self.gameFSM)
        del self.gameFSM
        self.sky.removeNode()
        self.environment.removeNode()
        self.feedButton.removeNode()
        self.intervalMeter.removeNode()
        self.timer.destroy()
        del self.sky, self.environment, self.feedButton, self.intervalMeter
        del self.timer
        for panel in self.scores.values():
            panel.removeNode()

    def onstage(self):
        self.notify.debug('onstage')
        self.sky.reparentTo(render)
        self.environment.reparentTo(render)
        camera.reparentTo(render)
        camera.setPos(0,16,10)
        camera.setHpr(180,-20,0)
        base.transitions.irisIn(0.4)
        self.camIntroInterval = Sequence(
            camera.posInterval(5, (18,16,10)),
            camera.posInterval(5, (9,28,13)),
        )
        self.camIntroInterval.start()

    def offstage(self):
        self.notify.debug('offstage')
        self.sky.reparentTo(hidden)
        self.environment.reparentTo(hidden)
        self.camIntroInterval.finish()
        if self.blinkFeedIv:
            self.blinkFeedIv.finish()
        camera.setPosHpr(0,0,0,0,0,0)
        for avId in self.avIdList:
            av = self.getAvatar(avId)
            if av:
                av.resetLOD()
        for ival in self.otherFeed.values():
            ival.finish()
        for doodle in self.fadDoodles.values():
            doodle.cleanup()
            doodle.removeNode()
        self.feedIval.finish()
        taskMgr.remove('resetBarTask')
        for toon in self.fadToons.values():
            toon.stopAll()
        
    def setGameReady(self):
        if not self.hasLocalToon:
            return
        if DistributedMinigame.setGameReady(self):
            return
        for avId in self.avIdList:
            av = self.getAvatar(avId)
            av.reparentTo(render)
            av.setPosHpr(0,0,0,0,0,0)
            av.setX(self.DISTANCE_AVATARS * self.avIdList.index(avId))
            av.setH(180)
            av.useLOD('1000')
            av.loop('neutral')
            toon = FADToon.FADToon(av)
            self.fadToons[avId] = toon
            
            doodle = FADDoodle.FADDoodle()
            doodle.makeRandomPet() # TODO: USE PLAYER's PET IF AVAILABLE
            doodle.reparentTo(render)
            doodle.setX(self.DISTANCE_AVATARS * self.avIdList.index(avId))
            doodle.setY(-15)
            doodle.loop('neutral')
            self.fadDoodles[avId] = doodle
        hpn = loader.loadModel('phase_6/models/golf/headPanel')
        for avId in self.avIdList:
            av = self.getAvatar(avId)
            scorePanel = ToonHeadFrame.ToonHeadFrame(av, g = hpn)
            scorePanel.reparentTo(hidden)
            scorePanel.setPos(0.2, 0, 0.2 + (0.4 * self.avIdList.index(avId)))
            scorePanel.setScale(0.3, 1, 0.7)
            scorePanel.head.setPos(0, 10, 0.18)
            scorePanel.head.setScale(0.47, 0.2, 0.2)
            scorePanel.tag1.setPos(0.3, 10, 0.18)
            scorePanel.tag1.setScale(0.1283, 0.055, 0.055)
            scorePanel.tag2.setPos(0, 10, 0.43)
            scorePanel.tag2.setScale(0.117, 0.05, 0.05)
            scorePanel['text'] = '0'
            scorePanel['text_scale'] = (0.220,0.100,0.2)
            scorePanel['text_font'] = ToontownGlobals.getSignFont()
            scorePanel['text_fg'] = Vec4(1,1,0,1)
            scorePanel['text_pos'] = (0,-0)
            self.scores[avId] = scorePanel

    def setGameStart(self, timestamp):
        if not self.hasLocalToon:
            return
        self.notify.debug('setGameStart')
        DistributedMinigame.setGameStart(self, timestamp)
        self.camIntroInterval.finish()
        self.gameFSM.request('play')

    def enterPlay(self):
        self.notify.debug('enterPlay')
        camera.setPos(-12,-30,10)
        camera.setHpr(-38,-15,0)
        
        doodlesWalkP = Parallel()
        for doodle in self.fadDoodles.values():
            doodlesWalkP.append(Parallel(
                Func(doodle.loop, 'walk'),
                doodle.posInterval(3, (doodle.getX(),-10,0))
                )
            )
        def ra(): 
            for d in self.fadDoodles.values(): d.loop('neutral')
            
        self.countdownText = OnscreenText(
            text = '3',
            font = ToontownGlobals.getSignFont(),
            fg = (0,1,0,1),
            scale = 0.8
        )
        def resetCt():
            self.countdownText.setText(str(int(self.countdownText.getText()) - 1))
            self.countdownText.setScale(0.8)
            self.countdownText.setColorScale(1,1,1,1)
            self.clockSfx1.play()
        countdownSeq = Sequence(
            Func(self.clockSfx1.play),
            Parallel(LerpScaleInterval(self.countdownText, 1, 1.6), LerpColorScaleInterval(self.countdownText, 1, (0,0,0,0))),
            Func(resetCt),
            Func(self.countdownText.node().setTextColor, Vec4(1,1,0,1)),
            Parallel(LerpScaleInterval(self.countdownText, 1, 1.3), LerpColorScaleInterval(self.countdownText, 1, (0,0,0,0))),
            Func(resetCt),
            Func(self.countdownText.node().setTextColor, Vec4(1,0,0,1)),
            Parallel(LerpScaleInterval(self.countdownText, 1, 1), LerpColorScaleInterval(self.countdownText, 1, (0,0,0,0))),
            Func(self.clockSfx2.play)
        )
        self.introSeq = Sequence(
            Func(countdownSeq.start),
            Func(doodlesWalkP.start),
            Wait(doodlesWalkP.getDuration() / 2),
            Func(self.setCameraInToon),
            Wait(doodlesWalkP.getDuration() / 2),
            Func(ra),
            Func(self.beginGame)
        )
        self.introSeq.start()
        
    def setCameraInToon(self):
        camera.reparentTo(localAvatar)
        camera.setPosHpr(0,-10,9,0,-25,0)
        
    def __handleFeedButton(self):
        if self.intervalMeter['value'] >= 100:
            if self.blinkFeedIv:
                self.blinkFeedIv.finish()
                self.blinkFeedIv = None
            self.intervalMeter['value'] = 0
            self.feedButton['state'] = DGG.DISABLED
            self.feedIval = self.fadToons[localAvatar.doId].feedDoodle(self.fadDoodles[localAvatar.doId])
            self.feedIval.start()
            taskMgr.add(self.__resetBarTask, 'resetBarTask')
            self.__serverRequestFeedBroadcast()
            
    def __resetBarTask(self, task):
        if self.intervalMeter['value'] >= 100:
            self.__serverRequestUpdateScore()
            self.feedButton['state'] = DGG.NORMAL
            self.blinkFeedButton()
            return task.done
        self.intervalMeter['value'] = ((self.feedIval.getT() * 100) / self.feedIval.getDuration())
        return task.again
        
    def beginGame(self):
        for sPanel in self.scores.values():
            sPanel.reparentTo(base.a2dBottomLeft)
        self.feedButton.reparentTo(base.a2dBottomRight)
        self.intervalMeter.reparentTo(base.a2dBottomRight)
        self.blinkFeedButton()
        self.timer.show()
        self.timer.countdown(self.TIME, self.__countdownExpired)
        
    def blinkFeedButton(self):
        self.blinkFeedIv = Sequence(
            self.feedButton.scaleInterval(0.4, (1.2)),
            self.feedButton.scaleInterval(0.2, (1)),
            Wait(0.4)
        )
        self.blinkFeedIv.loop()
        
    def __countdownExpired(self):
        self.gameOver()

    def exitPlay(self):
        pass
            
        
    def __serverRequestFeedBroadcast(self):
        self.sendUpdate('requestFeedBroadcast')
        
    def broadcastFeed(self, avId):
        if avId in self.avIdList and avId != localAvatar.doId:
            self.otherFeed[avId] = self.fadToons[avId].feedDoodle(self.fadDoodles[avId])
            self.otherFeed[avId].start()
        
    def __serverRequestUpdateScore(self):
        self.sendUpdate('requestUpdateScore')
        
    def broadcastScore(self, avId, newScore):
        if avId in self.avIdList:
            self.scores[avId]['text'] = str(newScore)
                
    def handleDisabledAvatar(self, avId):
        self.otherFeed[avId].finish()
        self.fadToons[avId].stopAll()
        self.fadDoodles[avId].cleanup()
        self.fadDoodles[avId].removeNode()
        del self.otherFeed[avId], self.fadToons[avId], self.fadDoodles[avId], self.otherScores[avId]
        DistributedMinigame.handleDisabledAvatar(self, avId)