from direct.interval.IntervalGlobal import *
from pandac.PandaModules import *
from direct.directnotify import DirectNotifyGlobal
from direct.showbase import DirectObject
from toontown.toon import ToonHeadFrame
from toontown.char import CharDNA
from toontown.suit import SuitDNA
from toontown.char import Char
from toontown.suit import Suit
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownBattleGlobals
from otp.speedchat import SpeedChatGlobals
from toontown.ai import DistributedBlackCatMgr
from otp.nametag.NametagConstants import *
import BlinkingArrows

notify = DirectNotifyGlobal.directNotify.newCategory('QuestParser')
lineDict = {}
globalVarDict = {}
curId = None

data = '''
ID reward_100
SHOW laffMeter
LERP_POS laffMeter 0 0 0 1
LERP_SCALE laffMeter 0.2 0.2 0.2 1
WAIT 1.5
ADD_LAFFMETER 1
WAIT 1
LERP_POS laffMeter -1.18 0 -0.87 1
LERP_SCALE laffMeter 0.075 0.075 0.075 1
WAIT 1
FINISH_QUEST_MOVIE

ID tutorial_mickey
LOAD_SFX soundRun "phase_3.5/audio/sfx/AV_footstep_runloop.ogg"
LOAD_DIALOGUE mickeyTutorialDialogue_4 "phase_3.5/audio/dial/CC_tom_tutorial_mickey02.ogg"
LOCK_LOCALTOON
REPARENTTO camera render
POSHPRSCALE camera 11 7 3 52 0 0 1 1 1
POS localToon 0 0 0
HPR localToon 0 0 0
WAIT 2
PLAY_SFX soundRun 1
LOOP_ANIM localToon "run"
LERP_POS localToon -1.8 14.4 0 2
WAIT 2
#LERP_HPR localToon -110 0 0 0.5
LERP_HPR localToon -70 0 0 0.5
WAIT 0.5
STOP_SFX soundRun
LOOP_ANIM localToon "neutral"
STOP_SFX soundRun
#CHAT npc QuestScriptTutorialMickey_4 mickeyTutorialDialogue_4
REPARENTTO camera localToon
POS localToon 1.6 9.8 0
HPR localToon 14 0 0
FREE_LOCALTOON
LOCAL_CHAT_PERSIST npc QuestScriptTutorialMickey_4 mickeyTutorialDialogue_4

ID quest_assign_101
CLEAR_CHAT npc
LOAD squirt1 "phase_3.5/models/gui/tutorial_gui" "squirt1"
LOAD squirt2 "phase_3.5/models/gui/tutorial_gui" "squirt2"
LOAD toonBuilding "phase_3.5/models/gui/tutorial_gui" "toon_buildings"
LOAD cogBuilding "phase_3.5/models/gui/tutorial_gui" "suit_buildings"
LOAD cogs "phase_3.5/models/gui/tutorial_gui" "suits"
LOAD tart "phase_3.5/models/props/tart"
LOAD flower "phase_3.5/models/props/squirting-flower"
LOAD_DIALOGUE tomDialogue_01 "phase_3.5/audio/dial/CC_tom_tutorial_questscript01.ogg"
LOAD_DIALOGUE tomDialogue_02 "phase_3.5/audio/dial/CC_tom_tutorial_questscript03.ogg"
LOAD_DIALOGUE tomDialogue_03 "phase_3.5/audio/dial/CC_tom_tutorial_questscript04.ogg"
LOAD_DIALOGUE tomDialogue_04 "phase_3.5/audio/dial/CC_tom_tutorial_questscript05.ogg"
LOAD_DIALOGUE tomDialogue_05 "phase_3.5/audio/dial/CC_tom_tutorial_questscript06.ogg"
LOAD_DIALOGUE tomDialogue_06 "phase_3.5/audio/dial/CC_tom_tutorial_questscript07.ogg"
LOAD_DIALOGUE tomDialogue_07 "phase_3.5/audio/dial/CC_tom_tutorial_questscript08.ogg"
LOAD_DIALOGUE tomDialogue_08 "phase_3.5/audio/dial/CC_tom_tutorial_questscript09.ogg"
LOAD_DIALOGUE tomDialogue_09 "phase_3.5/audio/dial/CC_tom_tutorial_questscript10.ogg"
LOAD_DIALOGUE tomDialogue_10 "phase_3.5/audio/dial/CC_tom_tutorial_questscript11.ogg"
LOAD_DIALOGUE tomDialogue_11 "phase_3.5/audio/dial/CC_tom_tutorial_questscript12.ogg"
LOAD_DIALOGUE tomDialogue_12 "phase_3.5/audio/dial/CC_tom_tutorial_questscript13.ogg"
LOAD_DIALOGUE tomDialogue_13 "phase_3.5/audio/dial/CC_tom_tutorial_questscript14.ogg"
LOAD_DIALOGUE tomDialogue_14 "phase_3.5/audio/dial/CC_tom_tutorial_questscript16.ogg"
POSHPRSCALE cogs -1.05 7 0 0 0 0 1 1 1
POSHPRSCALE toonBuilding -1.05 7 0 0 0 0 1.875 1.875 1.875
POSHPRSCALE cogBuilding -1.05 7 0 0 0 0 1.875 1.875 1.875
POSHPRSCALE squirt1 -1.05 7 0 0 0 0 1.875 1.875 1.875
POSHPRSCALE squirt2 -1.05 7 0 0 0 0 1.875 1.875 1.875
REPARENTTO camera npc
POS camera -2.2 5.2 3.3
HPR camera 215 5 0
WRTREPARENTTO camera localToon
PLAY_ANIM npc "right-hand-start" 1
WAIT 1
REPARENTTO cogs camera
LERP_SCALE cogs 1.875 1.875 1.875 0.5
WAIT 1.0833
LOOP_ANIM npc "right-hand" 1
FUNCTION npc "angryEyes"
FUNCTION npc "blinkEyes"
LOCAL_CHAT_CONFIRM npc QuestScript101_1 "CFReversed" tomDialogue_01
LOCAL_CHAT_CONFIRM npc QuestScript101_2 "CFReversed" tomDialogue_02
REPARENTTO cogs hidden
REPARENTTO toonBuilding camera
LOCAL_CHAT_CONFIRM npc QuestScript101_3 "CFReversed" tomDialogue_03
REPARENTTO toonBuilding hidden
REPARENTTO cogBuilding camera
FUNCTION npc "sadEyes"
FUNCTION npc "blinkEyes"
LOCAL_CHAT_CONFIRM npc QuestScript101_4 "CFReversed" tomDialogue_04
REPARENTTO cogBuilding hidden
REPARENTTO squirt1 camera
FUNCTION npc "normalEyes"
FUNCTION npc "blinkEyes"
LOCAL_CHAT_CONFIRM npc QuestScript101_5 "CFReversed" tomDialogue_05
REPARENTTO squirt1 hidden
REPARENTTO squirt2 camera
LOCAL_CHAT_CONFIRM npc QuestScript101_6 "CFReversed" tomDialogue_06
PLAY_ANIM npc "right-hand-start" -1.8
LERP_SCALE squirt2 1 1 0.01 0.5
WAIT 0.5
REPARENTTO squirt2 hidden
WAIT 0.6574
LOOP_ANIM npc "neutral" 1
LOCAL_CHAT_CONFIRM npc QuestScript101_7 "CFReversed" tomDialogue_07
# Make it look like the client has no inventory. Since the toon.dc
# specifies that the user really does have 1 of each item, we will 
# just put on a show for the client of not having any items then
# handing them out.
SET_INVENTORY 4 0 0
SET_INVENTORY 5 0 0
REPARENTTO inventory camera
SHOW inventory
SET_INVENTORY_DETAIL -1
POSHPRSCALE inventory -0.77 7.42 1.11 0 0 0 .01 .01 .01
SET_INVENTORY_YPOS 4 0  -.1
SET_INVENTORY_YPOS 5 0  -.1
LERP_SCALE inventory 3 .01 3 1
WAIT 1
REPARENTTO flower npc "**/1000/**/def_joint_right_hold"
POSHPRSCALE flower 0.10 -0.14 0.20 180.00 287.10 168.69 0.70 0.70 0.70
PLAY_ANIM npc "right-hand-start" 1.8
WAIT 1.1574
LOOP_ANIM npc "right-hand" 1.1
WAIT 0.8
WRTREPARENTTO flower camera
LERP_POSHPRSCALE flower -1.75 4.77 0.00 30.00 180.00 16.39 0.75 0.75 0.75 0.589
WAIT 1.094
LERP_POSHPRSCALE flower -1.76 7.42 -0.63 179.96 -89.9 -153.43 0.12 0.12 0.12 1
PLAY_ANIM npc "right-hand-start" -1.5
WAIT 1
ADD_INVENTORY 5 0 1
POSHPRSCALE inventory -0.77 7.42 1.11 0 0 0 3 .01 3
REPARENTTO flower hidden
REPARENTTO tart npc "**/1000/**/def_joint_right_hold"
POSHPRSCALE tart 0.19 0.02 0.00 0.00 0.00 349.38 0.34 0.34 0.34
PLAY_ANIM npc "right-hand-start" 1.8
WAIT 1.1574
LOOP_ANIM npc "right-hand" 1.1
WAIT 0.8
WRTREPARENTTO tart camera
LERP_POSHPRSCALE tart -1.37 4.56 0 329.53 39.81 346.76 0.6 0.6 0.6 0.589
WAIT 1.094
LERP_POSHPRSCALE tart -1.66 7.42 -0.36 0 30 30 0.12 0.12 0.12 1.0
PLAY_ANIM npc "right-hand-start" -1.5
WAIT 1
ADD_INVENTORY 4 0 1
POSHPRSCALE inventory -0.77 7.42 1.11 0 0 0 3 .01 3
REPARENTTO tart hidden
#PLAY_ANIM npc "neutral" 1
#WAIT 2.0833
PLAY_ANIM npc "right-hand-start" 1
WAIT 1.0
HIDE inventory
REPARENTTO inventory hidden
SET_INVENTORY_YPOS 4 0  0
SET_INVENTORY_YPOS 5 0  0
SET_INVENTORY_DETAIL 0
POSHPRSCALE inventory 0 0 0 0 0 0 1 1 1
OBSCURE_LAFFMETER 0
SHOW laffMeter
POS laffMeter 0.153 0.0 0.13
SCALE laffMeter 0.0 0.0 0.0
WRTREPARENTTO laffMeter aspect2d
LERP_POS laffMeter -0.25 0 -0.15 1
LERP_SCALE laffMeter 0.2 0.2 0.2 0.6
WAIT 1.0833
LOOP_ANIM npc "right-hand"
LOCAL_CHAT_CONFIRM npc QuestScript101_8 "CFReversed" tomDialogue_08
LOCAL_CHAT_CONFIRM npc QuestScript101_9 "CFReversed" tomDialogue_09
FUNCTION npc "sadEyes"
FUNCTION npc "blinkEyes"
LAFFMETER 15 15
WAIT 0.1
LAFFMETER 14 15
WAIT 0.1
LAFFMETER 13 15
WAIT 0.1
LAFFMETER 12 15
WAIT 0.1
LAFFMETER 11 15
WAIT 0.1
LAFFMETER 10 15
WAIT 0.1
LAFFMETER 9 15
WAIT 0.1
LAFFMETER 8 15
WAIT 0.1
LAFFMETER 7 15
WAIT 0.1
LAFFMETER 6 15
WAIT 0.1
LAFFMETER 5 15
WAIT 0.1
LAFFMETER 4 15
WAIT 0.1
LAFFMETER 3 15
WAIT 0.1
LAFFMETER 2 15
WAIT 0.1
LAFFMETER 1 15
WAIT 0.1
LAFFMETER 0 15
LOCAL_CHAT_CONFIRM npc QuestScript101_10 "CFReversed" tomDialogue_10
FUNCTION npc "normalEyes"
FUNCTION npc "blinkEyes"
LAFFMETER 15 15
WRTREPARENTTO laffMeter a2dBottomLeft
WAIT 0.5
LERP_POS laffMeter 0.153 0.0 0.13 0.6
LERP_SCALE laffMeter 0.075 0.075 0.075 0.6
PLAY_ANIM npc "right-hand-start" -2
WAIT 1.0625
LOOP_ANIM npc "neutral"
WAIT 0.5
LERP_HPR npc -50 0 0 0.5
FUNCTION npc "surpriseEyes"
FUNCTION npc "showSurpriseMuzzle"
PLAY_ANIM npc "right-point-start" 1.5
WAIT 0.6944
LOOP_ANIM npc "right-point"
LOCAL_CHAT_CONFIRM npc QuestScript101_11 "CFReversed" tomDialogue_11
LOCAL_CHAT_CONFIRM npc QuestScript101_12 "CFReversed" tomDialogue_12
PLAY_ANIM npc "right-point-start" -1
LERP_HPR npc -0.068 0 0 0.75
WAIT 1.0417
FUNCTION npc "angryEyes"
FUNCTION npc "blinkEyes"
FUNCTION npc "hideSurpriseMuzzle"
LOOP_ANIM npc "neutral"
FUNCTION localToon "questPage.showQuestsOnscreenTutorial"
LOCAL_CHAT_CONFIRM npc QuestScript101_13 "CFReversed" tomDialogue_13
FUNCTION localToon "questPage.hideQuestsOnscreenTutorial"
LOCAL_CHAT_CONFIRM npc QuestScript101_14 1 "CFReversed" tomDialogue_14
FUNCTION npc "normalEyes"
FUNCTION npc "blinkEyes"
# Cleanup
UPON_TIMEOUT FUNCTION tart "removeNode"
UPON_TIMEOUT FUNCTION flower "removeNode"
UPON_TIMEOUT FUNCTION cogs "removeNode"
UPON_TIMEOUT FUNCTION toonBuilding "removeNode"
UPON_TIMEOUT FUNCTION cogBuilding "removeNode"
UPON_TIMEOUT FUNCTION squirt1 "removeNode"
UPON_TIMEOUT FUNCTION squirt2 "removeNode"
UPON_TIMEOUT LOOP_ANIM npc "neutral"
UPON_TIMEOUT HIDE inventory
UPON_TIMEOUT SET_INVENTORY_DETAIL 0
UPON_TIMEOUT SHOW laffMeter
UPON_TIMEOUT REPARENTTO laffMeter a2dBottomLeft
UPON_TIMEOUT POS laffMeter 0.15 0 0.13
UPON_TIMEOUT SCALE laffMeter 0.075 0.075 0.075
UPON_TIMEOUT POSHPRSCALE inventory 0 0 0 0 0 0 1 1 1
POS localToon 0.776 14.6 0
HPR localToon 47.5 0 0
FINISH_QUEST_MOVIE


ID quest_incomplete_110
LOAD_DIALOGUE harryDialogue_01 "phase_3.5/audio/dial/CC_harry_tutorial_questscript01.ogg"
LOAD_DIALOGUE harryDialogue_02 "phase_3.5/audio/dial/CC_harry_tutorial_questscript02.ogg"
LOAD_DIALOGUE harryDialogue_03 "phase_3.5/audio/dial/CC_harry_tutorial_questscript03.ogg"
LOAD_DIALOGUE harryDialogue_04 "phase_3.5/audio/dial/CC_harry_tutorial_questscript04.ogg"
LOAD_DIALOGUE harryDialogue_05 "phase_3.5/audio/dial/CC_harry_tutorial_questscript05.ogg"
LOAD_DIALOGUE harryDialogue_06 "phase_3.5/audio/dial/CC_harry_tutorial_questscript06.ogg"
LOAD_DIALOGUE harryDialogue_07 "phase_3.5/audio/dial/CC_harry_tutorial_questscript07.ogg"
LOAD_DIALOGUE harryDialogue_08 "phase_3.5/audio/dial/CC_harry_tutorial_questscript08.ogg"
LOAD_DIALOGUE harryDialogue_09 "phase_3.5/audio/dial/CC_harry_tutorial_questscript09.ogg"
LOAD_DIALOGUE harryDialogue_10 "phase_3.5/audio/dial/CC_harry_tutorial_questscript10.ogg"
LOAD_DIALOGUE harryDialogue_11 "phase_3.5/audio/dial/CC_harry_tutorial_questscript11.ogg"
SET_MUSIC_VOLUME 0.4 activityMusic 0.5 0.7
LOCAL_CHAT_CONFIRM npc QuestScript110_1 harryDialogue_01
OBSCURE_BOOK 0
REPARENTTO bookOpenButton aspect2d
SHOW bookOpenButton
POS bookOpenButton 0 0 0
SCALE bookOpenButton 0.5 0.5 0.5
LERP_COLOR_SCALE bookOpenButton 1 1 1 0 1 1 1 1 0.5
WRTREPARENTTO bookOpenButton a2dBottomRight
WAIT 1.5
LERP_POS bookOpenButton -0.158 0 0.17 1
LERP_SCALE bookOpenButton 0.305 0.305 0.305 1
WAIT 1
LOCAL_CHAT_CONFIRM npc QuestScript110_2 harryDialogue_02
REPARENTTO arrows a2dBottomRight
ARROWS_ON -0.41 0.11 0 -0.11 0.36 90
LOCAL_CHAT_PERSIST npc QuestScript110_3 harryDialogue_03
WAIT_EVENT "enterStickerBook"
ARROWS_OFF
SHOW_BOOK
HIDE bookPrevArrow
HIDE bookNextArrow
CLEAR_CHAT npc
WAIT 0.5
TOON_HEAD npc -0.2 -0.45 1
LOCAL_CHAT_CONFIRM npc QuestScript110_4 harryDialogue_04
REPARENTTO arrows aspect2d
ARROWS_ON 0.85 -0.75 -90 0.85 -0.75 -90
SHOW bookNextArrow
LOCAL_CHAT_PERSIST npc QuestScript110_5 harryDialogue_05
WAIT_EVENT "stickerBookPageChange-3"
HIDE bookPrevArrow
HIDE bookNextArrow
ARROWS_OFF
CLEAR_CHAT npc
WAIT 0.5
LOCAL_CHAT_CONFIRM npc QuestScript110_6 harryDialogue_06
ARROWS_ON 0.85 -0.75 -90 0.85 -0.75 -90
SHOW bookNextArrow
LOCAL_CHAT_PERSIST npc QuestScript110_7 harryDialogue_07
WAIT_EVENT "stickerBookPageChange-4"
HIDE bookNextArrow
HIDE bookPrevArrow
ARROWS_OFF
CLEAR_CHAT npc
LOCAL_CHAT_CONFIRM npc QuestScript110_8 harryDialogue_08
LOCAL_CHAT_CONFIRM npc QuestScript110_9 harryDialogue_09
LOCAL_CHAT_PERSIST npc QuestScript110_10 harryDialogue_10
ENABLE_CLOSE_BOOK
REPARENTTO arrows a2dBottomRight
ARROWS_ON -0.41 0.11 0 -0.11 0.36 90
WAIT_EVENT "exitStickerBook"
ARROWS_OFF
TOON_HEAD npc 0 0 0
HIDE_BOOK
HIDE bookOpenButton
LOCAL_CHAT_CONFIRM npc QuestScript110_11 1 harryDialogue_11
SET_MUSIC_VOLUME 0.7 activityMusic 1.0 0.4
# Lots of cleanup
UPON_TIMEOUT OBSCURE_BOOK 0
UPON_TIMEOUT ARROWS_OFF
UPON_TIMEOUT REPARENTTO arrows aspect2d
UPON_TIMEOUT HIDE_BOOK
UPON_TIMEOUT COLOR_SCALE bookOpenButton 1 1 1 1
UPON_TIMEOUT POS bookOpenButton -0.158 0 0.17
UPON_TIMEOUT SCALE bookOpenButton 0.305 0.305 0.305
UPON_TIMEOUT TOON_HEAD npc 0 0 0
UPON_TIMEOUT SHOW bookOpenButton
FINISH_QUEST_MOVIE

ID tutorial_blocker
LOAD_DIALOGUE blockerDialogue_01 "phase_3.5/audio/dial/CC_flippy_tutorial_blocker01.ogg"
LOAD_DIALOGUE blockerDialogue_02 "phase_3.5/audio/dial/CC_flippy_tutorial_blocker02.ogg"
LOAD_DIALOGUE blockerDialogue_03 "phase_3.5/audio/dial/CC_flippy_tutorial_blocker03.ogg"
LOAD_DIALOGUE blockerDialogue_04 "phase_3.5/audio/dial/CC_flippy_tutorial_blocker04.ogg"
LOAD_DIALOGUE blockerDialogue_05a "phase_3.5/audio/dial/CC_flippy_tutorial_blocker05.ogg"
LOAD_DIALOGUE blockerDialogue_05b "phase_3.5/audio/dial/CC_flippy_tutorial_blocker06.ogg"
LOAD_DIALOGUE blockerDialogue_06 "phase_3.5/audio/dial/CC_flippy_tutorial_blocker07.ogg"
LOAD_DIALOGUE blockerDialogue_07 "phase_3.5/audio/dial/CC_flippy_tutorial_blocker08.ogg"
LOAD_DIALOGUE blockerDialogue_08 "phase_3.5/audio/dial/CC_flippy_tutorial_blocker09.ogg"
HIDE localToon
REPARENTTO camera npc
FUNCTION npc "stopLookAround"
POS camera 0.0 6.0 4.0
HPR camera 180.0 0.0 0.0
SET_MUSIC_VOLUME 0.4 music 0.5 0.8
LOCAL_CHAT_CONFIRM npc QuestScriptTutorialBlocker_1 blockerDialogue_01
WAIT 0.8 
LOCAL_CHAT_CONFIRM npc QuestScriptTutorialBlocker_2 blockerDialogue_02
WAIT 0.8 
POS camera -5.0 -9.0 6.0
HPR camera -25.0 -10.0 0.0
POS localToon 203.8 18.64 -0.475
HPR localToon -90.0 0.0 0.0
SHOW localToon
LOCAL_CHAT_CONFIRM npc QuestScriptTutorialBlocker_3 blockerDialogue_03
OBSCURE_CHAT 1 0
REPARENTTO chatScButton aspect2d
SHOW chatScButton
POS chatScButton -0.3 0 -0.1
SCALE chatScButton 2.0 2.0 2.0
LERP_COLOR_SCALE chatScButton 1 1 1 0 1 1 1 1 0.5
WRTREPARENTTO chatScButton a2dTopLeft
WAIT 0.5
LERP_POS chatScButton 0.204 0 -0.072 0.6
LERP_SCALE chatScButton 1.179 1.179 1.179 0.6
WAIT 0.6 
REPARENTTO arrows a2dTopLeft
ARROWS_ON 0.41 -0.09 180 0.21 -0.26 -90
LOCAL_CHAT_PERSIST npc QuestScriptTutorialBlocker_4 blockerDialogue_04
WAIT_EVENT "enterSpeedChat"
ARROWS_OFF
BLACK_CAT_LISTEN 1
WAIT_EVENT "SCChatEvent"
BLACK_CAT_LISTEN 0
WAIT 0.5
CLEAR_CHAT localToon
REPARENTTO camera localToon
LOCAL_CHAT_CONFIRM npc QuestScriptTutorialBlocker_5 "CFReversed" blockerDialogue_05a blockerDialogue_05b
LOCAL_CHAT_CONFIRM npc QuestScriptTutorialBlocker_6 "CFReversed" blockerDialogue_06
OBSCURE_CHAT 0 0
REPARENTTO chatNormalButton aspect2d
SHOW chatNormalButton
POS chatNormalButton -0.3 0 -0.1
SCALE chatNormalButton 2.0 2.0 2.0
LERP_COLOR_SCALE chatNormalButton 1 1 1 0 1 1 1 1 0.5
WAIT 0.5
WRTREPARENTTO chatNormalButton a2dTopLeft
LERP_POS chatNormalButton 0.068 0 -0.072 0.6
LERP_SCALE chatNormalButton 1.179 1.179 1.179 0.6
WAIT 0.6 
LOCAL_CHAT_CONFIRM npc QuestScriptTutorialBlocker_7 "CFReversed" blockerDialogue_07
LOCAL_CHAT_CONFIRM npc QuestScriptTutorialBlocker_8 1 "CFReversed" blockerDialogue_08
SET_MUSIC_VOLUME 0.8 music 1.0 0.4
LOOP_ANIM npc "walk"
LERP_HPR npc 270 0 0 0.5
WAIT 0.5
LOOP_ANIM npc "run"
LERP_POS npc 217.4 18.81 -0.475 0.75 
LERP_HPR npc 240 0 0 0.75 
WAIT 0.75
LERP_POS npc 222.4 15.0 -0.475 0.35
LERP_HPR npc 180 0 0 0.35
WAIT 0.35
LERP_POS npc 222.4 5.0 -0.475 0.75
WAIT 0.75
REPARENTTO npc hidden
FREE_LOCALTOON
UPON_TIMEOUT ARROWS_OFF
UPON_TIMEOUT REPARENTTO arrows aspect2d
UPON_TIMEOUT POS chatScButton 0.204 0 -0.072
UPON_TIMEOUT SCALE chatScButton 1.179 1.179 1.179 
UPON_TIMEOUT POS chatNormalButton 0.068 0 -0.072
UPON_TIMEOUT SCALE chatNormalButton 1.179 1.179 1.179 
UPON_TIMEOUT OBSCURE_CHAT 0 0 
UPON_TIMEOUT REPARENTTO camera localToon
FINISH_QUEST_MOVIE

ID gag_intro
SEND_EVENT "disableGagPanel"
SEND_EVENT "disableBackToPlayground"
HIDE inventory
TOON_HEAD npc 0 0 1
WAIT .1
# Welcome to the Gag Shop!
LOCAL_CHAT_CONFIRM npc QuestScriptGagShop_1
LERP_POS npcToonHead -.64 0 -.74 .7
LERP_SCALE npcToonHead .82 .82 .82 .7
LERP_COLOR_SCALE purchaseBg 1 1 1 1  .6 .6 .6 1 .7
WAIT .7
SHOW inventory
LOCAL_CHAT_CONFIRM npc QuestScriptGagShop_1a
## here's your jb jar
#ARROWS_ON -1.22 0.09 0 -.93 -.2 -90 
#LOCAL_CHAT_CONFIRM npc QuestScriptGagShop_2
#ARROWS_OFF
# try buying a gag
ARROWS_ON -0.19 0.04 180 -0.4 0.26 90
LOCAL_CHAT_PERSIST npc QuestScriptGagShop_3
SEND_EVENT "enableGagPanel"
WAIT_EVENT "inventory-selection"
ARROWS_OFF
CLEAR_CHAT npc
WAIT .5
LOCAL_CHAT_CONFIRM npc QuestScriptGagShop_4
# show advanced throw & squirt gags
LOCAL_CHAT_PERSIST npc QuestScriptGagShop_5
WAIT .5
SHOW_THROW_SQUIRT_PREVIEW
CLEAR_CHAT npc
WAIT .5
# show "Exit Back To Playground" button
SET_BIN backToPlaygroundButton "gui-popup"
LERP_POS backToPlaygroundButton -.12 0 .18 .5
LERP_SCALE backToPlaygroundButton 2 2 2 .5
LERP_COLOR_SCALE backToPlaygroundButton 1 1 1 1  2.78 2.78 2.78 1 .5
LERP_COLOR_SCALE inventory 1 1 1 1  .6 .6 .6 1 .5
WAIT .5
START_THROB backToPlaygroundButton 2.78 2.78 2.78 1  2.78 2.78 2.78 .7  2
LOCAL_CHAT_CONFIRM npc QuestScriptGagShop_6
STOP_THROB
LERP_POS backToPlaygroundButton .72 0 -.045 .5
LERP_SCALE backToPlaygroundButton 1.04 1.04 1.04 .5
LERP_COLOR_SCALE backToPlaygroundButton 2.78 2.78 2.78 1  1 1 1 1 .5
WAIT .5
CLEAR_BIN backToPlaygroundButton
# show "Play Again" button
SET_BIN playAgainButton "gui-popup"
LERP_POS playAgainButton -.12 0 .18 .5
LERP_SCALE playAgainButton 2 2 2 .5
LERP_COLOR_SCALE playAgainButton 1 1 1 1  2.78 2.78 2.78 1 .5
WAIT .5
START_THROB playAgainButton 2.78 2.78 2.78 1  2.78 2.78 2.78 .7  2
LOCAL_CHAT_CONFIRM npc QuestScriptGagShop_7
STOP_THROB
LERP_POS playAgainButton .72 0 -.24 .5
LERP_SCALE playAgainButton 1.04 1.04 1.04 .5
LERP_COLOR_SCALE playAgainButton 2.78 2.78 2.78 1  1 1 1 1 .5
WAIT .5
CLEAR_BIN playAgainButton
# You're needed in Toon HQ!
LOCAL_CHAT_CONFIRM npc QuestScriptGagShop_8 1
TOON_HEAD npc 0 0 0
LERP_COLOR_SCALE inventory .6 .6 .6 1  1 1 1 1 .5
LERP_COLOR_SCALE purchaseBg .6 .6 .6 1  1 1 1 1 .5
WAIT .5
SEND_EVENT "enableBackToPlayground"
UPON_TIMEOUT TOON_HEAD npc 0 0 0
UPON_TIMEOUT ARROWS_OFF
UPON_TIMEOUT SHOW inventory
UPON_TIMEOUT SEND_EVENT "enableGagPanel"
UPON_TIMEOUT SEND_EVENT "enableBackToPlayground"

ID quest_assign_120
CHAT_CONFIRM npc QuestScript120_1
# ANIM
CHAT_CONFIRM npc QuestScript120_2 1
FINISH_QUEST_MOVIE

ID quest_assign_121
CHAT_CONFIRM npc QuestScript121_1 1
FINISH_QUEST_MOVIE

ID quest_assign_130
CHAT_CONFIRM npc QuestScript130_1 1
FINISH_QUEST_MOVIE

ID quest_assign_131
CHAT_CONFIRM npc QuestScript131_1 1
FINISH_QUEST_MOVIE

ID quest_assign_140
CHAT_CONFIRM npc QuestScript140_1 1
FINISH_QUEST_MOVIE

ID quest_assign_141
CHAT_CONFIRM npc QuestScript141_1 1
FINISH_QUEST_MOVIE

ID quest_assign_145
CHAT_CONFIRM npc QuestScript145_1 1
LOAD frame "phase_4/models/gui/tfa_images" "FrameBlankA"
LOAD tunnel "phase_4/models/gui/tfa_images" "tunnelSignA"
POSHPRSCALE tunnel 0 0 0 0 0 0 0.8 0.8 0.8
REPARENTTO tunnel frame
POSHPRSCALE frame 0 0 0 0 0 0 0.1 0.1 0.1
REPARENTTO frame aspect2d
LERP_SCALE frame 1.0 1.0 1.0 1.0
WAIT 3.0
LERP_SCALE frame 0.1 0.1 0.1 0.5
WAIT 0.5
REPARENTTO frame hidden
CHAT_CONFIRM npc QuestScript145_2 1
UPON_TIMEOUT FUNCTION frame "removeNode"
FINISH_QUEST_MOVIE


ID quest_assign_150
CHAT_CONFIRM npc QuestScript150_1
ARROWS_ON  1.05 0.51 -120 1.05 0.51 -120
SHOW_FRIENDS_LIST
CHAT_CONFIRM npc QuestScript150_2
ARROWS_OFF
HIDE_FRIENDS_LIST
CHAT_CONFIRM npc QuestScript150_3
HIDE bFriendsList
CHAT_CONFIRM npc QuestScript150_4 1
UPON_TIMEOUT HIDE_FRIENDS_LIST
UPON_TIMEOUT ARROWS_OFF
FINISH_QUEST_MOVIE
'''

def init():
    inventoryOrigin = aspect2d.attachNewNode("quest_parser_inventory_origin")
    inventoryOrigin.setPos(.1, 0, -1)
    
    globalVarDict.update({'render': render,
     'camera': camera,
     'hidden': hidden,
     'aspect2d': aspect2d,
     'localToon': base.localAvatar,
     'laffMeter': base.localAvatar.laffMeter,
     'inventory': base.localAvatar.inventory,
     'bFriendsList': base.localAvatar.bFriendsList,
     'book': base.localAvatar.book,
     'bookPrevArrow': base.localAvatar.book.prevArrow,
     'bookNextArrow': base.localAvatar.book.nextArrow,
     'bookOpenButton': base.localAvatar.book.bookOpenButton,
     'bookCloseButton': base.localAvatar.book.bookCloseButton,
     'chatNormalButton': base.localAvatar.chatMgr.normalButton,
     'chatScButton': base.localAvatar.chatMgr.scButton,
     'arrows': BlinkingArrows.BlinkingArrows(),
     'a2dBottomLeft': base.a2dBottomLeft,
     'a2dBottomRight': base.a2dBottomRight,
     'a2dTopLeft': base.a2dTopLeft,
     'inventoryOrigin': inventoryOrigin,
     })

def clear():
    globalVarDict.clear()

def readData():
    global curId
    lines = data.split('\n')
    for line in lines:
        line = line.split('#', 1)[0]
        line = line.strip()
        if not line:
            continue
            
        line = splitTokens(line)
        if line[0] == 'ID':
            parseId(line)
            
        elif curId is None:
            notify.error('Every script must begin with an ID')
            
        else:
            lineDict[curId].append(line)
            
def splitTokens(line):
    line = line.split()
    res = []
    for token in line:
        try: 
            token = int(token)
            
        except:
            try:
                token = float(token)
                
            except:
                token = token.strip('"')
                
        res.append(token)
        
    return res
        
def parseId(line):
    global curId
    curId = line[1]
    notify.debug('Setting current scriptId to: %s' % curId)
    if questDefined(curId):
        notify.error('Already defined scriptId: %s' % curId)
    else:
        lineDict[curId] = []

def questDefined(scriptId):
    res = scriptId in lineDict
    notify.info('questDefined %s: %s' % (scriptId, res))
    return res

class NPCMoviePlayer(DirectObject.DirectObject):

    def __init__(self, scriptId, toon, npc):
        DirectObject.DirectObject.__init__(self)
        self.scriptId = scriptId
        self.toon = toon
        self.isLocalToon = self.toon == base.localAvatar
        self.npc = npc
        self.privateVarDict = {}
        self.toonHeads = {}
        self.chars = []
        self.uniqueId = 'scriptMovie_' + str(self.scriptId) + '_' + str(toon.getDoId()) + '_' + str(npc.getDoId())
        self.setVar('toon', self.toon)
        self.setVar('npc', self.npc)
        self.chapterDict = {}
        self.timeoutTrack = None
        self.currentTrack = None
        return

    def getVar(self, varName):
        if self.privateVarDict.has_key(varName):
            return self.privateVarDict[varName]
        elif globalVarDict.has_key(varName):
            return globalVarDict[varName]
        elif varName.find('tomDialogue') > -1 or varName.find('harryDialogue') > -1:
            notify.warning('%s getting referenced. Tutorial Ack: %d                                  Place: %s' % (varName, base.localAvatar.tutorialAck, base.cr.playGame.hood))
            return None
        else:
            notify.error('Variable not defined: %s' % varName)
        return None

    def delVar(self, varName):
        if self.privateVarDict.has_key(varName):
            del self.privateVarDict[varName]
        elif globalVarDict.has_key(varName):
            del globalVarDict[varName]
        else:
            notify.warning('Variable not defined: %s' % varName)

    def setVar(self, varName, var):
        self.privateVarDict[varName] = var

    def cleanup(self):
        if self.currentTrack:
            self.currentTrack.pause()
            self.currentTrack = None
        self.ignoreAll()
        taskMgr.remove(self.uniqueId)
        for toonHeadFrame in self.toonHeads.values():
            toonHeadFrame.destroy()

        while self.chars:
            self.__unloadChar(self.chars[0])

        del self.toonHeads
        del self.privateVarDict
        del self.chapterDict
        del self.toon
        del self.npc
        del self.timeoutTrack
        return

    def __unloadChar(self, char):
        char.removeActive()
        if char.style.name == 'mk' or char.style.name == 'mn':
            char.stopEarTask()
        char.delete()
        self.chars.remove(char)

    def timeout(self, fFinish = 0):
        if self.timeoutTrack:
            if fFinish:
                self.timeoutTrack.finish()
            else:
                self.timeoutTrack.start()

    def finishMovie(self):
        self.npc.finishMovie(self.toon, self.isLocalToon, 0.0)

    def playNextChapter(self, eventName, timeStamp = 0.0):
        trackList = self.chapterDict[eventName]
        if trackList:
            self.currentTrack = trackList.pop(0)
            self.currentTrack.start()
        else:
            notify.debug('Movie ended waiting for an event (%s)' % eventName)

    def play(self):
        lineNum = 0
        self.currentEvent = 'start'
        lines = lineDict.get(self.scriptId)
        if lines is None:
            notify.error('No movie defined for scriptId: %s' % self.scriptId)
        chapterList = []
        timeoutList = []
        for line in lines:
            lineNum += 1
            command = line[0]
            if command == 'UPON_TIMEOUT':
                uponTimeout = 1
                iList = timeoutList
                line = line[1:]
                command = line[0]
            else:
                uponTimeout = 0
                iList = chapterList
            if command == 'CALL':
                if uponTimeout:
                    self.notify.error('CALL not allowed in an UPON_TIMEOUT')
                iList.append(self.parseCall(line))
                continue
            elif command == 'DEBUG':
                iList.append(self.parseDebug(line))
                continue
            elif command == 'WAIT':
                if uponTimeout:
                    self.notify.error('WAIT not allowed in an UPON_TIMEOUT')
                iList.append(self.parseWait(line))
                continue
            elif command == 'CHAT':
                iList.append(self.parseChat(line))
                continue
            elif command == 'CLEAR_CHAT':
                iList.append(self.parseClearChat(line))
                continue
            elif command == 'FINISH_QUEST_MOVIE':
                chapterList.append(Func(self.finishMovie))
                continue
            elif command == 'CHAT_CONFIRM':
                if uponTimeout:
                    self.notify.error('CHAT_CONFIRM not allowed in an UPON_TIMEOUT')
                avatarName = line[1]
                avatar = self.getVar(avatarName)
                nextEvent = avatar.uniqueName('doneChatPage')
                iList.append(Func(self.acceptOnce, nextEvent, self.playNextChapter, [nextEvent]))
                iList.append(self.parseChatConfirm(line))
                self.closePreviousChapter(iList)
                chapterList = []
                self.currentEvent = nextEvent
                continue
            elif command == 'LOCAL_CHAT_CONFIRM':
                if uponTimeout:
                    self.notify.error('LOCAL_CHAT_CONFIRM not allowed in an UPON_TIMEOUT')
                avatarName = line[1]
                avatar = self.getVar(avatarName)
                nextEvent = avatar.uniqueName('doneChatPage')
                iList.append(Func(self.acceptOnce, nextEvent, self.playNextChapter, [nextEvent]))
                iList.append(self.parseLocalChatConfirm(line))
                self.closePreviousChapter(iList)
                chapterList = []
                self.currentEvent = nextEvent
                continue
            elif command == 'LOCAL_CHAT_PERSIST':
                iList.append(self.parseLocalChatPersist(line))
                continue
            elif command == 'LOCAL_CHAT_TO_CONFIRM':
                if uponTimeout:
                    self.notify.error('LOCAL_CHAT_TO_CONFIRM not allowed in an UPON_TIMEOUT')
                avatarName = line[1]
                avatar = self.getVar(avatarName)
                nextEvent = avatar.uniqueName('doneChatPage')
                iList.append(Func(self.acceptOnce, nextEvent, self.playNextChapter, [nextEvent]))
                iList.append(self.parseLocalChatToConfirm(line))
                self.closePreviousChapter(iList)
                chapterList = []
                self.currentEvent = nextEvent
                continue
            elif command == 'CC_CHAT_CONFIRM':
                if uponTimeout:
                    self.notify.error('CC_CHAT_CONFIRM not allowed in an UPON_TIMEOUT')
                avatarName = line[1]
                avatar = self.getVar(avatarName)
                nextEvent = avatar.uniqueName('doneChatPage')
                iList.append(Func(self.acceptOnce, nextEvent, self.playNextChapter, [nextEvent]))
                iList.append(self.parseCCChatConfirm(line))
                self.closePreviousChapter(iList)
                chapterList = []
                self.currentEvent = nextEvent
                continue
            elif command == 'CC_CHAT_TO_CONFIRM':
                if uponTimeout:
                    self.notify.error('CC_CHAT_TO_CONFIRM not allowed in an UPON_TIMEOUT')
                avatarName = line[1]
                avatar = self.getVar(avatarName)
                nextEvent = avatar.uniqueName('doneChatPage')
                iList.append(Func(self.acceptOnce, nextEvent, self.playNextChapter, [nextEvent]))
                iList.append(self.parseCCChatToConfirm(line))
                self.closePreviousChapter(iList)
                chapterList = []
                self.currentEvent = nextEvent
                continue
            if self.isLocalToon:
                if command == 'LOAD':
                    self.parseLoad(line)
                elif command == 'LOAD_SFX':
                    self.parseLoadSfx(line)
                elif command == 'LOAD_DIALOGUE':
                    self.parseLoadDialogue(line)
                elif command == 'LOAD_CC_DIALOGUE':
                    self.parseLoadCCDialogue(line)
                elif command == 'LOAD_CHAR':
                    self.parseLoadChar(line)
                elif command == 'LOAD_CLASSIC_CHAR':
                    self.parseLoadClassicChar(line)
                elif command == 'UNLOAD_CHAR':
                    iList.append(self.parseUnloadChar(line))
                elif command == 'LOAD_SUIT':
                    self.parseLoadSuit(line)
                elif command == 'SET':
                    self.parseSet(line)
                elif command == 'LOCK_LOCALTOON':
                    iList.append(self.parseLockLocalToon(line))
                elif command == 'FREE_LOCALTOON':
                    iList.append(self.parseFreeLocalToon(line))
                elif command == 'REPARENTTO':
                    iList.append(self.parseReparent(line))
                elif command == 'WRTREPARENTTO':
                    iList.append(self.parseWrtReparent(line))
                elif command == 'SHOW':
                    iList.append(self.parseShow(line))
                elif command == 'HIDE':
                    iList.append(self.parseHide(line))
                elif command == 'POS':
                    iList.append(self.parsePos(line))
                elif command == 'HPR':
                    iList.append(self.parseHpr(line))
                elif command == 'SCALE':
                    iList.append(self.parseScale(line))
                elif command == 'POSHPRSCALE':
                    iList.append(self.parsePosHprScale(line))
                elif command == 'COLOR':
                    iList.append(self.parseColor(line))
                elif command == 'COLOR_SCALE':
                    iList.append(self.parseColorScale(line))
                elif command == 'ADD_LAFFMETER':
                    iList.append(self.parseAddLaffMeter(line))
                elif command == 'LAFFMETER':
                    iList.append(self.parseLaffMeter(line))
                elif command == 'OBSCURE_LAFFMETER':
                    iList.append(self.parseObscureLaffMeter(line))
                elif command == 'ARROWS_ON':
                    iList.append(self.parseArrowsOn(line))
                elif command == 'ARROWS_OFF':
                    iList.append(self.parseArrowsOff(line))
                elif command == 'START_THROB':
                    iList.append(self.parseStartThrob(line))
                elif command == 'STOP_THROB':
                    iList.append(self.parseStopThrob(line))
                elif command == 'SHOW_FRIENDS_LIST':
                    iList.append(self.parseShowFriendsList(line))
                elif command == 'HIDE_FRIENDS_LIST':
                    iList.append(self.parseHideFriendsList(line))
                elif command == 'SHOW_BOOK':
                    iList.append(self.parseShowBook(line))
                elif command == 'HIDE_BOOK':
                    iList.append(self.parseHideBook(line))
                elif command == 'ENABLE_CLOSE_BOOK':
                    iList.append(self.parseEnableCloseBook(line))
                elif command == 'OBSCURE_BOOK':
                    iList.append(self.parseObscureBook(line))
                elif command == 'OBSCURE_CHAT':
                    iList.append(self.parseObscureChat(line))
                elif command == 'ADD_INVENTORY':
                    iList.append(self.parseAddInventory(line))
                elif command == 'SET_INVENTORY':
                    iList.append(self.parseSetInventory(line))
                elif command == 'SET_INVENTORY_YPOS':
                    iList.append(self.parseSetInventoryYPos(line))
                elif command == 'SET_INVENTORY_DETAIL':
                    iList.append(self.parseSetInventoryDetail(line))
                elif command == 'PLAY_SFX':
                    iList.append(self.parsePlaySfx(line))
                elif command == 'STOP_SFX':
                    iList.append(self.parseStopSfx(line))
                elif command == 'PLAY_ANIM':
                    iList.append(self.parsePlayAnim(line))
                elif command == 'LOOP_ANIM':
                    iList.append(self.parseLoopAnim(line))
                elif command == 'LERP_POS':
                    iList.append(self.parseLerpPos(line))
                elif command == 'LERP_HPR':
                    iList.append(self.parseLerpHpr(line))
                elif command == 'LERP_SCALE':
                    iList.append(self.parseLerpScale(line))
                elif command == 'LERP_POSHPRSCALE':
                    iList.append(self.parseLerpPosHprScale(line))
                elif command == 'LERP_COLOR':
                    iList.append(self.parseLerpColor(line))
                elif command == 'LERP_COLOR_SCALE':
                    iList.append(self.parseLerpColorScale(line))
                elif command == 'DEPTH_WRITE_ON':
                    iList.append(self.parseDepthWriteOn(line))
                elif command == 'DEPTH_WRITE_OFF':
                    iList.append(self.parseDepthWriteOff(line))
                elif command == 'DEPTH_TEST_ON':
                    iList.append(self.parseDepthTestOn(line))
                elif command == 'DEPTH_TEST_OFF':
                    iList.append(self.parseDepthTestOff(line))
                elif command == 'SET_BIN':
                    iList.append(self.parseSetBin(line))
                elif command == 'CLEAR_BIN':
                    iList.append(self.parseClearBin(line))
                elif command == 'TOON_HEAD':
                    iList.append(self.parseToonHead(line))
                elif command == 'SEND_EVENT':
                    iList.append(self.parseSendEvent(line))
                elif command == 'FUNCTION':
                    iList.append(self.parseFunction(line))
                elif command == 'BLACK_CAT_LISTEN':
                    iList.append(self.parseBlackCatListen(line))
                elif command == 'FIXMETER':
                    iList.append(self.parseFixMeter(line))
                elif command == 'SHOW_THROW_SQUIRT_PREVIEW':
                    if uponTimeout:
                        self.notify.error('SHOW_THROW_SQUIRT_PREVIEW not allowed in an UPON_TIMEOUT')
                    nextEvent = 'doneThrowSquirtPreview'
                    iList.append(Func(self.acceptOnce, nextEvent, self.playNextChapter, [nextEvent]))
                    iList.append(self.parseThrowSquirtPreview(line))
                    self.closePreviousChapter(iList)
                    chapterList = []
                    self.currentEvent = nextEvent
                elif command == 'WAIT_EVENT':
                    if uponTimeout:
                        self.notify.error('WAIT_EVENT not allowed in an UPON_TIMEOUT')
                    nextEvent = self.parseWaitEvent(line)

                    def proceed(self = self, nextEvent = nextEvent):
                        self.playNextChapter(nextEvent)

                    def handleEvent(*args):
                        proceed = args[0]
                        proceed()

                    iList.append(Func(self.acceptOnce, nextEvent, handleEvent, [proceed]))
                    self.closePreviousChapter(iList)
                    chapterList = []
                    self.currentEvent = nextEvent
                elif command == 'SET_MUSIC_VOLUME':
                    iList.append(self.parseSetMusicVolume(line))
                else:
                    notify.warning('Unknown command token: %s for scriptId: %s on line: %s' % (command, self.scriptId, lineNum))

        self.closePreviousChapter(chapterList)
        if timeoutList:
            self.timeoutTrack = Sequence(*timeoutList)
        self.playNextChapter('start')
        return

    def closePreviousChapter(self, iList):
        trackList = self.chapterDict.setdefault(self.currentEvent, [])
        trackList.append(Sequence(*iList))

    def parseLoad(self, line):
        if len(line) == 3:
            token, varName, modelPath = line
            node = loader.loadModel(modelPath.strip('"'))
        elif len(line) == 4:
            token, varName, modelPath, subNodeName = line
            node = loader.loadModel(modelPath.strip('"')).find('**/' + subNodeName)
        else:
            notify.error('invalid parseLoad command')
        self.setVar(varName, node)

    def parseLoadSfx(self, line):
        token, varName, fileName = line
        sfx = loader.loadSfx(fileName)
        self.setVar(varName, sfx)

    def parseLoadDialogue(self, line):
        token, varName, fileName = line
        if varName == 'tomDialogue_01':
            notify.debug('VarName tomDialogue getting added. Tutorial Ack: %d' % base.localAvatar.tutorialAck)
        if base.config.GetString('language', 'english') == 'japanese':
            dialogue = loader.loadSfx(fileName)
        else:
            dialogue = None
        self.setVar(varName, dialogue)
        return

    def parseLoadCCDialogue(self, line):
        token, varName, filenameTemplate = line
        if self.toon.getStyle().gender == 'm':
            classicChar = 'mickey'
        else:
            classicChar = 'minnie'
        filename = filenameTemplate % classicChar
        if base.config.GetString('language', 'english') == 'japanese':
            dialogue = loader.loadSfx(filename)
        else:
            dialogue = None
        self.setVar(varName, dialogue)
        return

    def parseLoadChar(self, line):
        token, name, charType = line
        char = Char.Char()
        dna = CharDNA.CharDNA()
        dna.newChar(charType)
        char.setDNA(dna)
        if charType == 'mk' or charType == 'mn':
            char.startEarTask()
        char.nametag.manage(base.marginManager)
        char.addActive()
        char.hideName()
        self.setVar(name, char)

    def parseLoadClassicChar(self, line):
        token, name = line
        char = Char.Char()
        dna = CharDNA.CharDNA()
        if self.toon.getStyle().gender == 'm':
            charType = 'mk'
        else:
            charType = 'mn'
        dna.newChar(charType)
        char.setDNA(dna)
        char.startEarTask()
        char.nametag.manage(base.marginManager)
        char.addActive()
        char.hideName()
        self.setVar(name, char)
        self.chars.append(char)

    def parseUnloadChar(self, line):
        token, name = line
        char = self.getVar(name)
        track = Sequence()
        track.append(Func(self.__unloadChar, char))
        track.append(Func(self.delVar, name))
        return track

    def parseLoadSuit(self, line):
        token, name, suitType = line
        suit = Suit.Suit()
        dna = SuitDNA.SuitDNA()
        dna.newSuit(suitType)
        suit.setDNA(dna)
        self.setVar(name, suit)

    def parseSet(self, line):
        token, varName, value = line
        self.setVar(varName, value)

    def parseCall(self, line):
        token, scriptId = line
        nmp = NPCMoviePlayer(scriptId, self.toon, self.npc)
        return Func(nmp.play)

    def parseLockLocalToon(self, line):
        return Sequence(Func(self.toon.detachCamera), Func(self.toon.collisionsOff), Func(self.toon.disableAvatarControls), Func(self.toon.stopTrackAnimToSpeed), Func(self.toon.stopUpdateSmartCamera))

    def parseFreeLocalToon(self, line):
        return Sequence(Func(self.toon.attachCamera), Func(self.toon.startTrackAnimToSpeed), Func(self.toon.collisionsOn), Func(self.toon.enableAvatarControls), Func(self.toon.startUpdateSmartCamera))

    def parseDebug(self, line):
        token, str = line
        return Func(notify.debug, str)

    def parseReparent(self, line):
        if len(line) == 3:
            token, childNodeName, parentNodeName = line
            subNodeName = None
        elif len(line) == 4:
            token, childNodeName, parentNodeName, subNodeName = line
        childNode = self.getVar(childNodeName)
        if subNodeName:
            parentNode = self.getVar(parentNodeName).find(subNodeName)
        else:
            parentNode = self.getVar(parentNodeName)
            
        return ParentInterval(childNode, parentNode)

    def parseWrtReparent(self, line):
        if len(line) == 3:
            token, childNodeName, parentNodeName = line
            subNodeName = None
        elif len(line) == 4:
            token, childNodeName, parentNodeName, subNodeName = line
        childNode = self.getVar(childNodeName)
        if subNodeName:
            parentNode = self.getVar(parentNodeName).find(subNodeName)
        else:
            parentNode = self.getVar(parentNodeName)
        return WrtParentInterval(childNode, parentNode)

    def parseShow(self, line):
        token, nodeName = line
        node = self.getVar(nodeName)
        return Func(node.show)

    def parseHide(self, line):
        token, nodeName = line
        node = self.getVar(nodeName)
        return Func(node.hide)

    def parsePos(self, line):
        token, nodeName, x, y, z = line
        node = self.getVar(nodeName)
        return Func(node.setPos, x, y, z)

    def parseHpr(self, line):
        token, nodeName, h, p, r = line
        node = self.getVar(nodeName)
        return Func(node.setHpr, h, p, r)

    def parseScale(self, line):
        token, nodeName, x, y, z = line
        node = self.getVar(nodeName)
        return Func(node.setScale, x, y, z)

    def parsePosHprScale(self, line):
        token, nodeName, x, y, z, h, p, r, sx, sy, sz = line
        node = self.getVar(nodeName)
        return Func(node.setPosHprScale, x, y, z, h, p, r, sx, sy, sz)

    def parseColor(self, line):
        token, nodeName, r, g, b, a = line
        node = self.getVar(nodeName)
        return Func(node.setColor, r, g, b, a)

    def parseColorScale(self, line):
        token, nodeName, r, g, b, a = line
        node = self.getVar(nodeName)
        return Func(node.setColorScale, r, g, b, a)

    def parseWait(self, line):
        token, waitTime = line
        return Wait(waitTime)

    def parseChat(self, line):
        toonId = self.toon.getDoId()
        avatarName = line[1]
        avatar = self.getVar(avatarName)
        chatString = eval('TTLocalizer.' + line[2])
        chatFlags = CFSpeech | CFTimeout
        quitButton, extraChatFlags, dialogueList = self.parseExtraChatArgs(line[3:])
        if extraChatFlags:
            chatFlags |= extraChatFlags
        if len(dialogueList) > 0:
            dialogue = dialogueList[0]
        else:
            dialogue = None
        return Func(avatar.setChatAbsolute, chatString, chatFlags, dialogue)

    def parseClearChat(self, line):
        toonId = self.toon.getDoId()
        avatarName = line[1]
        avatar = self.getVar(avatarName)
        chatFlags = CFSpeech | CFTimeout
        return Func(avatar.setChatAbsolute, '', chatFlags)

    def parseExtraChatArgs(self, args):
        quitButton = 0
        extraChatFlags = None
        dialogueList = []
        for arg in args:
            if type(arg) == type(0):
                quitButton = arg
            elif type(arg) == type(''):
                if len(arg) > 2 and arg[:2] == 'CF':
                    extraChatFlags = eval(arg)
                else:
                    dialogueList.append(self.getVar(arg))
            else:
                pass
                #notify.error('invalid argument type')

        return (quitButton, extraChatFlags, dialogueList)

    def parseChatConfirm(self, line):
        lineLength = len(line)
        toonId = self.toon.getDoId()
        avatarName = line[1]
        avatar = self.getVar(avatarName)
        chatString = eval('TTLocalizer.' + line[2])
        quitButton, extraChatFlags, dialogueList = self.parseExtraChatArgs(line[3:])
        return Func(avatar.setPageChat, toonId, 0, chatString, quitButton, extraChatFlags, dialogueList)

    def parseLocalChatConfirm(self, line):
        lineLength = len(line)
        avatarName = line[1]
        avatar = self.getVar(avatarName)
        chatString = eval('TTLocalizer.' + line[2])
        quitButton, extraChatFlags, dialogueList = self.parseExtraChatArgs(line[3:])
        return Func(avatar.setLocalPageChat, chatString, quitButton, extraChatFlags, dialogueList)

    def parseLocalChatPersist(self, line):
        lineLength = len(line)
        avatarName = line[1]
        avatar = self.getVar(avatarName)
        chatString = eval('TTLocalizer.' + line[2])
        quitButton, extraChatFlags, dialogueList = self.parseExtraChatArgs(line[3:])
        if len(dialogueList) > 0:
            dialogue = dialogueList[0]
        else:
            dialogue = None
        return Func(avatar.setChatAbsolute, chatString, CFSpeech, dialogue)

    def parseLocalChatToConfirm(self, line):
        lineLength = len(line)
        avatarKey = line[1]
        avatar = self.getVar(avatarKey)
        toAvatarKey = line[2]
        toAvatar = self.getVar(toAvatarKey)
        localizerAvatarName = toAvatar.getName().capitalize()
        toAvatarName = eval('TTLocalizer.' + localizerAvatarName)
        chatString = eval('TTLocalizer.' + line[3])
        chatString = chatString.replace('%s', toAvatarName)
        quitButton, extraChatFlags, dialogueList = self.parseExtraChatArgs(line[4:])
        return Func(avatar.setLocalPageChat, chatString, quitButton, extraChatFlags, dialogueList)

    def parseCCChatConfirm(self, line):
        lineLength = len(line)
        avatarName = line[1]
        avatar = self.getVar(avatarName)
        if self.toon.getStyle().gender == 'm':
            chatString = eval('TTLocalizer.' + line[2] % 'Mickey')
        else:
            chatString = eval('TTLocalizer.' + line[2] % 'Minnie')
        quitButton, extraChatFlags, dialogueList = self.parseExtraChatArgs(line[3:])
        return Func(avatar.setLocalPageChat, chatString, quitButton, extraChatFlags, dialogueList)

    def parseCCChatToConfirm(self, line):
        lineLength = len(line)
        avatarKey = line[1]
        avatar = self.getVar(avatarKey)
        toAvatarKey = line[2]
        toAvatar = self.getVar(toAvatarKey)
        localizerAvatarName = toAvatar.getName().capitalize()
        toAvatarName = eval('TTLocalizer.' + localizerAvatarName)
        if self.toon.getStyle().gender == 'm':
            chatString = eval('TTLocalizer.' + line[3] % 'Mickey')
        else:
            chatString = eval('TTLocalizer.' + line[3] % 'Minnie')
        chatString = chatString.replace('%s', toAvatarName)
        quitButton, extraChatFlags, dialogueList = self.parseExtraChatArgs(line[4:])
        return Func(avatar.setLocalPageChat, chatString, quitButton, extraChatFlags, dialogueList)

    def parsePlaySfx(self, line):
        if len(line) == 2:
            token, sfxName = line
            looping = 0
        elif len(line) == 3:
            token, sfxName, looping = line
        else:
            notify.error('invalid number of arguments')
        sfx = self.getVar(sfxName)
        return Func(base.playSfx, sfx, looping)

    def parseStopSfx(self, line):
        token, sfxName = line
        sfx = self.getVar(sfxName)
        return Func(sfx.stop)

    def parsePlayAnim(self, line):
        if len(line) == 3:
            token, actorName, animName = line
            playRate = 1.0
        elif len(line) == 4:
            token, actorName, animName, playRate = line
        else:
            notify.error('invalid number of arguments')
        actor = self.getVar(actorName)
        return Sequence(Func(actor.setPlayRate, playRate, animName), Func(actor.play, animName))

    def parseLoopAnim(self, line):
        if len(line) == 3:
            token, actorName, animName = line
            playRate = 1.0
        elif len(line) == 4:
            token, actorName, animName, playRate = line
        else:
            notify.error('invalid number of arguments')
        actor = self.getVar(actorName)
        return Sequence(Func(actor.setPlayRate, playRate, animName), Func(actor.loop, animName))

    def parseLerpPos(self, line):
        token, nodeName, x, y, z, t = line
        node = self.getVar(nodeName)
        return Sequence(LerpPosInterval(node, t, Point3(x, y, z), blendType='easeInOut'), duration=0.0)

    def parseLerpHpr(self, line):
        token, nodeName, h, p, r, t = line
        node = self.getVar(nodeName)
        return Sequence(LerpHprInterval(node, t, VBase3(h, p, r), blendType='easeInOut'), duration=0.0)

    def parseLerpScale(self, line):
        token, nodeName, x, y, z, t = line
        node = self.getVar(nodeName)
        return Sequence(LerpScaleInterval(node, t, VBase3(x, y, z), blendType='easeInOut'), duration=0.0)

    def parseLerpPosHprScale(self, line):
        token, nodeName, x, y, z, h, p, r, sx, sy, sz, t = line
        node = self.getVar(nodeName)
        return Sequence(LerpPosHprScaleInterval(node, t, VBase3(x, y, z), VBase3(h, p, r), VBase3(sx, sy, sz), blendType='easeInOut'), duration=0.0)

    def parseLerpColor(self, line):
        token, nodeName, sr, sg, sb, sa, er, eg, eb, ea, t = line
        node = self.getVar(nodeName)
        return Sequence(LerpColorInterval(node, t, VBase4(er, eg, eb, ea), startColorScale=VBase4(sr, sg, sb, sa), blendType='easeInOut'), duration=0.0)

    def parseLerpColorScale(self, line):
        token, nodeName, sr, sg, sb, sa, er, eg, eb, ea, t = line
        node = self.getVar(nodeName)
        return Sequence(LerpColorScaleInterval(node, t, VBase4(er, eg, eb, ea), startColorScale=VBase4(sr, sg, sb, sa), blendType='easeInOut'), duration=0.0)

    def parseDepthWriteOn(self, line):
        token, nodeName, depthWrite = line
        node = self.getVar(nodeName)
        return Sequence(Func(node.setDepthWrite, depthWrite))

    def parseDepthWriteOff(self, line):
        token, nodeName = line
        node = self.getVar(nodeName)
        return Sequence(Func(node.clearDepthWrite))

    def parseDepthTestOn(self, line):
        token, nodeName, depthTest = line
        node = self.getVar(nodeName)
        return Sequence(Func(node.setDepthTest, depthTest))

    def parseDepthTestOff(self, line):
        token, nodeName = line
        node = self.getVar(nodeName)
        return Sequence(Func(node.clearDepthTest))

    def parseSetBin(self, line):
        if len(line) == 3:
            token, nodeName, binName = line
            sortOrder = 0
        else:
            token, nodeName, binName, sortOrder = line
        node = self.getVar(nodeName)
        return Sequence(Func(node.setBin, binName, sortOrder))

    def parseClearBin(self, line):
        token, nodeName = line
        node = self.getVar(nodeName)
        return Sequence(Func(node.clearBin))

    def parseWaitEvent(self, line):
        token, eventName = line
        return eventName

    def parseSendEvent(self, line):
        token, eventName = line
        return Func(messenger.send, eventName)

    def parseFunction(self, line):
        token, objectName, functionName = line
        object = self.getVar(objectName)
        return Func(eval('object.' + functionName))

    def parseAddLaffMeter(self, line):
        token, maxHpDelta = line
        newMaxHp = maxHpDelta + self.toon.getMaxHp()
        newHp = newMaxHp
        laffMeter = self.getVar('laffMeter')
        return Func(laffMeter.adjustFace, newHp, newMaxHp)

    def parseLaffMeter(self, line):
        token, newHp, newMaxHp = line
        laffMeter = self.getVar('laffMeter')
        return Func(laffMeter.adjustFace, newHp, newMaxHp)

    def parseObscureLaffMeter(self, line):
        token, val = line
        return Func(self.toon.laffMeter.obscure, val)

    def parseAddInventory(self, line):
        token, track, level, number = line
        inventory = self.getVar('inventory')
        countSound = loader.loadSfx('phase_3.5/audio/sfx/tick_counter.ogg')
        return Sequence(Func(base.playSfx, countSound), Func(inventory.buttonBoing, track, level), Func(inventory.addItems, track, level, number), Func(inventory.updateGUI, track, level))

    def parseSetInventory(self, line):
        token, track, level, number = line
        inventory = self.getVar('inventory')
        return Sequence(Func(inventory.setItem, track, level, number), Func(inventory.updateGUI, track, level))

    def parseSetInventoryYPos(self, line):
        token, track, level, yPos = line
        inventory = self.getVar('inventory')
        button = inventory.buttons[track][level].stateNodePath[0]
        text = button.find('**/+TextNode')
        return Sequence(Func(text.setY, yPos))

    def parseSetInventoryDetail(self, line):
        if len(line) == 2:
            token, val = line
        elif len(line) == 4:
            token, val, track, level = line
        else:
            notify.error('invalid line for parseSetInventoryDetail: %s' % line)
        inventory = self.getVar('inventory')
        if val == -1:
            return Func(inventory.noDetail)
        elif val == 0:
            return Func(inventory.hideDetail)
        elif val == 1:
            return Func(inventory.showDetail, track, level)
        else:
            notify.error('invalid inventory detail level: %s' % val)

    def parseShowFriendsList(self, line):
        from toontown.friends import FriendsListPanel
        return Func(FriendsListPanel.showFriendsListTutorial)

    def parseHideFriendsList(self, line):
        from toontown.friends import FriendsListPanel
        return Func(FriendsListPanel.hideFriendsListTutorial)

    def parseShowBook(self, line):
        return Sequence(Func(self.toon.book.setPage, self.toon.mapPage), Func(self.toon.book.enter), Func(self.toon.book.disableBookCloseButton))

    def parseEnableCloseBook(self, line):
        return Sequence(Func(self.toon.book.enableBookCloseButton))

    def parseHideBook(self, line):
        return Func(self.toon.book.exit)

    def parseObscureBook(self, line):
        token, val = line
        return Func(self.toon.book.obscureButton, val)

    def parseObscureChat(self, line):
        token, val0, val1 = line
        return Func(self.toon.chatMgr.obscure, val0, val1)

    def parseArrowsOn(self, line):
        arrows = self.getVar('arrows')
        token, x1, y1, h1, x2, y2, h2 = line
        return Func(arrows.arrowsOn, x1, y1, h1, x2, y2, h2)

    def parseArrowsOff(self, line):
        arrows = self.getVar('arrows')
        return Func(arrows.arrowsOff)

    def parseStartThrob(self, line):
        token, nodeName, r, g, b, a, r2, g2, b2, a2, t = line
        node = self.getVar(nodeName)
        startCScale = Point4(r, g, b, a)
        destCScale = Point4(r2, g2, b2, a2)
        self.throbIval = Sequence(LerpColorScaleInterval(node, t / 2.0, destCScale, startColorScale=startCScale, blendType='easeInOut'), LerpColorScaleInterval(node, t / 2.0, startCScale, startColorScale=destCScale, blendType='easeInOut'))
        return Func(self.throbIval.loop)

    def parseStopThrob(self, line):
        return Func(self.throbIval.finish)

    def parseToonHead(self, line):
        if len(line) == 5:
            token, toonName, x, z, toggle = line
            scale = 1.0
        else:
            token, toonName, x, z, toggle, scale = line
        toon = self.getVar(toonName)
        toonId = toon.getDoId()
        toonHeadFrame = self.toonHeads.get(toonId)
        if not toonHeadFrame:
            toonHeadFrame = ToonHeadFrame.ToonHeadFrame(toon)
            toonHeadFrame.tag1Node
            toonHeadFrame.hide()
            self.toonHeads[toonId] = toonHeadFrame
            self.setVar('%sToonHead' % toonName, toonHeadFrame)
        if toggle:
            return Sequence(Func(toonHeadFrame.setPos, x, 0, z), Func(toonHeadFrame.setScale, scale), Func(toonHeadFrame.show))
        else:
            return Func(toonHeadFrame.hide)

    def parseToonHeadScale(self, line):
        token, toonName, scale = line
        toon = self.getVar(toonName)
        toonId = toon.getDoId()
        toonHeadFrame = self.toonHeads.get(toonId)
        return Func(toonHeadFrame.setScale, scale)

    def parseBlackCatListen(self, line):
        token, enable = line
        if enable:

            def phraseSaid(phraseId):
                toontastic = 315
                if phraseId == toontastic:
                    messenger.send(DistributedBlackCatMgr.DistributedBlackCatMgr.ActivateEvent)

            def enableBlackCatListen():
                self.acceptOnce(SpeedChatGlobals.SCStaticTextMsgEvent, phraseSaid)

            return Func(enableBlackCatListen)
        else:

            def disableBlackCatListen():
                self.ignore(SpeedChatGlobals.SCStaticTextMsgEvent)

            return Func(disableBlackCatListen)

    def parseThrowSquirtPreview(self, line):
        oldTrackAccess = [None]

        def grabCurTrackAccess(oldTrackAccess = oldTrackAccess):
            oldTrackAccess[0] = copy.deepcopy(base.localAvatar.getTrackAccess())

        def restoreTrackAccess(oldTrackAccess = oldTrackAccess):
            base.localAvatar.setTrackAccess(oldTrackAccess[0])

        minGagLevel = ToontownBattleGlobals.MIN_LEVEL_INDEX + 1
        maxGagLevel = ToontownBattleGlobals.MAX_LEVEL_INDEX + 1
        curGagLevel = minGagLevel

        def updateGagLevel(t, curGagLevel = curGagLevel):
            newGagLevel = int(round(t))
            if newGagLevel == curGagLevel:
                return
            curGagLevel = newGagLevel
            base.localAvatar.setTrackAccess([0,
             0,
             0,
             0,
             curGagLevel,
             curGagLevel,
             0])

        return Sequence(Func(grabCurTrackAccess), LerpFunctionInterval(updateGagLevel, fromData=1, toData=7, duration=0.3), WaitInterval(3.5), LerpFunctionInterval(updateGagLevel, fromData=7, toData=1, duration=0.3), Func(restoreTrackAccess), Func(messenger.send, 'doneThrowSquirtPreview'))

    def parseSetMusicVolume(self, line):
        if base.config.GetString('language', 'english') == 'japanese':
            try:
                loader = base.cr.playGame.place.loader
                type = 'music'
                duration = 0
                fromLevel = 1.0
                if len(line) == 2:
                    token, level = line
                elif len(line) == 3:
                    token, level, type = line
                elif len(line) == 4:
                    token, level, type, duration = line
                elif len(line) == 5:
                    token, level, type, duration, fromLevel = line
                if type == 'battleMusic':
                    music = loader.battleMusic
                elif type == 'activityMusic':
                    music = loader.activityMusic
                else:
                    music = loader.music
                if duration == 0:
                    return Func(music.setVolume, level)
                else:

                    def setVolume(level):
                        music.setVolume(level)

                    return LerpFunctionInterval(setVolume, fromData=fromLevel, toData=level, duration=duration)
            except AttributeError:
                pass

        else:
            return Wait(0.0)

    def parseFixMeter(self, line):
        if self.toon.style.getAnimal() == 'monkey':
            p = (0.153, 0.0, 0.13)
            
        else:
            p = (0.133, 0.0, 0.13)
            
        laffMeter = self.getVar('laffMeter')
        return Func(laffMeter.setPos, p)
            
readData()
#print lineDict['tutorial_mickey']
#exit()
