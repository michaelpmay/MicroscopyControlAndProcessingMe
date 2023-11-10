#!/bin/bash
if [ -z  $1 ]; then

  echo "ERROR: provide a Python Version"
  exit 1
fi

if [ -d "venv" ]; then
  rm -r venv
fi

python -m venv venv/
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
