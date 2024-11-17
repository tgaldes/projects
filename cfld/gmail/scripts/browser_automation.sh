#!/bin/bash
# start the venv
source /home/tgaldes/git/3rdparty/browser-use/env/bin/activate
set +H

# run a python script called browser_automation.py in the same directory as this file
# and pass all the command line args to it
SCRIPT_DIR=$(dirname "$(realpath "$0")")
python3 $SCRIPT_DIR/browser_automation.py $@
cd /home/tgaldes/git/3rdparty/browser-use
# print the next command
echo "python3 examples/try.py $@"
python3 examples/try.py "$@"
cd -

# exit the venv
deactivate
