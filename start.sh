#!/bin/bash
echo "Starting Q-Scope Tangibles!"
echo "killing old processes"
pkill chromium-browser 
pkill firefox
pkill python3
pkill node

. ~/.profile

echo 'starting infoscreen'
cd /home/qscope/qscope/qscope_infoscreen
node q100_info.js &
sleep 2

echo 'starting firefox'
firefox --kiosk http://localhost:8082/ &


sleep 2

source ~/envs/qscope/bin/activate

echo 'starting the frontend'
cd /home/qscope/qscope/qscope_frontend_tangibles
python3 run_q100viz.py
