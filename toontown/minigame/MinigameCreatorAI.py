import copy
import random
import time
from toontown.toonbase import ToontownGlobals
from toontown.uberdog import TopToonsGlobals
import DistributedMinigameTemplateAI
import DistributedRaceGameAI
import DistributedCannonGameAI
import DistributedTagGameAI
import DistributedPatternGameAI
import DistributedRingGameAI
import DistributedMazeGameAI
import DistributedTugOfWarGameAI
import DistributedCatchGameAI
import DistributedDivingGameAI
import DistributedTargetGameAI
import DistributedPairingGameAI
import DistributedPhotoGameAI
import DistributedVineGameAI
import DistributedIceGameAI
import DistributedCogThiefGameAI
import DistributedTwoDGameAI
import DistributedTravelGameAI
import DistributedSurfersGameAI
import DistributedFADGameAI
import TravelGameGlobals
from otp.ai.MagicWordGlobal import *
ALLOW_TEMP_MINIGAMES = simbase.config.GetBool('allow-temp-minigames', False)
if ALLOW_TEMP_MINIGAMES:
    from toontown.minigame.TempMinigameAI import *
simbase.forcedMinigameId = simbase.config.GetInt('minigame-id', 0)
RequestMinigame = {}
MinigameZoneRefs = {}

# Add here the games that can't be an option for trolley tracks
# None of the new minigames can since they'd crash the client
NonTrolleyTrackableGames = (ToontownGlobals.TravelGameId,
                            ToontownGlobals.SurfersGameId,
                            ToontownGlobals.FADGameId)
                            
# Add here the new minigames that are not stable enough (i. e. still not tested enough)
# They will be blocked on release server
UnstableMinigames = (ToontownGlobals.SurfersGameId,
                     ToontownGlobals.FADGameId)

def createMinigame(air, playerArray, trolleyZone, minigameZone = None, previousGameId = ToontownGlobals.NoPreviousGameId, newbieIds = [], startingVotes = None, metagameRound = -1, desiredNextGame = None):
    isTracks = 1
    if minigameZone == None:
        isTracks = 0
        minigameZone = air.allocateZone()
    acquireMinigameZone(minigameZone)  
    
    excludeList = [ToontownGlobals.TravelGameId]
    if trolleyZone == ToontownGlobals.FunnyFarm:
        trolleyZone = config.GetInt('funny-farm-trolley-fake-hood', ToontownGlobals.DonaldsDreamland)
        # the games below need to be disabled on FF bc there's no support for them!
        excludeList.extend([ToontownGlobals.MazeGameId, ToontownGlobals.CogThiefGameId, ToontownGlobals.PhotoGameId])
        
    if not config.GetBool('want-dev-minigames', False):
        excludeList.extend(UnstableMinigames)
        
    mgId = None
    mgDiff = None
    mgSzId = None
    for avId in playerArray:
        request = RequestMinigame.get(avId)
        if request != None:
            mgId, mgKeep, mgDiff, mgSzId = request
            if not mgKeep:
                del RequestMinigame[avId]
            break

    if mgId != None:
        pass
    elif simbase.forcedMinigameId:
        mgId = simbase.forcedMinigameId
    else:
        randomList = list(copy.copy(ToontownGlobals.MinigamePlayerMatrix[len(playerArray)]))
        if simbase.air.useAllMinigames and len(playerArray) > 1:
            randomList = list(copy.copy(ToontownGlobals.MinigameIDs))
            for gameId in excludeList:
                if gameId in randomList:
                    randomList.remove(gameId)

        if isTracks:
            for gameId in NonTrolleyTrackableGames:
                if gameId in randomList:
                    randomList.remove(gameId)

        if previousGameId != ToontownGlobals.NoPreviousGameId:
            if randomList.count(previousGameId) != 0 and len(randomList) > 1:
                randomList.remove(previousGameId)
        randomList = removeUnreleasedMinigames(randomList, True)
        mgId = random.choice(randomList)
        if metagameRound > -1:
            if metagameRound % 2 == 0:
                mgId = ToontownGlobals.TravelGameId
            elif desiredNextGame:
                mgId = desiredNextGame
    mgCtors = {ToontownGlobals.RaceGameId: DistributedRaceGameAI.DistributedRaceGameAI,
     ToontownGlobals.CannonGameId: DistributedCannonGameAI.DistributedCannonGameAI,
     ToontownGlobals.TagGameId: DistributedTagGameAI.DistributedTagGameAI,
     ToontownGlobals.PatternGameId: DistributedPatternGameAI.DistributedPatternGameAI,
     ToontownGlobals.RingGameId: DistributedRingGameAI.DistributedRingGameAI,
     ToontownGlobals.MazeGameId: DistributedMazeGameAI.DistributedMazeGameAI,
     ToontownGlobals.TugOfWarGameId: DistributedTugOfWarGameAI.DistributedTugOfWarGameAI,
     ToontownGlobals.CatchGameId: DistributedCatchGameAI.DistributedCatchGameAI,
     ToontownGlobals.DivingGameId: DistributedDivingGameAI.DistributedDivingGameAI,
     ToontownGlobals.TargetGameId: DistributedTargetGameAI.DistributedTargetGameAI,
     ToontownGlobals.MinigameTemplateId: DistributedMinigameTemplateAI.DistributedMinigameTemplateAI,
     ToontownGlobals.PairingGameId: DistributedPairingGameAI.DistributedPairingGameAI,
     ToontownGlobals.VineGameId: DistributedVineGameAI.DistributedVineGameAI,
     ToontownGlobals.IceGameId: DistributedIceGameAI.DistributedIceGameAI,
     ToontownGlobals.CogThiefGameId: DistributedCogThiefGameAI.DistributedCogThiefGameAI,
     ToontownGlobals.TwoDGameId: DistributedTwoDGameAI.DistributedTwoDGameAI,
     ToontownGlobals.TravelGameId: DistributedTravelGameAI.DistributedTravelGameAI,
     ToontownGlobals.PhotoGameId: DistributedPhotoGameAI.DistributedPhotoGameAI,
     ToontownGlobals.SurfersGameId: DistributedSurfersGameAI.DistributedSurfersGameAI,
     ToontownGlobals.FADGameId: DistributedFADGameAI.DistributedFADGameAI}
    if ALLOW_TEMP_MINIGAMES:
        from TempMinigameAI import TempMgCtors
        for key, value in TempMgCtors.items():
            mgCtors[key] = value

    try:
        mg = mgCtors[mgId](air, mgId)
    except KeyError:
        raise Exception, 'unknown minigame ID: %s' % mgId

    mg.setExpectedAvatars(playerArray)
    mg.setNewbieIds(newbieIds)    
    mg.setTrolleyZone(trolleyZone)
    mg.setDifficultyOverrides(mgDiff, mgSzId)
    if startingVotes == None:
        for avId in playerArray:
            mg.setStartingVote(avId, TravelGameGlobals.DefaultStartingVotes)

    else:
        for index in range(len(startingVotes)):
            avId = playerArray[index]
            votes = startingVotes[index]
            if votes < 0:
                votes = 0
            mg.setStartingVote(avId, votes)

    mg.setMetagameRound(metagameRound)
    mg.generateWithRequired(minigameZone)
    toons = []
    for id in playerArray:
        toon = simbase.air.doId2do.get(id)
        if toon != None:
            toons.append(toon)
            
    for toon in toons:
        messenger.send('topToonsManager-event', [toon.doId, TopToonsGlobals.CAT_TROLLEY, 1])

    retVal = {}
    retVal['minigameZone'] = minigameZone
    retVal['minigameId'] = mgId
    return retVal


def acquireMinigameZone(zoneId):
    if zoneId not in MinigameZoneRefs:
        MinigameZoneRefs[zoneId] = 0
    MinigameZoneRefs[zoneId] += 1


def releaseMinigameZone(zoneId):
    MinigameZoneRefs[zoneId] -= 1
    if MinigameZoneRefs[zoneId] <= 0:
        del MinigameZoneRefs[zoneId]
        simbase.air.deallocateZone(zoneId)


def removeUnreleasedMinigames(startList, increaseChanceOfNewGames = 0):
    randomList = startList[:]
    for gameId in ToontownGlobals.MinigameReleaseDates:
        dateTuple = ToontownGlobals.MinigameReleaseDates[gameId]
        currentTime = time.time()
        releaseTime = time.mktime((dateTuple[0],
         dateTuple[1],
         dateTuple[2],
         0,
         0,
         0,
         0,
         0,
         -1))
        releaseTimePlus1Week = releaseTime + 7 * 24 * 60 * 60
        if currentTime < releaseTime:
            if gameId in randomList:
                doRemove = True
                if gameId == ToontownGlobals.CogThiefGameId and simbase.air.config.GetBool('force-allow-thief-game', 0):
                    doRemove = False
                    if increaseChanceOfNewGames:
                        randomList += [gameId] * 4
                elif gameId == ToontownGlobals.IceGameId and simbase.air.config.GetBool('force-allow-ice-game', 0):
                    doRemove = False
                    if increaseChanceOfNewGames:
                        randomList += [gameId] * 4
                elif gameId == ToontownGlobals.TwoDGameId and simbase.air.config.GetBool('force-allow-2d-game', 0):
                    doRemove = False
                    if increaseChanceOfNewGames:
                        randomList += [gameId] * 4
                elif gameId == ToontownGlobals.PhotoGameId and simbase.air.config.GetBool('force-allow-photo-game', 0):
                    doRemove = False
                    if increaseChanceOfNewGames:
                        randomList += [gameId] * 4
                if doRemove:
                    randomList.remove(gameId)
        if releaseTime < currentTime and currentTime < releaseTimePlus1Week and gameId in randomList and increaseChanceOfNewGames:
            randomList += [gameId] * 4

    return randomList

@magicWord(chains=[CHAIN_MOD], types=[str, int, int, int])
def requestMinigame(minigameName='remove', minigameKeep=False, minigameDiff=None, minigamePG=None):
    if minigameName=='remove':
        if spellbook.getInvoker().doId in RequestMinigame:
            del RequestMinigame[spellbook.getInvoker().doId]
            return "Deleted trolley game request."
        else:
            return "You had no trolley game requests!"
    else:
        mg = ToontownGlobals.MinigameNames[minigameName]
        if not config.GetBool('want-dev-minigames', False):
            if mg in UnstableMinigames:
                return 'The game you requested is disallowed in this server.'
            
        RequestMinigame[spellbook.getTarget().doId] = mg, minigameKeep, minigameDiff, minigamePG
        return "Your request for " + minigameName + " was added."
