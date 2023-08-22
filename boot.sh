#!/bin/env /bin/bash

# Run the Flask App
cd /home/asteralabs/pisomounter
source venv/bin/activate
export FLASK_APP=app.py
python3 -m flask run --host=0.0.0.0

# Connect the USB Drive
sudo modprobe g_mass_storage file=/home/asteralabs/pisomounter/images/memtest86-iso.iso cdrom=1 stall=0
