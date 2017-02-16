from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
import __builtin__, random, os

class LocalizerAgentBase(DirectObject):
    language = None
    
    def startTask(self):
        taskMgr.doMethodLater(2, self.titleTask, 'localizerAgent-titleTask')
        self.titleIndex = 0
        
    def getTitle(self, index):
        return 'Toontown'
    
    def titleTask(self, task):
        self.titleIndex = (self.titleIndex + 1) % 2
        
        wp = WindowProperties()
        wp.setTitle(self.getTitle(self.titleIndex))
        base.win.requestProperties(wp)
        
        return task.again
    
    def getGagshopSign(self):
        return None
    
    def handleHookGSSign(self, geom, flatten=True):
        newSign = self.getGagshopSign()
        if newSign:
            gs = geom.find('**/*_gag_shop_DNARoot')
            if not gs.isEmpty():
                sign = gs.find('**/sign')
                if not sign.isEmpty():
                    newSignNP = loader.loadModel(newSign)
                    newSignNP.reparentTo(sign)
                    newSignNP.wrtReparentTo(sign.getParent())
                    sign.removeNode()
            
        if flatten:
            geom.flattenMedium()
        
    def handleHookGSSignInterior(self, geom):
        newSign = self.getGagshopSign()
        if newSign:
            sign = geom.find('**/sign')
            if not sign.isEmpty():
                newSignNP = loader.loadModel(newSign)
                newSignNP.reparentTo(sign.getParent())
                newSignNP.setPos(3, 28, 0)
                newSignNP.setH(180)
                newSignNP.setScale(.4)
                sign.removeNode()

    def findDNA(self, file):
        dir, filename = os.path.split(str(file))
        searchPath = DSearchPath()

        #searchPath.appendDirectory(Filename('resources/' + dir))
        searchPath.appendDirectory(Filename('../resources/' + dir))
            
        dnaFile = Filename(filename)
        return self._doFind(dnaFile, searchPath)
        
    def _doFind(self, filename, searchPath):
        if not vfs.resolveFilename(filename, searchPath):
            raise IOError('Could not find %s' % filename)
            
        return filename
        
    def getAd(self):
        return None

class LocalizerAgentEN(LocalizerAgentBase):
    language = 'english'
    
class LocalizerAgentLeet(LocalizerAgentBase):
    language = 'leet'
    
    def getTitle(self, index):
        return ('Toontown', 'To0n10wn')[index]

class LocalizerAgentYolo(LocalizerAgentBase):
    language = 'yolo'
    
    def getTitle(self, index):
        return ('Toontown', random.choice(['yolo', 'swag']))[index]
        
class LocalizerAgentPT(LocalizerAgentBase):
    language = 'portuguese'
    
    def getGagshopSign(self):
        return 'phase_3.5/pt/GS_pt_sign'
        
    def findDNA(self, file):
        dir, filename = os.path.split(str(file))
        searchPath = DSearchPath()
                
        #searchPath.appendDirectory(Filename('resources/phase_3.5/pt/dna'))
        searchPath.appendDirectory(Filename('../resources/phase_3.5/pt/dna'))
        searchPath.appendDirectory(Filename('../resources/' + dir))
            
        dnaFile = Filename(filename)
        return self._doFind(dnaFile, searchPath)
       
    def getAd(self):
        root = NodePath('ad_root')
        
        logo = root.attachNewNode(CardMaker('ad').generate())
        logo.setTexture(loader.loadTexture('phase_7/maps/ptad.png'))
        logo.setTransparency(1)
        logo.setScale(.5)
        
        tn = TextNode('adtext')
        tn.setText('www.computerspace.com.br')
        tn.setTextColor(0, 0, 0, 1)
        tn.setTextScale(.05)
        text = root.attachNewNode(tn)
        text.setZ(-.06)
        text.setSx(text, .7)
        
        return root
        
def install(lang):
    if lang == 'english':
        __builtin__.localizerAgent = LocalizerAgentEN()
        
    elif lang == 'portuguese':
        __builtin__.localizerAgent = LocalizerAgentPT()
        
    elif lang == 'leet':
        __builtin__.localizerAgent = LocalizerAgentLeet()
        
    elif lang == 'yolo':
        __builtin__.localizerAgent = LocalizerAgentYolo()
        
    else:
        print 'WARNING: Cannot find LocalizerAgent for', lang
        __builtin__.localizerAgent = LocalizerAgentEN()
        