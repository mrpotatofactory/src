#coding: latin-1
import setup

from direct.stdpy import threading, thread
import sys

defaultText = '''
base.cr.currSuitPlanner.showPaths()
'''

defaultText = '''
from panda3d.core import *
n = CollisionNode('n')
n.addSolid(CollisionSphere(0, 0, 0, 1))
np = render.attachNewNode(n)
np.show()
'''

defaultText = '''
from toontown.makeatoon.CustomStatePanel import *
p = CustomStatePanel()
'''

defaultText = '''
zones = [2649, 1834, 5620, 4835, 3707, 9619]
index = 0

def next(task=None):
    global index
    messenger.send('SCStaticTextMsg', [10003])
    if index >= len(zones):
        print 'ALL DONE'
        if task:
            return task.done
        return
        
    base.cr.sendSetLocation(localAvatar.doId, localAvatar.defaultShard, zones[index])
    index += 1
        
    if task:
        return task.again
    
next()
base.cr.scvMgr.triggerDelay = 0
taskMgr.doMethodLater(1, next, 'nextzone')
'''

defaultText = '''
from toontown.uberdog.TopToonsGlobals import *
import time
for i in xrange(20):
    c = getChallenge(i * time.time())
    print i, c.quest.getDefaultQuestDialog(), c.challengeType, c.reward, 'jellybeans'
'''

defaultText = '''
class Avatar:
    def __init__(self):
        self.quests = [5205, 1000, 1000, 101, 0, 5207, 1000, 1000, 100, 0]
        
    def getQuests(self):
        return self.quests
        
    def b_setQuests(self, q):
        self.quests = sum(q, [])
        
from toontown.ai.QuestManagerAI import *
m = QuestManagerAI(None)
av = Avatar()
print m.toonCaughtFishingItem(av)
print av.getQuests()
'''

defaultText = '''class Avatar:
    def __init__(self):
        self.quests = [5205, 1000, 1000, 101, 0, 5207, 1000, 1000, 100, 0]

    def getNpcId(self): return hash(self)
    getDoId = getNpcId   
   
    def getGameAccess(self): return 2
    def getRewardTier(self): return self.getRewardHistory()[0]
    def getQuestHistory(self): return  self.getRewardHistory()[1]

    def getRewardHistory(self):
        return PRE_ELDER_TIER, []
        
from toontown.quest.Quests import *
av = Avatar()
print chooseBestQuests(PRE_ELDER_TIER, av, av)
'''

defaultText = '''
door = base.cr.doFind('DistributedDoor')
t = door.getTrigger()
t.show()
'''

defaultText = '''
from panda3d.core import *

tunnel = render.find('**/toph_*_2301')
origin = tunnel.find('**/*origin')
sphere = origin.attachNewNode(CollisionNode('sp'))
sphere.node().addSolid(CollisionSphere(0, 0, 0, 1))
sphere.show()
'''

defaultText = '''
localAvatar.setDisguisePageFlag(1)
localAvatar.hoodsVisited.append(10000)
'''

defaultText = '''
av = base.cr.friendsMap.values()[0]
localAvatar.setTalkWhisper(av.doId, 0, av.getName(), 'rthkij 3rogkgj 4pflp f5f', [], 0)
'''

defaultText = '''
from direct.showbase.ShadowDemo import arbitraryShadow as ASH
from toontown.suit.DistributedSuit import *

def thetask(task):
 for cog in base.cr.doFindAllInstances(DistributedSuit):
   if not hasattr(cog, 'SH'): cog.SH = ASH(cog)

 return task.cont

taskMgr.add(thetask, 'thetask')
'''

def runInjectorCode_tk():
        global text
        try:
            exec (text.get(1.0, "end"),globals())
        except Exception, e: print e

def openInjector_tk():
    import Tkinter as tk
    from direct.stdpy import thread
    root = tk.Tk()
    root.geometry('600x400')
    root.title('Cogtown (TTN version) Injector')
    root.resizable(False, False)
    global text
    frame = tk.Frame(root)
    text = tk.Text(frame,width=70,height=20)

    text.insert(1.0, defaultText)

    text.pack(side="left")
    tk.Button(root,text="Inject!",command=runInjectorCode_tk).pack()
    scroll = tk.Scrollbar(frame)
    scroll.pack(fill="y",side="right")
    scroll.config(command=text.yview)
    text.config(yscrollcommand=scroll.set)
    frame.pack(fill="y")

    thread.start_new_thread(root.mainloop,())


##################################################
#wx version

def __inject_wx(_):
    code = textbox.GetValue()
    exec (code, globals())

def openInjector_wx():
    import wx
    
    app = wx.App(redirect = False)
        
    frame = wx.Frame(None, title = "TTN Injector", size=(640, 400), style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
    panel = wx.Panel(frame)
    button = wx.Button(parent = panel, id = -1, label = "Inject", size = (50, 20), pos = (295, 0))
    global textbox
    textbox = wx.TextCtrl(parent = panel, id = -1, pos = (20, 22), size = (600, 340), style = wx.TE_MULTILINE)
    frame.Bind(wx.EVT_BUTTON, __inject_wx, button)

    frame.Show()
    app.SetTopWindow(frame)
    
    textbox.AppendText(defaultText)
    
    threading.Thread(target = app.MainLoop).start()
    
def handleInstallInjector():
    if not '-inj' in sys.argv:
        return
        
    injType = sys.argv[sys.argv.index('-inj') + 1].lower()

    if injType == "wx":
        openInjector_wx()
        
    elif injType == "tk":
        openInjector_tk()
        
    else:
        raise ValueError('Invalid injector config: %s. Must be "wx" or "tk"!' % injType)
            
handleInstallInjector()

import toontown.toonbase.ToontownStart
