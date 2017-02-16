from pandac.PandaModules import *
from pandac.PandaModules import *
from direct.directnotify import DirectNotifyGlobal
from direct.showbase.ShadowPlacer import ShadowPlacer
from direct.showbase.ShadowDemo import Task, ShadowCaster as DirectShadowCaster
from otp.otpbase import OTPGlobals
from toontown.toonbase import Settings
globalDropShadowFlag = 1

def setGlobalDropShadowFlag(flag):
    global globalDropShadowFlag
    if flag != globalDropShadowFlag:
        globalDropShadowFlag = flag
        messenger.send('globalDropShadowFlagChanged')


globalDropShadowGrayLevel = 0.5

def setGlobalDropShadowGrayLevel(grayLevel):
    global globalDropShadowGrayLevel
    if grayLevel != globalDropShadowGrayLevel:
        globalDropShadowGrayLevel = grayLevel
        messenger.send('globalDropShadowGrayLevelChanged')


class ShadowCaster:
    notify = DirectNotifyGlobal.directNotify.newCategory('ShadowCaster')
    WantDecentShadow = config.GetBool('want-decent-shadow', False)

    def __init__(self, squareShadow = False):
        if squareShadow:
            self.shadowFileName = 'phase_3/models/props/square_drop_shadow'
        else:
            self.shadowFileName = 'phase_3/models/props/drop_shadow'
        self.dropShadow = None
        self.shadowPlacer = None
        self.activeShadow = 0
        self.wantsActive = 1
        self.storedActiveState = 0
        if hasattr(base, 'wantDynamicShadows') and base.wantDynamicShadows:
            messenger.accept('globalDropShadowFlagChanged', self, self.__globalDropShadowFlagChanged)
            messenger.accept('globalDropShadowGrayLevelChanged', self, self.__globalDropShadowGrayLevelChanged)
        
        self.sc = None
        self.shadowTaskName = 'shadow-task-%x' % id(self)
        messenger.accept('SHADOWS_SETTINGS_CHANGED', self, self.__shadowSettingsChanged)
        self.initDecentShadow()
        
    def __shadowSettingsChanged(self, value):
        self.deleteDropShadow()
        self.initializeDropShadow()

    def delete(self):
        if hasattr(base, 'wantDynamicShadows') and base.wantDynamicShadows:
            messenger.ignore('globalDropShadowFlagChanged', self)
            messenger.ignore('globalDropShadowGrayLevelChanged', self)
        messenger.ignore('SHADOWS_SETTINGS_CHANGED', self)
        self.deleteDropShadow()
        self.shadowJoint = None

    def initializeDropShadow(self, hasGeomNode = True):
        self.deleteDropShadow()
        self.setBin('fixed', 25)
        if hasGeomNode:
            self.getGeomNode().setTag('cam', 'caster')
        dropShadow = loader.loadModel(self.shadowFileName)
        dropShadow.setScale(0.4)
        dropShadow.flattenMedium()
        dropShadow.setBillboardAxis(2)
        dropShadow.setColor(0.0, 0.0, 0.0, globalDropShadowGrayLevel, 1)
        self.shadowPlacer = ShadowPlacer(base.shadowTrav, dropShadow, OTPGlobals.WallBitmask, OTPGlobals.FloorBitmask)
        self.dropShadow = dropShadow
        if not globalDropShadowFlag:
            self.dropShadow.hide()
        if self.getShadowJoint():
            dropShadow.reparentTo(self.getShadowJoint())
        else:
            self.dropShadow.hide()
        self.setActiveShadow(self.wantsActive)
        self.__globalDropShadowFlagChanged()
        self.__globalDropShadowGrayLevelChanged()
        self.initDecentShadow()

    def update(self):
        pass

    def deleteDropShadow(self):
        if self.shadowPlacer:
            self.shadowPlacer.delete()
            self.shadowPlacer = None
        if self.dropShadow:
            self.dropShadow.removeNode()
            self.dropShadow = None
        if self.sc:
            self.sc.clear()
            self.sc = None
            taskMgr.remove(self.shadowTaskName)

    def setActiveShadow(self, isActive = 1):
        isActive = isActive and self.wantsActive
        if not globalDropShadowFlag:
            self.storedActiveState = isActive
        if self.shadowPlacer != None:
            isActive = isActive and globalDropShadowFlag
            if self.activeShadow != isActive:
                self.activeShadow = isActive
                if isActive:
                    self.shadowPlacer.on()
                else:
                    self.shadowPlacer.off()
        return

    def setShadowHeight(self, shadowHeight):
        if self.dropShadow:
            self.dropShadow.setZ(-shadowHeight)

    def getShadowJoint(self):
        if hasattr(self, 'shadowJoint'):
            return self.shadowJoint
        shadowJoint = self.find('**/attachShadow')
        if shadowJoint.isEmpty():
            self.shadowJoint = NodePath(self)
        else:
            self.shadowJoint = shadowJoint
        return self.shadowJoint

    def hideShadow(self):
        self.dropShadow.hide()

    def showShadow(self):
        if not globalDropShadowFlag:
            self.dropShadow.hide()
        else:
            self.dropShadow.show()

    def __globalDropShadowFlagChanged(self):
        if self.dropShadow != None:
            if globalDropShadowFlag == 0:
                if self.activeShadow == 1:
                    self.storedActiveState = 1
                    self.setActiveShadow(0)
            elif self.activeShadow == 0:
                self.setActiveShadow(1)
            self.showShadow()
        return

    def __globalDropShadowGrayLevelChanged(self):
        if self.dropShadow != None:
            self.dropShadow.setColor(0.0, 0.0, 0.0, globalDropShadowGrayLevel, 1)
        return

    def initDecentShadow(self):
        try:
            objectPath = self.getGeomNode()
            if not objectPath:
                objectPath = self
            
        except:
            objectPath = self

        if self.sc:
            self.sc.clear()
            shadowCamera = objectPath.find('**/shadowCamera')
            if shadowCamera:
                shadowCamera.removeNode()
            
        if self.dropShadow:
            self.dropShadow.stash()
        
        shadowCamera = objectPath.attachNewNode('shadowCamera')
        lightPath = shadowCamera.attachNewNode('lightPath')
        # TO DO: Day-night system to fix angle
        height = 0
        lightPath.setPos(height, 0, 0)

        def shadowCameraRotate(task, shadowCamera=shadowCamera):
            shadowCamera.setHpr(render, 0, 0, 0)
            lightPath.lookAt(shadowCamera, 0, 0, 3)
            return Task.cont
            
        doShadow = config.GetBool('want-decent-shadow-%s' % self.__class__.__name__, ShadowCaster.WantDecentShadow)
        if doShadow:
            doShadow = Settings.getEnableShadows()
            
        if doShadow:
            taskMgr.remove(self.shadowTaskName)
            taskMgr.add(shadowCameraRotate, self.shadowTaskName)

            self.sc = DirectShadowCaster(lightPath, objectPath, 4, 6)
            self.sc.setGround(render)
        
        else:
            if self.dropShadow:
                self.dropShadow.unstash()
                