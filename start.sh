#!/bin/bash

. ~/.profile

pkill chromium-browser 
pkill firefox
pkill python3
pkill node

echo 'setup input allocation for touch table..' 
sleep 1

xinput --map-to-output "Advanced Silicon S.A. CoolTouch® System" "DP-1-7" && # finde output via xinput --list und input via xrandr 

echo 'starting infoscreen'
cd /home/qscope/qscope/qscope_infoscreen
node q100_info.js &
sleep 2

echo 'starting firefox'
firefox --kiosk http://localhost:8082/ &
# wait $!

# xdotool search --sync --onlyvisible --class "Firefox" windowactivate key F11 
# chromium-browser --kiosk --user-data-dir=tmp --app="http://localhost:8082/" --enable-features=OverlayScrollbar --disable-restore-session-state --force-device-scale-factor=1 --start-maximized --window-size=1920,1080 &

sleep 2

source ~/envs/qscope/bin/activate

echo 'starting the frontend'
cd /home/qscope/qscope/qscope_frontend_touch
python3 run_q100viz.py
