from pandac.PandaModules import *
import SafeZoneLoader
import DGPlayground
from toontown.toonbase import ToontownGlobals

class DGSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = DGPlayground.DGPlayground
        self.musicFile = 'phase_8/audio/bgm/DG_nbrhood.ogg'
        self.activityMusicFile = 'phase_8/audio/bgm/DG_SZ.ogg'
        self.dnaFile = 'phase_8/dna/daisys_garden_sz.dna'
        self.safeZoneStorageDNAFile = 'phase_8/dna/storage_DG_sz.dna'

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        if base.cr.newsManager:
            holidayIds = base.cr.newsManager.getDecorationHolidayId()
            if ToontownGlobals.HALLOWEEN_COSTUMES in holidayIds:
                self.birdSound = map(base.loadSfx, ['phase_4/audio/sfx/SZ_TC_owl1.ogg', 'phase_4/audio/sfx/SZ_TC_owl2.ogg', 'phase_4/audio/sfx/SZ_TC_owl3.ogg'])
            else:
                self.birdSound = map(base.loadSfx, ['phase_8/audio/sfx/SZ_DG_bird_01.ogg', 'phase_8/audio/sfx/SZ_DG_bird_02.ogg', 'phase_8/audio/sfx/SZ_DG_bird_03.ogg', 'phase_8/audio/sfx/SZ_DG_bird_04.ogg'])

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)
        del self.birdSound

    def enter(self, requestStatus):
        SafeZoneLoader.SafeZoneLoader.enter(self, requestStatus)

    def exit(self):
        SafeZoneLoader.SafeZoneLoader.exit(self)
