@echo off
echo UD
echo ==========================
C:/Panda3D-ttn/python/ppython -m toontown.uberdog.ServiceStart --base-channel 100000 --max-channels 100000 --stateserver 10000 --astron-ip "127.0.0.1:7199" --eventlogger-ip "127.0.0.1:7197"
echo ==========================
pause