import random
import ToonInteriorColors
import ToonInteriorTextures
import DistributedToonInterior
from direct.distributed.DistributedObject import DistributedObject
from toontown.dna.DNAParser import *
from toontown.hood import ZoneUtil
from toontown.toon.DistributedNPCToonBase import DistributedNPCToonBase
from toontown.hood import SkyUtil
from toontown.toonbase.ToontownGlobals import *
from toontown.toonbase.ToonBaseGlobal import *


class DistributedBankInterior(DistributedToonInterior.DistributedToonInterior):
 
    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.randomGenerator = None
        self.setup()
 
    def setup(self):
        self.dnaStore = base.cr.playGame.dnaStore
        for npc in self.cr.doFindAllInstances(DistributedNPCToonBase):
            npc.initToonState()
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        self.interior = loader.loadModel('phase_4/models/modules/bank_interior.bam')
        self.interior.reparentTo(render)
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.textures = ToonInteriorTextures.textures[hoodId]
        self.colors = ToonInteriorColors.colors[hoodId]
        self.replaceRandomInModel(self.interior)
        self.setupBankFOV()
        self.chooseDoor()
        self.setupBankSky()
        self.setupBankInteriorModels()
        del self.colors
        del self.dnaStore
        del self.randomGenerator
        self.interior.flattenMedium()
 
    def replaceRandomInModel(self, model):
        baseTag = 'random_'
        npc = model.findAllMatches('**/' + baseTag + '???_*')
        for i in xrange(npc.getNumPaths()):
            np = npc.getPath(i)
            name = np.getName()
            b = len(baseTag)
            category = name[b + 4:] #strips 'random_***_' from string leaving only 'catagory'
            key1 = name[b] #key1 == first char after 'random_'
            key2 = name[b + 1] #key2 == second char after 'random_'
            if key1 == 'm': #'m' == model
                model = self.randomDNAItem(category, self.dnaStore.findNode)
                newNP = model.copyTo(np)
                if key2 == 'r': #'r' == Cycles through this sub again to replace random_*** that is in the model itself
                    self.replaceRandomInModel(newNP)
            elif key1 == 't': #'t' == is a texture
                texture = self.randomGenerator.choice(self.textures[category])
                np.setTexture(loader.loadTexture(texture), 100)
                newNP = np
                if key2 == 'c': #'c' == signifies the random  replacement of texture
                    if category == 'TI_wallpaper' or category == 'TI_wallpaper_border':
                        self.randomGenerator.seed(self.zoneId)
                        newNP.setColorScale(self.randomGenerator.choice(self.colors[category]))
                    else:
                        newNP.setColorScale(self.randomGenerator.choice(self.colors[category]))
 
    def randomDNAItem(self, category, findFunc):
        codeCount = self.dnaStore.getNumCatalogCodes(category)
        index = self.randomGenerator.randint(0, codeCount - 1)
        code = self.dnaStore.getCatalogCode(category, index)
        return findFunc(code)
    
    def setZoneIdAndBlock(self, zoneId, block):
        self.zoneId = zoneId
        self.block = block

    def chooseDoor(self):
        doorModelName = 'door_double_round_ul'
        if doorModelName[-1:] == 'r':
            doorModelName = doorModelName[:-1] + 'l'
        else:
            doorModelName = doorModelName[:-1] + 'r'
        door = self.dnaStore.findNode(doorModelName)
        #return door
        door_origin = render.find('**/door_origin;+s')
        doorNP = door.copyTo(door_origin)
        door_origin.setScale(0.8, 0.8, 0.8)
        door_origin.setPos(door_origin, 0, -0.025, 0)
        color = self.randomGenerator.choice(self.colors['TI_door'])
        DNADoor.setupDoor(doorNP, self.interior, door_origin, self.dnaStore, self.block + 500, color)
        doorFrame = doorNP.find('door_*_flat')
        doorFrame.wrtReparentTo(self.interior)
        doorFrame.setColor(color)

    def setupBankSky(self):
        self.bankSkyFile = 'phase_3.5/models/props/TT_sky'
        self.bankSky = loader.loadModel(self.bankSkyFile)
        sky = self.bankSky
        self.bankSky.setPos(0, 0, 0)
        self.bankSky.setScale(0.5, .5, 2.5)
        self.startBankSky()

    def startBankSky(self):
        SkyUtil.startBankSky(self)
    
    def bankSkyTrack(self, task):
        return SkyUtil.bankCloudSkyTrack(task)

    def stopSky(self):
        taskMgr.remove('bankSkyTrack')
        self.bankSky.removeNode()

    def __cleanupSky(self):
        sky = self.bankSky
        sky.setH(0)
        sky.setZ(0)
        self.stopSky()

    def setupBankInteriorModels(self):
        self.barriers = loader.loadModel('phase_4/models/modules/bank_int_barrier_set.bam')
        self.barriers.wrtReparentTo(self.interior)
        self.replaceRandomInModel(self.barriers)
        
        self.signsModel = loader.loadModel('phase_4/models/props/newSigns.bam')
        self.enterSign = self.signsModel.find('**/signArrowEnter_Lt')
        # self.otherSigns = self.signsModel.findAllMatches('**/*sign*')
        # for sign in range(0, self.otherSigns.getNumPaths()):
          # np = self.otherSigns.getPath(sign)
          # if np != self.enterSign:
              # self.otherSigns.getPath(sign).removeNode()
        self.enterSign.wrtReparentTo(self.interior)
        self.enterSign.setPos (6.82, -18.6, 0.15)
        self.enterSign.setHpr ( -40.24, 0, 0 )
        
        self.atm_machine = loader.loadModel('phase_4/models/props/atm_machine.bam')
        self.atm_machine.wrtReparentTo(self.interior)
        self.atm_machine.setPos (-27.74702853, 7.839149475, 0)
        self.atm_machine.setHpr ( 0, 0, 0 )
        
        self.phone = loader.loadModel('phase_4/models/props/phone.bam')
        self.phone.wrtReparentTo(self.interior)
        self.phone.setPos (21, 5.867, 3.018)
        self.phone.setHpr ( 270, 0, 0 )
        

    def deleteBankInteriorModels(self):
        self.barriers.removeNode()
        del self.barriers
        self.signsModel.removeNode()
        del self.signsModel
        self.atm_machine.removeNode()
        del self.atm_machine
        self.phone.removeNode()
        del self.phone

    def setupBankFOV(self):
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear, 1500)
        
    def restoreFOV(self):
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear, ToontownGlobals.DefaultCameraFar)
    
    def disable(self):
        self.restoreFOV()
        self.deleteBankInteriorModels()
        self.interior.removeNode()
        del self.interior
        self.__cleanupSky()
        del self.bankSky
        DistributedObject.disable(self)
 
    
