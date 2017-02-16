@echo off
echo AI
echo ==========================
C:/Panda3D-ttn/python/ppython -m toontown.ai.ServiceStart --base-channel 342000000 --max-channels 9999999 --stateserver 10000 --district-name "TTN-Dev 1" --astron-ip "127.0.0.1:7199" --eventlogger-ip "127.0.0.1:7197"
echo ==========================
pause