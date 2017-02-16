from pandac.PandaModules import *
import __builtin__, os

if __debug__:
    loadPrcFile('dev.prc')
    
    if os.path.isfile('extra.prc'):
        loadPrcFile('extra.prc')
    
    # let's check if they edited the prc server stuff
    config = getConfigExpress()
    defaultServer = '127.0.0.1'
    if config.GetString('game-server', defaultServer) != defaultServer:
        print 'YOU EDITED THE PRC SERVER!!!'
        print 'DO NOT DO THIS!!'
        print 'USE "-s IP" INSTEAD!'
        
    defaultToken = 'dev'
    if config.GetString('fake-playtoken', defaultToken) != defaultToken:
        print 'YOU EDITED THE PRC TOKEN!!!'
        print 'DO NOT DO THIS!!'
        print 'USE "-t TOKEN" INSTEAD!'

class game:
    name = 'toontown'
    process = 'client'

__builtin__.game = game()

import time, sys, random

customServer = False
if '-s' in sys.argv:
    server = sys.argv[sys.argv.index('-s') + 1]
    
    if __debug__:
        if server == "lc":
            server = "24.89.214.253"

    customServer = True
    loadPrcFileData('', 'game-server ' + server)

if '-t' in sys.argv:
	token = sys.argv[sys.argv.index('-t') + 1]
	loadPrcFileData('', 'fake-playtoken ' + token)

else:
    if customServer:
        print 'You must use a token (-t) with -s!'
        exit()
    
if '-v' in sys.argv:
    ver = sys.argv[sys.argv.index('-v') + 1]
    loadPrcFileData('', 'server-version ' + ver)
    
if '-l' in sys.argv:
    langMap = {'pt': 'portuguese', 'en': 'english', 'leet': 'leet', 'yolo': 'yolo'}
    lang = sys.argv[sys.argv.index('-l') + 1]
    
    if lang == "en":
        print 'WARNING: default language is already English!'
       
    elif lang not in langMap:
        print 'ERROR: invalid lang', lang
        print 'THE LANGUAGES ARE:'
        for l in langMap:
            print '\t', l
          
        print

    loadPrcFileData('', 'language ' + langMap[lang])
    
import sys
reload(sys)
sys.setdefaultencoding('latin-1')# latin-1 utf-8

from toontown.launcher.TTLauncher import TTLauncher
__builtin__.launcher = TTLauncher()

print 'ToontownStart: Starting the game.'
    
tempLoader = Loader()
backgroundNode = tempLoader.loadSync(Filename('phase_3/models/gui/loading-background'))

from direct.gui import DirectGuiGlobals
import ToontownGlobals
DirectGuiGlobals.setDefaultFontFunc(ToontownGlobals.getInterfaceFont)

launcher.setPandaErrorCode(7)

# base
import ToonBase
ToonBase.ToonBase()
base.loadSettings()

if base.win == None:
    print 'Unable to open window; aborting.'
    sys.exit()
    
launcher.setPandaErrorCode(0)
launcher.setPandaWindowOpen()

localizerAgent.startTask()

ConfigVariableDouble('decompressor-step-time').setValue(0.01)
ConfigVariableDouble('extractor-step-time').setValue(0.01)

# loading screen
backgroundNodePath = aspect2d.attachNewNode(backgroundNode, 0)
backgroundNodePath.setPos(0.0, 0.0, 0.0)
backgroundNodePath.setScale(render2d, VBase3(1))
backgroundNodePath.find('**/bg').setBin('fixed', 10)

# change the logo
backgroundNodePath.find('**/fg').stash()

from direct.gui.DirectGui import OnscreenImage
logo = OnscreenImage('phase_3/maps/toontown-logo-new.png')
logo.reparentTo(backgroundNodePath)
logo.setBin('fixed', 20)
logo.setTransparency(TransparencyAttrib.MAlpha)
logo.setScale(.8, 1, .7)

base.graphicsEngine.renderFrame()

# default DGG stuff
DirectGuiGlobals.setDefaultRolloverSound(base.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
DirectGuiGlobals.setDefaultClickSound(base.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel('phase_3/models/gui/dialog_box_gui'))

# localizer
import TTLocalizer
from otp.otpbase import OTPGlobals
OTPGlobals.setDefaultProductPrefix(TTLocalizer.ProductPrefix)

# loading music
music = None
if base.musicManagerIsValid:
    music = base.musicManager.getSound('phase_3/audio/bgm/tt_theme.ogg')
    if music:
        music.setLoop(1)
        music.setVolume(0.9)
        music.play()

# loader
import ToontownLoader
from direct.gui.DirectGui import *
serverVersion = base.config.GetString('server-version', 'no_version_set')
version = OnscreenText(serverVersion, pos=(-1.3, -0.975), scale=0.06, fg=Vec4(0, 0, 1, 0.6), align=TextNode.ALeft)
loader.beginBulkLoad('init', TTLocalizer.LoaderLabel, 50, 0, TTLocalizer.TIP_NONE)

ad = localizerAgent.getAd()
if ad:
    ad.reparentTo(backgroundNodePath)
    ad.setBin('fixed', 20)
    ad.setPos(.35, 1, .45)

from ToonBaseGlobal import *
from direct.showbase.MessengerGlobal import *

# cr
from toontown.distributed import ToontownClientRepository
cr = ToontownClientRepository.ToontownClientRepository(serverVersion, launcher)
cr.setDeferInterval(1)
cr.music = music
del music
base.initNametagGlobals()
base.cr = cr
loader.endBulkLoad('init')

# friend mgr
from otp.friends import FriendManager
from otp.distributed.OtpDoGlobals import *
cr.generateGlobalObject(OTP_DO_ID_FRIEND_MANAGER, 'FriendManager')

# start
base.startShow(cr)

# cleanup
backgroundNodePath.reparentTo(hidden)
backgroundNodePath.removeNode()
del backgroundNodePath
del backgroundNode
del tempLoader
del logo
version.cleanup()
del version

try:
    run()
    
except SystemExit:
    try:
        __nirai__
    
    except:
        raise SystemExit
    
except KeyboardInterrupt:
    raise
    
except:
    try:
        base.cr.timeManager.setDisconnectReason(3)
    
    except:
        pass
        
    raise
    
