#!/bin/bash
source venv/bin/activate
python -m unittest discover -s test/ -p '*_test.py'
