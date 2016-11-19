import toontown.minigame.MinigameCreatorAI
from toontown.distributed.ToontownDistrictAI import ToontownDistrictAI
from toontown.distributed.ToontownDistrictStatsAI import ToontownDistrictStatsAI
from otp.ai.TimeManagerAI import TimeManagerAI
from otp.ai.MagicWordManagerAI import MagicWordManagerAI
from toontown.ai.HolidayManagerAI import HolidayManagerAI
from toontown.ai.NewsManagerAI import NewsManagerAI
from toontown.ai.FishManagerAI import FishManagerAI
from toontown.safezone.SafeZoneManagerAI import SafeZoneManagerAI
from toontown.distributed.ToontownInternalRepository import ToontownInternalRepository
from toontown.toon import NPCToons
from toontown.hood import TTHoodDataAI, DDHoodDataAI, DGHoodDataAI, BRHoodDataAI, MMHoodDataAI, DLHoodDataAI, FFHoodDataAI
from toontown.hood import OZHoodDataAI, GSHoodDataAI, GZHoodDataAI, ZoneUtil
from toontown.hood import SellbotHQDataAI, CashbotHQDataAI, LawbotHQDataAI, BossbotHQDataAI
from toontown.toonbase import ToontownGlobals
from direct.distributed.PyDatagram import *
from otp.ai.AIZoneData import *
from toontown.dna.DNAParser import *
from toontown.coghq import MintManagerAI, FactoryManagerAI, LawOfficeManagerAI, CountryClubManagerAI
from otp.friends.FriendManagerAI import FriendManagerAI
from toontown.estate.EstateManagerAI import EstateManagerAI
from toontown.uberdog.DistributedPartyManagerAI import DistributedPartyManagerAI
from otp.distributed.OtpDoGlobals import *
from direct.task import Task
from toontown.toonbase import ToontownGlobals
from toontown.effects.DistributedFireworkShowAI import DistributedFireworkShowAI
from toontown.effects import FireworkShows
import random
from direct.distributed.ClockDelta import *
import time, os, datetime, sys
from otp.ai.MagicWordGlobal import *
from toontown.parties import PartyGlobals

from toontown.tutorial.TutorialManagerAI import TutorialManagerAI
from DistributedSuitInvasionManagerAI import DistributedSuitInvasionManagerAI, SuitDNA
from QuestManagerAI import QuestManagerAI
from PromotionManagerAI import PromotionManagerAI
from toontown.battle.CogPageManagerAI import CogPageManagerAI
from toontown.coghq.CogSuitManagerAI import CogSuitManagerAI
from toontown.building.DistributedTrophyMgrAI import *
from toontown.estate.DistributedBankMgrAI import *
from toontown.catalog.CatalogManagerAI import *
from toontown.pets.PetManagerAI import *

hoods = (TTHoodDataAI.TTHoodDataAI, DDHoodDataAI.DDHoodDataAI, DGHoodDataAI.DGHoodDataAI,
         BRHoodDataAI.BRHoodDataAI, MMHoodDataAI.MMHoodDataAI, DLHoodDataAI.DLHoodDataAI,
         GSHoodDataAI.GSHoodDataAI, OZHoodDataAI.OZHoodDataAI, GZHoodDataAI.GZHoodDataAI,
         SellbotHQDataAI.SellbotHQDataAI, CashbotHQDataAI.CashbotHQDataAI,
         LawbotHQDataAI.LawbotHQDataAI, BossbotHQDataAI.BossbotHQDataAI,
         #FFHoodDataAI.FFHoodDataAI
)
         
import DistributedResistanceEmoteMgrAI
import DistributedPolarPlaceEffectMgrAI

from toontown.uberdog.BanManagerAI import BanManagerAI
from toontown.uberdog.ShardAPIManagerAI import ShardAPIManagerAI

class ToontownAIRepository(ToontownInternalRepository):
    def __init__(self, baseChannel, serverId, districtName):
        ToontownInternalRepository.__init__(self, baseChannel, serverId, dcSuffix='AI')

        self.districtName = districtName

        self.zoneAllocator = UniqueIdAllocator(ToontownGlobals.DynamicZonesBegin,
                                               ToontownGlobals.DynamicZonesEnd)

        NPCToons.generateZone2NpcDict()
        self.hoods = []
        self._dnaStoreMap = {}
                
        self.zoneDataStore = AIZoneDataStore()

        self.useAllMinigames = self.config.GetBool('want-all-minigames', False)
        self.doLiveUpdates = True
        
        self.wantCogdominiums = self.config.GetBool('want-cogdo', False)
        self.wantParties = self.config.GetBool('want-parties', True)
        self.wantEmblems = self.config.GetBool('want-emblems', True)
        
        self.questManager = QuestManagerAI(self)
        self.promotionMgr = PromotionManagerAI(self)
        self.cogPageManager = CogPageManagerAI(self)
        self.cogSuitMgr = CogSuitManagerAI(self)

        self.trophyMgr = DistributedTrophyMgrAI(self)
        
        self.fishManager = FishManagerAI()
		
        self.dnaStoreMap = {}
        
        self.mintMgr = MintManagerAI.MintManagerAI(self)
        self.factoryMgr = FactoryManagerAI.FactoryManagerAI(self)
        self.lawMgr = LawOfficeManagerAI.LawOfficeManagerAI(self)
        self.countryClubMgr = CountryClubManagerAI.CountryClubManagerAI(self)
        
        self.buildingManagers = {}
        self.suitPlanners = {}
        
        self.wantMegaInvasions = str(self.ourChannel // 1000000) in self.config.GetString('mega-invasion-shards', '402 403').split()

        self.accept('GLOBAL_MSG_CLOSING_FOR_UPDATE_NOW', sys.exit, [1024])

    def getTrackClsends(self):
        return False
        
    def handleConnected(self):
        ToontownInternalRepository.handleConnected(self)
        self.districtId = self.allocateChannel()
        self.distributedDistrict = ToontownDistrictAI(self)
        self.distributedDistrict.setName(self.districtName)
        self.distributedDistrict.generateWithRequiredAndId(simbase.air.districtId, self.getGameDoId(), 2)

        dg = PyDatagram()
        dg.addServerHeader(simbase.air.districtId, simbase.air.ourChannel, STATESERVER_OBJECT_SET_AI)
        dg.addChannel(simbase.air.ourChannel)
        simbase.air.send(dg)

        self.createGlobals()
        self.createZones()

    def __ready(self):
        self.removeAtExit(self.districtStats.doId)

        self.apiMgr = ShardAPIManagerAI(self)
        self.apiMgr.d_setShardData()
        
        self.banMgr = BanManagerAI(self)
        
        self.trophyMgr.updateToonData()
        
    def gotUberdogAPISync(self):
        if not self.distributedDistrict.getAvailable():
            self.notify.info('Got UD API sync, opening shard...')
            messenger.send('startShardActivity')
            self.distributedDistrict.b_setAvailable(1)
            self.sendNetEvent('shardStarted')
            self.addExitEvent('shardDied')

    def incrementPopulation(self):
        self.districtStats.b_setAvatarCount(self.districtStats.getAvatarCount() + 1)

    def decrementPopulation(self):
        self.districtStats.b_setAvatarCount(self.districtStats.getAvatarCount() - 1)

    def allocateZone(self):
        return self.zoneAllocator.allocate()

    def deallocateZone(self, zone):
        self.zoneAllocator.free(zone)

    def getZoneDataStore(self):
        return self.zoneDataStore

    def getAvatarExitEvent(self, avId):
        return 'distObjDelete-%d' % avId

    def createGlobals(self):
        self.districtStats = ToontownDistrictStatsAI(self)
        self.districtStats.settoontownDistrictId(self.districtId)
        self.districtStats.generateWithRequiredAndId(self.allocateChannel(), self.getGameDoId(), 2)
		
        self.timeManager = TimeManagerAI(self)
        self.timeManager.generateWithRequired(2)

        self.newsManager = NewsManagerAI(self)
        self.newsManager.generateWithRequired(2)

        self.holidayManager = HolidayManagerAI(self)

        self.magicWordManager = MagicWordManagerAI(self)
        self.magicWordManager.generateWithRequired(2)

        self.safeZoneManager = SafeZoneManagerAI(self)
        self.safeZoneManager.generateWithRequired(2)
		
        self.petMgr = PetManagerAI(self)

        self.friendManager = FriendManagerAI(self)
        self.friendManager.generateWithRequired(2)

        self.partyManager = DistributedPartyManagerAI(self)
        self.partyManager.generateWithRequired(2)
		
        self.tutorialManager = TutorialManagerAI(self)
        self.tutorialManager.generateWithRequired(2)
		
        self.estateManager = EstateManagerAI(self)
        self.estateManager.generateWithRequired(2)
        
        self.suitInvasionManager = DistributedSuitInvasionManagerAI(self)
        self.suitInvasionManager.generateWithRequired(2)

        self.bankMgr = DistributedBankMgrAI(self)
        self.bankMgr.generateWithRequired(2)
        
        self.catalogManager = CatalogManagerAI(self)
        self.catalogManager.generateWithRequired(2)
        
        self.huntId = 0
        
        if self.holidayManager.isHolidayRunning(ToontownGlobals.TRICK_OR_TREAT):
            import DistributedTrickOrTreatTargetAI
            self.trickOrTreatMgr = DistributedTrickOrTreatTargetAI.DistributedTrickOrTreatTargetAI(self)
            self.trickOrTreatMgr.generateWithRequired(2)
            
        self.handleBlackCatMgr()
        self.handleBloodsuckerInvasion()
        self.handleSkelCogWeekInvasion()
        
        if config.GetBool('want-resistance-emote', True):
            self.resistanceMgr = DistributedResistanceEmoteMgrAI.DistributedResistanceEmoteMgrAI(self)
            self.resistanceMgr.generateWithRequired(9720)
        
        if config.GetBool('want-top-toons', True):
            self.topToonsMgr = self.generateGlobalObject(OTP_DO_ID_TOONTOWN_TOP_TOONS_MGR, 'DistributedTopToonsManager')
            
        else:
            self.topToonsMgr = None

        if config.GetBool('want-polar-effect', True):
            self.polarMgr = DistributedPolarPlaceEffectMgrAI.DistributedPolarPlaceEffectMgrAI(self)
            self.polarMgr.generateWithRequired(3821)
            
    def handleBlackCatMgr(self):
        today = datetime.datetime.now()
        start = datetime.datetime(today.year, 10, 31)
        end = datetime.datetime(today.year, 11, 3)
        
        def createBlackCatMgr(task=None):
            import DistributedBlackCatMgrAI
            self.blackCatMgr = DistributedBlackCatMgrAI.DistributedBlackCatMgrAI(self)
            self.blackCatMgr.generateWithRequired(2513)
            if not self.config.GetBool('force-black-cat-mgr', False):
                self.blackCatMgr.expire((end - today).total_seconds())
            return Task.done
        
        if start <= today < end or self.config.GetBool('force-black-cat-mgr', False):
            createBlackCatMgr(None)
            
        elif start >= today:
            taskMgr.doMethodLater((start - today).total_seconds(), createBlackCatMgr, 'air-createBlackCatMgr')
            
    def handleBloodsuckerInvasion(self):
        if not self.wantMegaInvasions:
            return
            
        today = datetime.datetime.now()
        start = datetime.datetime(today.year, 10, 31)
        end = datetime.datetime(today.year, 11, 3)
        
        if start <= today < end:
            self.startMegaInvasion(9, end=end)
            
        elif start > today:
            taskMgr.doMethodLater((start - today).total_seconds(), self.startMegaInvasion, 'air-mega-invasion-9', extraArgs=[9, False, end])
            
    def handleSkelCogWeekInvasion(self):
        if not self.wantMegaInvasions:
            return
            
        today = datetime.datetime.now()
        start = datetime.datetime(today.year, 11, 10)
        end = datetime.datetime(today.year, 11, 17)
        
        if start <= today < end:
            self.startMegaInvasion(-1, skel=True, end=end)
            
        elif start > today:
            taskMgr.doMethodLater((start - today).total_seconds(), self.startMegaInvasion, 'air-mega-invasion-skel', extraArgs=[-1, True, end])
            
    def startMegaInvasion(self, suitIndex, skel=False, end=None):
        if suitIndex >= 0:
            suitName = SuitDNA.suitHeadTypes[suitIndex]
            
        else:
            suitName = None
            
        if self.suitInvasionManager.hasInvading():
            if self.suitInvasionManager.isMega():
                return Task.done
                
            self.suitInvasionManager.abort()
            
        self.suitInvasionManager.startInvasion(suitName, skel, mega=True)
        if end:
            def doAbort(task):
                self.suitInvasionManager.abort()
                return task.done

            today = datetime.datetime.now()
            taskMgr.doMethodLater((end - today).total_seconds(), doAbort, 'air-abort-mega-invasion')
        
    def getStorage(self, zone):
        s = self._dnaStoreMap.get(zone)
        if not s:
            s = DNAStorage()
            self.loadDNAFileAI(s, self.genDNAFileName(zone))
            self._dnaStoreMap[zone] = s
        
        return s

    def createZones(self):
        self.zoneTable = {
                          1000: ((1000, 1, 0), (1100, 1, 1), (1200, 1, 1), (1300, 1, 1)),
                          2000: ((2000, 1, 0), (2100, 1, 1), (2200, 1, 1), (2300, 1, 1)),
                          3000: ((3000, 1, 0), (3100, 1, 1), (3200, 1, 1), (3300, 1, 1)),
                          4000: ((4000, 1, 0), (4100, 1, 1), (4200, 1, 1), (4300, 1, 1)),
                          5000: ((5000, 1, 0), (5100, 1, 1), (5200, 1, 1), (5300, 1, 1)),
                          9000: ((9000, 1, 0), (9100, 1, 1), (9200, 1, 1)),
                          
                          6000: (),
                          7000: ((7000, 1, 0), (7100, 1, 1)),
                          8000: ((8000, 1, 0),),
                          10000: (),
                          11000: (),
                          12000: (),
                          13000: (),
                          17000: (),
                         }
        
        self.__nextHood(0)
                         
    def __nextHood(self, hoodIndex):
        if hoodIndex >= len(hoods):
            self.__ready()
            return Task.done
                         
        self.hoods.append(hoods[hoodIndex](self))
        taskMgr.doMethodLater(0, ToontownAIRepository.__nextHood, 'nextHood', [self, hoodIndex + 1])
        return Task.done

    def sendSetZone(self, obj, zoneId):
        obj.b_setLocation(obj.parentId, zoneId)
        
    def getDisconnectReason(self, avId):
        return self.timeManager.disconnectReasonMap.get(avId, 1) # Default: user closed window
        
    def killToon(self, avId, force = True):
        return


        '''
        Kills given toon if within this shard.
        If force is False, then checks getDisconnectReason.
        '''
        toon = self.doId2do.get(avId)
        
        if not toon:
            self.notify.warning('Tried to kill non-existing toon %s' % avId)
            return False
            
        if not force:
            if self.getDisconnectReason(avId) == 3: # Python Error
                return False
            
        toon.b_setHp(0)
        
        inventory = toon.inventory
        inventory.zeroInv()
        toon.b_setInventory(inventory.makeNetString())
        
        self.notify.info('Killed toon %s, RIP!' % avId)
        return True
        
    def handleObjExit(self, di):
        doId = di.getUint32()

        if doId not in self.doId2do:
            self.notify.warning('Received AI exit for unknown object %d' % (doId))
            return

        do = self.doId2do[doId]
        do.sendDeleteEvent()
        self.removeDOFromTables(do)
        do.delete()

@magicWord(types=[int, str], chains=[CHAIN_HEAD])
def closeserver(time, type='maintenance'):
    if type not in ('maintenance', 'update'):
        return 'Invalid type!'
        
    if time < 0 or time in (2, 3, 4):
        return 'Min time is 5 (or 0 to abort, 1 to get)'
        
    av = spellbook.getInvoker()
    av.air.sendNetEvent('GLOBAL_MSG_CLOSING_FOR_UPDATE', [time, type])
    
    def resp(status):
        if status:
            channel = av.GetPuppetConnectionChannel(av.doId)
            av.air.sendSysMsg(status, channel)
        
    av.air.acceptOnce('GLOBAL_MSG_CLOSING_FOR_UPDATE_RESP', resp)
