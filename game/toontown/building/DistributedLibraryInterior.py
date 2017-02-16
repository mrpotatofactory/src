import random
import ToonInteriorColors
import ToonInteriorTextures
import DistributedToonInterior
from direct.distributed.DistributedObject import DistributedObject
from toontown.dna.DNAParser import DNADoor
from toontown.hood import ZoneUtil
from toontown.toon.DistributedNPCToonBase import DistributedNPCToonBase
 
class DistributedLibraryInterior(DistributedToonInterior.DistributedToonInterior):
 
    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.setup()
 
    def setup(self):
        self.dnaStore = base.cr.playGame.dnaStore
        for npc in self.cr.doFindAllInstances(DistributedNPCToonBase):
            npc.initToonState()
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        self.interior = loader.loadModel('phase_4/models/modules/library_interior.bam')
        self.interior.reparentTo(render)
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.textures = ToonInteriorTextures.textures[hoodId]
        self.colors = ToonInteriorColors.colors[hoodId]
        self.replaceRandomInModel(self.interior)
        doorModelName = 'door_double_round_ul'
        if doorModelName[-1:] == 'r':
            doorModelName = doorModelName[:-1] + 'l'
        else:
            doorModelName = doorModelName[:-1] + 'r'
        door = self.dnaStore.findNode(doorModelName)
        door_origin = render.find('**/door_origin;+s')
        doorNP = door.copyTo(door_origin)
        door_origin.setScale(0.8, 0.8, 0.8)
        door_origin.setPos(door_origin, 0, -0.025, 0)
        color = self.randomGenerator.choice(self.colors['TI_door'])
        DNADoor.setupDoor(doorNP, self.interior, door_origin, self.dnaStore, self.block + 500, color)
        doorFrame = doorNP.find('door_*_flat')
        doorFrame.wrtReparentTo(self.interior)
        doorFrame.setColor(color)
 
    def replaceRandomInModel(self, model):
        baseTag = 'random_'
        npc = model.findAllMatches('**/' + baseTag + '???_*')
        for i in xrange(npc.getNumPaths()):
            np = npc.getPath(i)
            name = np.getName()
            b = len(baseTag)
            category = name[b + 4:]
            key1 = name[b]
            key2 = name[b + 1]
            if key1 == 'm':
                model = self.randomDNAItem(category, self.dnaStore.findNode)
                newNP = model.copyTo(np)
                if key2 == 'r':
                    self.replaceRandomInModel(newNP)
            elif key1 == 't':
                texture = self.randomGenerator.choice(self.textures[category])
                np.setTexture(loader.loadTexture(texture), 100)
                newNP = np
            if key2 == 'c':
                if category == 'TI_wallpaper' or category == 'TI_wallpaper_border':
                    self.randomGenerator.seed(self.zoneId)
                    newNP.setColorScale(self.randomGenerator.choice(self.colors[category]))
                else:
                    newNP.setColorScale(self.randomGenerator.choice(self.colors[category]))
 
    def disable(self):
        DistributedObject.disable(self)
        self.interior.removeNode()
        del self.interior
 
    def setZoneIdAndBlock(self, zoneId, block):
        self.zoneId = zoneId
        self.block = block