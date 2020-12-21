import pdb

global g_config
global g_org
def init(config):
    global g_config
    global g_org
    g_config = config
    if 'org_init_import' in g_config:
        import_line = g_config['org_init_import']
        exec(import_line, globals())
        g_org = org_init(config)
    
