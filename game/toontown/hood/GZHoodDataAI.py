from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals
import HoodDataAI

class GZHoodDataAI(HoodDataAI.HoodDataAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('GZHoodDataAI')
    numStreets = 0
    
    zoneId = ToontownGlobals.GolfZone
    wantTrolley = False
    