import pdb

from LookupInfo import LookupInfo

global g_li
global g_nsh
global g_org
def init(data, raw_availability, raw_availability_blurbs, org_name):
    global g_li
    g_li = LookupInfo(data)
    global g_nsh
    if org_name == 'cfld':
        from orgs.cfld.NewSubmissionHandler import NewSubmissionHandler
        g_nsh = NewSubmissionHandler(raw_availability, raw_availability_blurbs)
        g_org = org_name
    
