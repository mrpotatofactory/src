from direct.showbase.DirectObject import DirectObject
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.MsgTypes import *
from direct.directnotify import DirectNotifyGlobal

class BanManagerAI(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('BanManagerAI')
    
    def __init__(self, air):
        self.air = air
        
    def ban(self, banner, target, time, reason):
        self.air.sendNetEvent('BANMGR_ban', [banner, target.doId, target.DISLid, time, reason])
        
from otp.ai.MagicWordGlobal import *
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.hood import ZoneUtil

@magicWord(chains=[CHAIN_MOD], types=[bool])
def kick(overrideSelfKick=False):
    if not overrideSelfKick and spellbook.getTarget() == spellbook.getInvoker():
        return 'Are you sure you want to kick yourself? Use "~kick True" if you are.'

    dg = PyDatagram()
    dg.addServerHeader(spellbook.getTarget().GetPuppetConnectionChannel(spellbook.getTarget().doId), simbase.air.ourChannel, CLIENTAGENT_EJECT)
    dg.addUint16(155)
    dg.addString('You were kicked by a moderator!')
    simbase.air.send(dg)
    return '%s was kicked.' % spellbook.getTarget().getName()

@magicWord(chains=[CHAIN_MOD], types=[int, str])
def ban(hours, reason):
    if spellbook.getTarget() == spellbook.getInvoker():
        return 'ERROR: You cannot ban yourself!'
        
    if hours > 24 * 7:
        if spellbook.getInvokerAccess() < 400:
            return 'ERROR: Mods can ban only up to %d hours!' % (24 * 7)
            
    MAX_TIME = 24 * 60 # 60 days
    
    if hours == 0:
        return 'ERROR: 0 hour?'
            
    if hours == 1:
        if spellbook.getInvokerAccess() < 400:
            return 'ERROR: Mods cannot terminate!'
        
    if hours > MAX_TIME:
        return 'ERROR: Can ban only up to %d hours! Consider terminating (hours=1)' % MAX_TIME
        
    if len(reason) < 3:
        return 'ERROR: Reason too short!'
        
    elif len(reason) > 32:
        return 'ERROR: Reason too long (max 32 chars)!'
            
    target = spellbook.getTarget()
    target.air.banMgr.ban(spellbook.getInvoker().doId, target, hours, reason)
              
@magicWord(chains=[CHAIN_MOD])
def ghost():
    av = spellbook.getTarget() if spellbook.getInvokerAccess() >= 400 else spellbook.getInvoker()
    
    if av.ghostMode == 0:
        av.b_setGhostMode(1 if av.getAdminAccess() < 300 else 2)
        return 'Time to ninja! Enabled ghost for %s' % av.getName()
        
    else:
        av.b_setGhostMode(0)
        return 'Disabled ghost for %s' % av.getName()
        
@magicWord(chains=[CHAIN_MOD])
def badName():
    oldname = spellbook.getTarget().name
    dna = spellbook.getTarget().dna
    colorstring = TTLocalizer.NumToColor[dna.headColor]
    animaltype = TTLocalizer.AnimalToSpecies[dna.getAnimal()]
    spellbook.getTarget().b_setName(colorstring + ' ' + animaltype)
    spellbook.getTarget().sendUpdate('WishNameState', ['REJECTED'])
    return 'Revoked %s\'s name successfully. They have been renamed to %s.' % (oldname, spellbook.getTarget().getName())

@magicWord(chains=[CHAIN_CHARACTERSTATS], types=[int], accessOther=ACCESS_ADMIN)
def setGM(gmId):        
    if not 0 <= gmId <= 4:
        return 'Args: 0=off, 1=council, 2=whistle, 3=fist, 4=gc'
        
    spellbook.getTarget().b_setGM(gmId)
    
    return 'You have set %s to GM type %s' % (spellbook.getTarget().getName(), gmId)

@magicWord(chains=[CHAIN_MOD], types=[int, str])
def locate(avIdShort=0, returnType=''):
    if avIdShort <= 0:
        return 'Please enter a valid avId to find! Note: You only need to enter the last few digits of the full avId!'
        
    avIdFull = 100000000 + avIdShort
    av = simbase.air.doId2do.get(avIdFull, None)
    if not av:
        return 'Could not find the avatar on the current AI.'
    
    # Get the avatar's location.
    zoneId = av.getLocation()[1] # This returns: (parentId, zoneId)
    trueZoneId = zoneId
    interior = False
    
    if returnType == 'zone':
        # The avatar that called the MagicWord wants a zoneId... Provide them with the untouched zoneId.
        return '%s is in zoneId %d.' % (av.getName(), trueZoneId)
        
    if returnType == 'playground':
        # The avatar that called the MagicWord wants the playground name that the avatar is currently in.
        zoneId = ZoneUtil.getCanonicalHoodId(zoneId)
    
    if ZoneUtil.isInterior(zoneId):
        # If we're in an interior, we want to fetch the street/playground zone, since there isn't
        # any mapping for interiorId -> shop name (afaik).
        zoneId -= 500
        interior = True
    
    if ZoneUtil.isPlayground(zoneId):
        # If it's a playground, TTG contains a map of all hoodIds -> playground names.
        where = ToontownGlobals.hoodNameMap.get(zoneId, None)
    else:
        # If it's not a playground, the TTL contains a list of all streetId -> street names.
        zoneId = zoneId - zoneId % 100 # This essentially truncates the last 2 digits.
        where = TTLocalizer.GlobalStreetNames.get(zoneId, None)

    if not where:
        return 'Failed to map the zoneId %d [trueZoneId: %d] to a location...' % (zoneId, trueZoneId)
    
    if interior:
        return '%s has been located %s %s, inside a building.' % (av.getName(), where[1], where[2])
        
    return '%s has been located %s %s.' % (av.getName(), where[1], where[2])

@magicWord(chains=[CHAIN_HEAD])
def allplayers():
    out = '\n\nCMD\n'
    
    from toontown.toon.DistributedNPCToonBaseAI import DistributedNPCToonBaseAI
    for doId, obj in spellbook.getTarget().air.doId2do.items():
        if obj.__class__.__name__ == 'DistributedToonAI':
            if not obj.isNPC():
                out += '%d: %s [%s]\n' % (doId, obj.getName(), locate(doId - 100000000))

    return out
    