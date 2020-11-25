import pdb

from LookupInfo import LookupInfo
from NewSubmissionHandler import NewSubmissionHandler

global g_li
global g_nsh
def init(data, raw_availability, raw_availability_blurbs):
    global g_li
    g_li = LookupInfo(data)
    global g_nsh
    g_nsh = NewSubmissionHandler(raw_availability, raw_availability_blurbs)
    
