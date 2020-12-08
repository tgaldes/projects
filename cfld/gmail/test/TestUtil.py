import os
from Message import GMailMessage
import pathlib
import json

parent_path = str(pathlib.Path(__file__).parent.absolute())

def get_thread_constructor_args(fn):
    with open(os.path.join(parent_path, fn), 'r') as f:
        d = json.load(f)
    messages = []
    for fields in d['messages']:
        messages.append(GMailMessage(fields))
    return d['id'], messages



