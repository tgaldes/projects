#!/usr/bin/python3
import sys

# print what is supplied in the quoted first argument to the file /home/tgaldes/browser_automation.log

with open('/home/tgaldes/browser_automation.log', 'a') as f:
    line = ''
    for arg in sys.argv[1:]:
        line += arg + ' '
    f.write(line + '\n')

