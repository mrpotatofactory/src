from direct.fsm.StatePush import StateVar
from otp.level.EntityStateVarSet import EntityStateVarSet
from CogdoUtil import VariableContainer
from toontown.cogdominium.CogdoEntityTypes import CogdoCraneGameSettings, CogdoCraneCogSettings
Gameplay = VariableContainer()
Gameplay.SecondsUntilGameOver = 60.0 * 3.0
Gameplay.TimeRunningOutSeconds = 45.0
Audio = VariableContainer()
Audio.MusicFiles = {'normal': 'phase_9/audio/bgm/CHQ_FACT_bg.ogg',
 'end': 'phase_7/audio/bgm/encntr_toon_winning_indoor.ogg',
 'timeRunningOut': 'phase_7/audio/bgm/encntr_suit_winning_indoor.ogg'}
Settings = EntityStateVarSet(CogdoCraneGameSettings)
CogSettings = EntityStateVarSet(CogdoCraneCogSettings)
StompOMaticPosHpr = [( 0, 0, 0, 0, 0, 0 )]

elevatorINPosHpr = [( -72.75515747, -0.8223749542, 0, 90, 0, 0 )]

elevatorOUTPosHpr = [( 74.7226648, 8.122365365, 0, -90, 0, 0 )]

CranePosHprs = [( -20, -20, 0, -45, 0, 0 ), 
( -20, 20, 0, 225, 0, 0 ), 
( 20, 20, 0, 135, 0, 0 ), 
( 20, -20, 0, 45, 0, 0 )]

MoneyBagPosHprs = [[ -37.39435573, -15.48237495, 0, -90, 0, 0 ], 
[ -38.55568955, 12.38489211, 0, -90, 0, 0 ], 
[ 38.29226596, -12.58237495, 0, 90, 0, 0 ], 
[ 39.09665787, 12.51628086, 0, 90, 0, 0 ], 
[ -15.03627619, -38.69905975, 0, 0, 0, 0 ], 
[ 9.084017195, -38.10716796, 0, 0, 0, 0 ], 
[ -12.50592804, 39.11762505, 0, 180, 0, 0 ], 
[ 14.69407196, 39.11762505, 0, 180, 0, 0 ]]
for i in xrange(len(MoneyBagPosHprs)):
    MoneyBagPosHprs[i][2] += 6
