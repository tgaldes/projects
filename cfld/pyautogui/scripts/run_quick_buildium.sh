#!/bin/sh
cd /home/tgaldes/git/projects/cfld/pyautogui
export PYTHONPATH=.
/usr/bin/python3 buildium/main.py "$@"
