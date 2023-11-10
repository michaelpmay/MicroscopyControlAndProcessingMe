#!/bin/bash
if [ -z  $1 ]; then

  echo "ERROR: provide a Python Version"
  exit 1
fi

if [ -d "venv" ]; then
  rm -r venv
fi

python$1 -m venv venv/
source venv/bin/activate
python$1 -m pip install --upgrade pip
pip install -r requirements.txt
