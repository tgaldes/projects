import pdb
g_config = None

def init(config, logger):
    global g_org
    global g_logger
    global g_config
    g_logger = logger
    g_config = config

    if 'org_init_import' in g_config:
        import_line = g_config['org_init_import']
        exec(import_line, globals())
        g_org = org_init(config)
    
