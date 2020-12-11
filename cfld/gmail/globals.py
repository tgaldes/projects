import pdb

from LookupInfo import LookupInfo

global g_li
global g_nsh
global g_org
global g_config
def init(data, raw_availability, raw_availability_blurbs, config):
    global g_li
    g_li = LookupInfo(data)
    global g_nsh
    global g_config
    g_config = config
    if g_config['org']['name'] == 'cfld':
        from orgs.cfld.NewSubmissionHandler import NewSubmissionHandler # TODO: we should probably do an exec with the import in the config file
        g_nsh = NewSubmissionHandler(raw_availability, raw_availability_blurbs)
        g_org = g_config['org']['name']
    
