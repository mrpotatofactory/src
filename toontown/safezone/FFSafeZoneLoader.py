from pandac.PandaModules import *
import SafeZoneLoader
import FFPlayground
from direct.fsm import State
from toontown.char import CharDNA
from toontown.char import Char
from toontown.toonbase import ToontownGlobals
from direct.interval.IntervalGlobal import *

class FFSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):
    ALLOW_GEOM_FLATTEN = False
    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = FFPlayground.FFPlayground
        self.musicFile = 'phase_14/audio/bgm/FF_nbrhood.ogg'
        self.activityMusicFile = 'phase_14/audio/bgm/FF_SZ_activity.ogg'
        self.dnaFile = 'phase_14/dna/funny_farm_sz.dna'
        self.safeZoneStorageDNAFile = 'phase_14/dna/storage_FF_sz.dna'
        
    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        self.birdSound = map(base.loadSfx, ['phase_4/audio/sfx/SZ_TC_bird1.ogg',
         'phase_4/audio/sfx/SZ_TC_bird2.ogg', 'phase_4/audio/sfx/SZ_TC_bird3.ogg'])
        water = self.geom.find('**/water')
        water.setTransparency(1)
        water.setColor(1, 1, 1, 0.8)
        self.waterSound = base.loadSfx('phase_6/audio/sfx/SZ_DD_waterlap.ogg')
        self.__startWaterEffect()
        goldenbean = self.createGoldenBean(base.cr.playGame.hood.loader.geom)
        goldenbean.setPosHpr(-130.875,72,0,86.365,0,0)
        self.underwaterSound = base.loadSfx('phase_4/audio/sfx/AV_ambient_water.ogg')
        self.swimSound = base.loadSfx('phase_4/audio/sfx/AV_swim_single_stroke.ogg')
        self.submergeSound = base.loadSfx('phase_5.5/audio/sfx/AV_jump_in_water.ogg')
        self.waterSound = base.loadSfx('phase_6/audio/sfx/SZ_DD_waterlap.ogg')
        base.camLens.setFar(475)

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)
        del self.birdSound
        del self.waterSound
        del self.underwaterSound
        del self.swimSound
        del self.submergeSound
        self.__stopWaterEffect()
        base.camLens.setFar(410)
        
    def createGoldenBean(self, parentId):
        facade = loader.loadModel("phase_3.5/models/modules/facade_bN.bam")
        facade.reparentTo(parentId)
        facade.find('**/showcase').setTwoSided(1)
        goldenbean = loader.loadModel("phase_4/models/props/jellybean4.bam")
        goldenbean.reparentTo(facade)
        goldenbean.setPos(0,-1.5,4)
        goldenbean.setHpr(90,0,0)
        goldenbean.setScale(5)
        goldenbean.setBillboardAxis(1.5);goldenbean.setColor(1,0.9,0)
        glow = loader.loadModel("phase_3.5/models/props/glow.bam")
        glow.reparentTo(facade)
        glow.setPos(0,-1.37,4.1)
        glow.setScale(3)
        glow.setBillboardAxis(1.65)
        glow.setColor(1,0.9,0)
        Sequence(goldenbean.hprInterval(3,Point3(0,0,0),startHpr=Point3(360,0,0)), name="spin").loop()
        return facade
        
    def __startWaterEffect(self):
        waterTop = self.geom.find('**/top_surface*')
        #waterBottom = self.geom.find('**/bottom_surface*')
        water = self.geom.find('**/water*')
        if not water.isEmpty():
            #waterTop.setTexture(loader.loadTexture('phase_4/maps/water3.jpg'), 1)
            #waterBottom.setTexture(loader.loadTexture('phase_4/maps/water3.jpg'), 1)
            topE1 = LerpColorScaleInterval(waterTop, 1.5, (.9,.9,.9,1))
            topE2 = LerpColorScaleInterval(waterTop, 1.5, (1,1,1,1))
            self.waterTopEffect = Sequence(topE1, topE2)
            self.waterTopEffect.loop()
            #bottomE1 = LerpColorScaleInterval(waterBottom, 1.5, (.9,.9,.9,1))
            #bottomE2 = LerpColorScaleInterval(waterBottom, 1.5, (1,1,1,1))
            #self.waterBotEffect = Sequence(bottomE1, bottomE2)
            #self.waterBotEffect.loop()
            ShakeFactor = .25
            waterE1 = water.hprInterval(4, (0,0,ShakeFactor), startHpr=(0,0,-ShakeFactor))
            waterE2 = water.hprInterval(4, (0,0,-ShakeFactor), startHpr=(0,0,ShakeFactor))
            self.waterShake = Sequence(waterE1, Wait(1),  waterE2, Wait(1))
            self.waterShake.loop()
            
    def __stopWaterEffect(self):
        self.waterTopEffect.finish()
        #self.waterBotEffect.finish()
        self.waterShake.finish()
        del self.waterTopEffect, self.waterShake#, self.waterBotEffect
