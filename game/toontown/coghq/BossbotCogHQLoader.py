from direct.directnotify import DirectNotifyGlobal
from direct.fsm import StateData
import CogHQLoader
from toontown.toonbase import ToontownGlobals
from direct.gui import DirectGui
from toontown.toonbase import TTLocalizer
from toontown.toon import Toon
from direct.fsm import State
from toontown.coghq import BossbotHQExterior
from toontown.coghq import BossbotHQBossBattle
from toontown.coghq import BossbotOfficeExterior
from toontown.coghq import CountryClubInterior
from toontown.coghq import TowersLobby
from toontown.suit import SuitDNA
from toontown.building import SuitInterior
from pandac.PandaModules import *
import random, sys
aspectSF = 0.7227

class BossbotCogHQLoader(CogHQLoader.CogHQLoader):
    notify = DirectNotifyGlobal.directNotify.newCategory('BossbotCogHQLoader')
    
    def __init__(self, hood, parentFSMState, doneEvent):
        CogHQLoader.CogHQLoader.__init__(self, hood, parentFSMState, doneEvent)
        self.fsm.addState(State.State('countryClubInterior', self.enterCountryClubInterior, self.exitCountryClubInterior, ['quietZone', 'cogHQExterior']))
        self.fsm.addState(State.State('towersLobby', self.enterTowersLobby, self.exitTowersLobby, ['quietZone', 'cogHQExterior', 'suitInterior']))
        self.fsm.addState(State.State('suitInterior', self.enterSuitInterior, self.exitSuitInterior, ['quietZone', 'cogHQExterior']))
        for stateName in ['start', 'cogHQExterior', 'quietZone']:
            state = self.fsm.getStateNamed(stateName)
            state.addTransition('countryClubInterior')
            state.addTransition('towersLobby')
            
        self.fsm.getStateNamed('quietZone').addTransition('suitInterior')

        self.musicFile = random.choice(['phase_12/audio/bgm/Bossbot_Entry_v1.ogg', 'phase_12/audio/bgm/Bossbot_Entry_v2.ogg', 'phase_12/audio/bgm/Bossbot_Entry_v3.ogg'])
        self.cogHQExteriorModelPath = 'phase_12/models/bossbotHQ/CogGolfHub'
        self.factoryExteriorModelPath = 'phase_11/models/lawbotHQ/LB_DA_Lobby'
        self.cogHQLobbyModelPath = 'phase_12/models/bossbotHQ/CogGolfCourtyard'
        self.geom = None
        return

    def load(self, zoneId):
        CogHQLoader.CogHQLoader.load(self, zoneId)
        Toon.loadBossbotHQAnims()

    def unloadPlaceGeom(self):
        if self.geom:
            self.geom.removeNode()
            self.geom = None
        CogHQLoader.CogHQLoader.unloadPlaceGeom(self)
        return

    def loadPlaceGeom(self, zoneId):
        self.notify.info('loadPlaceGeom: %s' % zoneId)
        zoneId = zoneId - zoneId % 100
        self.notify.debug('zoneId = %d ToontownGlobals.BossbotHQ=%d' % (zoneId, ToontownGlobals.BossbotHQ))
        if zoneId == ToontownGlobals.BossbotHQ:
            self.geom = loader.loadModel(self.cogHQExteriorModelPath)
            gzLinkTunnel = self.geom.find('**/LinkTunnel1')
            gzLinkTunnel.setName('linktunnel_gz_17000_DNARoot')
            self.makeSigns()
            top = self.geom.find('**/TunnelEntrance')
            origin = top.find('**/tunnel_origin')
            origin.setH(-33.33)
            
        elif zoneId == ToontownGlobals.BossbotLobby:
            if base.config.GetBool('want-qa-regression', 0):
                self.notify.info('QA-REGRESSION: COGHQ: Visit BossbotLobby')
            self.notify.debug('cogHQLobbyModelPath = %s' % self.cogHQLobbyModelPath)
            self.geom = loader.loadModel(self.cogHQLobbyModelPath)
            
        elif zoneId == ToontownGlobals.TowersLobby:
            self.geom = hidden.attachNewNode("geom")
            
            env = loader.loadModel(self.cogHQExteriorModelPath)
            
            env.find('**/LinkTunnel1').removeNode()
            env.find('**/gatesall').removeNode()
            env.find('**/ClubHouse').removeNode()
            env.find('**/GateHouse').removeNode()
            
            # 'panda3d.core.NodePathCollection' object has no attribute 'removeNode' cri so hard
            env.findAllMatches('**/door_*').hide()
            env.findAllMatches('**/tree_*').hide()
            
            env.setScale(5)
            env.setZ(-7)
            env.flattenStrong()
            env.reparentTo(self.geom)
            
            store = base.cr.playGame.dnaStore
            loader.loadDNAFile(store, 'phase_5/dna/storage_town.dna')
            loader.loadDNAFile(store, 'phase_5/dna/storage_TT_town.dna')
            bldgs = self.geom.attachNewNode(loader.loadDNAFile(store, 'phase_12/dna/towers.dna'))
            bldgs.setPos(-150, 90, 0)
            tile = bldgs.find('**/TILECOLLIDER')
            tile.node().setCollideMask(2)
            
            bucket = hidden.attachNewNode('landmarkBlocks')
            npc = bldgs.findAllMatches('**/sb*:*_landmark_*_DNARoot')
            for i in range(npc.getNumPaths()):
                npc.getPath(i).wrtReparentTo(bucket)
                
            self.zoneDict = {19000: bldgs}
            
        else:
            self.notify.warning('loadPlaceGeom: unclassified zone %s' % zoneId)
            
        CogHQLoader.CogHQLoader.loadPlaceGeom(self, zoneId)

    def makeSigns(self):
        def makeSign(topStr, signStr, textId):
            top = self.geom.find('**/' + topStr)
            if not top.isEmpty():
                sign = top.find('**/' + signStr)
                locator = top.find('**/sign_origin')
                signText = DirectGui.OnscreenText(text=TextEncoder.upper(TTLocalizer.GlobalStreetNames[textId][-1]), font=ToontownGlobals.getSuitFont(), scale=TTLocalizer.BCHQLsignText, fg=(0, 0, 0, 1), parent=sign)
                signText.setPosHpr(locator, 0, -0.1, -0.25, 0, 0, 0)
                signText.setDepthWrite(0)

        makeSign('Gate_2', 'Sign_6', 10700)
        makeSign('TunnelEntrance', 'Sign_2', 1000)
        makeSign('Gate_3', 'Sign_3', 10600)
        makeSign('Gate_4', 'Sign_4', 10500)
        makeSign('GateHouse', 'Sign_5', 10200)

    def unload(self):
        CogHQLoader.CogHQLoader.unload(self)
        Toon.unloadSellbotHQAnims()

    def enterStageInterior(self, requestStatus):
        self.placeClass = StageInterior.StageInterior
        self.stageId = requestStatus['stageId']
        self.enterPlace(requestStatus)

    def exitStageInterior(self):
        self.exitPlace()
        self.placeClass = None
        return

    def getExteriorPlaceClass(self):
        self.notify.debug('getExteriorPlaceClass')
        return BossbotHQExterior.BossbotHQExterior

    def getBossPlaceClass(self):
        self.notify.debug('getBossPlaceClass')
        return BossbotHQBossBattle.BossbotHQBossBattle

    def enterFactoryExterior(self, requestStatus):
        self.placeClass = BossbotOfficeExterior.BossbotOfficeExterior
        self.enterPlace(requestStatus)

    def exitFactoryExterior(self):
        taskMgr.remove('titleText')
        self.hood.hideTitleText()
        self.exitPlace()
        self.placeClass = None
        return

    def enterCogHQBossBattle(self, requestStatus):
        self.notify.debug('BossbotCogHQLoader.enterCogHQBossBattle')
        CogHQLoader.CogHQLoader.enterCogHQBossBattle(self, requestStatus)
        base.cr.forbidCheesyEffects(1)

    def exitCogHQBossBattle(self):
        self.notify.debug('BossbotCogHQLoader.exitCogHQBossBattle')
        CogHQLoader.CogHQLoader.exitCogHQBossBattle(self)
        base.cr.forbidCheesyEffects(0)

    def enterCountryClubInterior(self, requestStatus):
        self.placeClass = CountryClubInterior.CountryClubInterior
        self.notify.info('enterCountryClubInterior, requestStatus=%s' % requestStatus)
        self.countryClubId = requestStatus['countryClubId']
        self.enterPlace(requestStatus)

    def exitCountryClubInterior(self):
        self.exitPlace()
        self.placeClass = None
        del self.countryClubId
    
    def enterTowersLobby(self, requestStatus):
        self.placeClass = TowersLobby.TowersLobby
        self.enterPlace(requestStatus)
    
    def exitTowersLobby(self):
        self.exitPlace()
        self.placeClass = None
        
    def enterSuitInterior(self, requestStatus = None):
        self.placeDoneEvent = 'suit-interior-done'
        self.acceptOnce(self.placeDoneEvent, self.handleSuitInteriorDone)
        self.place = SuitInterior.SuitInterior(self, self.fsm, self.placeDoneEvent)
        self.place.load()
        self.place.enter(requestStatus)
        base.cr.playGame.setPlace(self.place)

    def exitSuitInterior(self):
        self.ignore(self.placeDoneEvent)
        self.place.exit()
        self.place.unload()
        self.place = None
        base.cr.playGame.setPlace(self.place)

    def handleSuitInteriorDone(self):
        doneStatus = self.place.getDoneStatus()
        self.fsm.request('quietZone', [doneStatus])
