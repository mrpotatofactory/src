from direct.distributed.ClockDelta import globalClockDelta
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from pandac.PandaModules import Vec4

from otp.ai.MagicWordGlobal import *
from toontown.event import ExperimentEventObjectives
from toontown.event.DistributedEvent import DistributedEvent
from toontown.event.ExperimentBlimp import ExperimentBlimp
from toontown.event.ExperimentEventObjectiveGUI import ExperimentEventObjectiveGUI


class DistributedExperimentEvent(DistributedEvent):
    notify = directNotify.newCategory('DistributedExperimentEvent')

    def __init__(self, cr):
        DistributedEvent.__init__(self, cr)

        self.introMusic = base.loadMusic('phase_4/audio/bgm/TE_battle_intro.ogg')
        self.music = base.loadMusic('phase_4/audio/bgm/TE_battle.ogg')
        self.musicSequence = None

        self.blimp = None

        self.objectiveGui = None

    def start(self):
        self.requestExperimentToon()

        taskMgr.remove('TT-birds')

        base.musicManager.stopAllSounds()
        base.lockMusic()

        self.musicSequence = Sequence(
            Func(base.playMusic, self.introMusic, looping=0, volume=1, playLocked=True),
            Wait(self.introMusic.length()),
            Func(base.playMusic, self.music, looping=1, volume=1, playLocked=True))
        self.musicSequence.start()

        self.cr.playGame.hood.startSpookySky()
        render.setColorScale(Vec4(0.40, 0.40, 0.60, 1))
        aspect2d.setColorScale(Vec4(0.40, 0.40, 0.60, 1))

    def delete(self):
        DistributedEvent.delete(self)

        self.musicSequence.finish()
        self.musicSequence = None

        if self.blimp is not None:
            self.blimp.cleanup()
            self.blimp = None

        if self.objectiveGui:
            self.objectiveGui.destroy()

        base.musicManager.stopAllSounds()
        base.unlockMusic()

        self.cr.playGame.hood.startSky()
        render.setColorScale(Vec4(1, 1, 1, 1))
        aspect2d.setColorScale(Vec4(1, 1, 1, 1))

    def setVisGroups(self, visGroups):
        self.cr.sendSetZoneMsg(self.zoneId, visGroups)

    def createBlimp(self, timestamp):
        self.blimp = ExperimentBlimp()
        self.blimp.reparentTo(render)
        self.blimp.setPosHpr(144, -188, 55, 140, 0, 5)
        self.blimp.startFlying(timestamp)
        self.blimp.request('Phase0', timestamp)

    def setObjective(self, objectiveId):
        if objectiveId == 0:
            self.completeObjective()
            return

        objectiveInfo = ExperimentEventObjectives.getObjectiveInfo(objectiveId)
        self.objectiveGui = ExperimentEventObjectiveGUI(*objectiveInfo)
        self.objectiveGui.setPos(0, 0, 0.8)
        self.objectiveGui.fadeIn()

    def setObjectiveCount(self, count):
        if self.objectiveGui:
            self.objectiveGui.updateProgress(count)

    def completeObjective(self):
        if self.objectiveGui:
            self.objectiveGui.fadeOutDestroy()
            self.objectiveGui = None

    def setExperimentToon(self, avId):
        base.localAvatar.altDoId = avId
        self.cr.doId2do[avId] = base.localAvatar
        base.localAvatar.dclass = self.cr.dclassesByName['DistributedExperimentToon']

        self.sendUpdate('setExperimentToonResponse', [avId])

    def requestExperimentToon(self):
        self.sendUpdate('requestExperimentToon', [base.localAvatar.doId])


@magicWord(category=CATEGORY_PROGRAMMER, types=[int])
def blimp(phase):
    if not (0 <= phase <= 3):
        return 'Invalid phase.'
    for event in base.cr.doFindAllInstances(DistributedExperimentEvent):
        event.blimp.request('Phase%d' % phase, globalClockDelta.getRealNetworkTime(bits=32))
        break
    else:
        return "Couldn't find a blimp."