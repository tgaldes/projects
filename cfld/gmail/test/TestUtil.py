import os
import pdb
from services.gmail.GMailMessage import GMailMessage
import pathlib
import json
from unittest.mock import Mock
import base64

parent_path = str(pathlib.Path(__file__).parent.absolute())

def get_thread_constructor_args(fn):
    with open(os.path.join(parent_path, fn), 'r') as f:
        d = json.load(f)
    messages = []
    for fields in d['messages']:
        messages.append(GMailMessage(fields, Mock()))
    return d['id'], messages

def encode_for_payload(text):
    return base64.urlsafe_b64encode(text.encode('utf-8')).decode()


