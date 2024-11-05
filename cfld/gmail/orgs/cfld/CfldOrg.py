from interface import implements
from framework.Interfaces import IOrg
from framework.Logger import Logger
from orgs.cfld.CfldSheetService import CfldSheetService
from orgs.cfld.NewSubmissionHandler import NewSubmissionHandler
from framework.LookupInfo import LookupInfo

class CfldOrg(Logger, implements(IOrg)):
    def __init__(self, config):
        super(CfldOrg, self).__init__(__class__)
        try:
            self.config = config
            self.ss = CfldSheetService(config['sheet_service_email'], config['sheet_name'], config['spreadsheet_id'], config['secret_path'], config['client_token_dir'])
            self.rule_data = self.ss.get_rule_construction_data()
            self.nsh = NewSubmissionHandler(self.ss.get_availability(), \
                                       self.ss.get_availability_blurbs())
            self.li = LookupInfo(self.ss.get_lookup_info_data())
        except: # catch this and expose another initialize call to be used by the tests
            pass
    def initialize_from_test_module(self, rule_data, avail, avail_blurbs, lookup_info):
        self.rule_data = rule_data
        self.nsh = NewSubmissionHandler(avail, avail_blurbs)
        self.li = LookupInfo(lookup_info)
    # IOrg
    def get_rule_construction_data(self):
        return self.rule_data
    def get_imports(self):
        return self.config['org']['imports']

    # Classes intialized in org_init function
    def lookup_info(self, k1, k2):
        return self.li.lookup_info(k1, k2)

    def run_new_submission_handler(self, t):
        return self.nsh.handle_thread(t)

    def short_name(self, key):
        return self.li.lookup_info('short_name', key.strip())

    def get_llm_info(self):
        return self.ss.get_llm_info()

# Having non class wrapper functions around the org makes it easier to call these 
# functions in the rule snippets (don't need 'org.XXXXXX')
# AND easier to make them visible in evaluate_expression 
# (import a function instead of importing a global class instance)
def lookup_info(k1, k2):
    return org.lookup_info(k1, k2)

def llm_info():
    return org.get_llm_info()

def run_new_submission_handler(t):
    return org.run_new_submission_handler(t)

# TODO: update rules on sheet
def short_name_from_address(key):
    return org.lookup_info('short_name_from_address', key.strip())

def direct_initialize_org(rule_data, avail, avail_blurbs, lookup_info):
    org.initialize_from_test_module(rule_data, avail, avail_blurbs, lookup_info)

def org_init(config):
    global org
    org = CfldOrg(config)
    return org
