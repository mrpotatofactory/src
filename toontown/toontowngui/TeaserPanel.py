from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.gui import DirectGuiGlobals
from pandac.PandaModules import *
from direct.directnotify import DirectNotifyGlobal
import TTDialog
from toontown.toonbase import TTLocalizer
from direct.showbase import PythonUtil
from direct.showbase.DirectObject import DirectObject
from otp.login import LeaveToPayDialog
Pages = {'otherHoods': (TTLocalizer.TeaserOtherHoods,),
 'typeAName': (TTLocalizer.TeaserTypeAName,),
 'sixToons': (TTLocalizer.TeaserSixToons,),
 'otherGags': (TTLocalizer.TeaserOtherGags,),
 'clothing': (TTLocalizer.TeaserClothing,),
 'cogHQ': (TTLocalizer.TeaserCogHQ,),
 'secretChat': (TTLocalizer.TeaserSecretChat,),
 'quests': (TTLocalizer.TeaserQuests,),
 'emotions': (TTLocalizer.TeaserEmotions,),
 'minigames': (TTLocalizer.TeaserMinigames,),
 'karting': (TTLocalizer.TeaserKarting,),
 'kartingAccessories': (TTLocalizer.TeaserKartingAccessories,),
 'gardening': (TTLocalizer.TeaserGardening,),
 'tricks': (TTLocalizer.TeaserTricks,),
 'species': (TTLocalizer.TeaserSpecies,),
 'golf': (TTLocalizer.TeaserGolf,),
 'fishing': (TTLocalizer.TeaserFishing,),
 'parties': (TTLocalizer.TeaserParties,),
 'plantGags': (TTLocalizer.TeaserPlantGags,),
 'pickGags': (TTLocalizer.TeaserPickGags,),
 'restockGags': (TTLocalizer.TeaserRestockGags,),
 'getGags': (TTLocalizer.TeaserGetGags,),
 'useGags': (TTLocalizer.TeaserUseGags,)}
PageOrder = ['sixToons',
 'typeAName',
 'species',
 'otherHoods',
 'otherGags',
 'clothing',
 'parties',
 'tricks',
 'cogHQ',
 'secretChat',
 'quests',
 'emotions',
 'minigames',
 'karting',
 'kartingAccessories',
 'gardening',
 'golf',
 'fishing',
 'plantGags',
 'pickGags',
 'restockGags',
 'getGags',
 'useGags']

class TeaserPanel(DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('TeaserPanel')

    def __init__(self, pageName, doneFunc = None):
        self.doneFunc = doneFunc
        self.dialog = TTDialog.TTGlobalDialog('Access denied.', style=TTDialog.Acknowledge, doneEvent='teaser-done')
        self.acceptOnce('teaser-done', self.ok)
        base.transitions.fadeScreen(.7)
        
    def ok(self, *args):
        self.dialog.cleanup()
        self.dialog = None
        base.transitions.noFade()
        
        if self.doneFunc:
            self.notify.debug('calling doneFunc')
            self.doneFunc()

    def destroy(self):
        self.cleanup()

    def cleanup(self):
        pass

    def unload(self):
        pass

    def showPage(self, pageName):
        pass

    def removed(self):
        return 1
