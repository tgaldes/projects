import pdb

def init_config(config):
    global g_config
    g_config = config
    
def init(config, logger):
    global g_org
    global g_logger
    g_logger = logger
    if 'org_init_import' in g_config:
        import_line = g_config['org_init_import']
        exec(import_line, globals())
        g_org = org_init(config)
    
