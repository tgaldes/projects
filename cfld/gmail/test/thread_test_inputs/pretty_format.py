import os
import json

for fn in os.listdir('.'):
    if fn[-4:] != '.txt':
        print('Skipping non .txt file {}'.format(fn))
        continue
    print('Pretty printing {}'.format(fn))
    with open(fn, 'r') as f:
        d = json.loads(f.read())
    with open(fn, 'w') as f:
        json.dump(d, f, indent=4)
