import pdb

def init(config, logger):
    global g_config
    global g_org
    global g_logger
    g_config = config
    g_logger = logger
    if 'org_init_import' in g_config:
        import_line = g_config['org_init_import']
        exec(import_line, globals())
        g_org = org_init(config)
    
