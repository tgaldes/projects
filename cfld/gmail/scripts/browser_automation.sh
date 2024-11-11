#!/bin/bash
# start the venv
source /home/tgaldes/git/3rdparty/browser-use/env/bin/activate

# run a python script called browser_automation.py in the same directory as this file
# and pass all the command line args to it
SCRIPT_DIR=$(dirname "$(realpath "$0")")
python3 $SCRIPT_DIR/browser_automation.py $@

# exit the venv
deactivate
