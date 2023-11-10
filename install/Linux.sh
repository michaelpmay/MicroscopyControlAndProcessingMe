#!/bin/bash
if [ -z  $1 ]; then

  echo "ERROR: provide a Python Version"
  exit 1
fi

if [ -d "venv" ]; then
  rm -r venv
fi
apt update && sudo apt upgrade
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install python$1
sudo apt install python$1
python$1 -m venv venv/
source venv/bin/activate
python$1 -m pip install --upgrade pip
pip install -r requirements.txt
