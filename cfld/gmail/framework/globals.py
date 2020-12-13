import pdb

global g_config
global g_org
def init(config):
    global g_config
    global g_org
    g_config = config
    # We could even read the imports from the json here so that the org code could live outside the repo completely
    if g_config['org']['name'] == 'cfld':
        from orgs.cfld.util import org_init
        g_org = org_init(config)
    elif g_config['org']['name'] == 'example_org':
        from orgs.example_org.ExampleOrg import org_init
        g_org = org_init(config)
    
