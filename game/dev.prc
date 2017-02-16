window-title Toontown - DEV

###########################
SERVER CONFIG
DO NOT EDIT
USE ARGS INSTEAD:

CUSTOM SERVER: run -s IP
CUSTOM TOKEN: run -t TOKEN
###########################
game-server 127.0.0.1
eventlog-host 127.0.0.1
server-version ttn-dev
server-force-ssl #f
###########################

#Game
dc-file ttn.dc
want-dev #f

audio-library-name p3fmod_audio
accountdb-local-file databases/csm-cookies.db

model-path ../resources/
default-model-extension .bam
icon-filename icon.ico
cursor-filename toonmono.cur

default-directnotify-level info

#Core Features
cog-thief-ortho 0
show-total-population #t
want-mat-all-tailors #t
estate-day-night #t
want-news-page #f
want-news-tab #f
want-housing #t
want-old-fireworks #t
want-instant-parties #t
want-silly-meter #t
want-game-tables #t
want-chinese-checkers #t
want-checkers #t
want-find-four #t
want-top-toons #t
want-golf-karts #t
want-parties #t
want-pets #t
want-octaves #t
auto-skip-tutorial #f
want-dev-minigames #t
want-bank-interior #t
want-library-interior #t

#CogDominiums
want-emblems #t
cogdo-want-barrel-room #t
want-lawbot-cogdo #t
want-house-types #t
cogdo-want-org #t

#Disney Characters
want-classic-chars #t

#Developer
want-dev-camera-positions #t
schellgames-dev #f

#Server
allow-secret-chat #t
secret-chat-needs-parent-password #f
parent-password-set #t
force-typed-whisper-enabled #t

holiday-list 60,64,65,66
silly-meter-phase 12.0

ai-sleep .01
log-stack-dump #f

account-db-type local
force-black-cat-mgr #t
mega-invasion-shards 401
want-instant-delivery #t
