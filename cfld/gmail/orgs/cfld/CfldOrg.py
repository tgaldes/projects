from interface import implements
from framework.Interfaces import IOrg
from framework.Logger import Logger
from orgs.cfld.CfldSheetService import CfldSheetService
from orgs.cfld.NewSubmissionHandler import NewSubmissionHandler
from framework.LookupInfo import LookupInfo

class CfldOrg(Logger, implements(IOrg)):
    def __init__(self, config):
        super(CfldOrg, self).__init__(__name__)
        self.ss = CfldSheetService(config['sheet_service_email'], config['sheet_name'], config['spreadsheet_id'], config['secret_path'], config['client_token_dir'])
        self.nsh = NewSubmissionHandler(self.ss.get_availability(), \
                                   self.ss.get_availability_blurbs())
        self.li = LookupInfo(self.ss.get_lookup_info_data())
        self.config = config
    # IOrg
    def get_rule_construction_data(self):
        return self.ss.get_rule_construction_data()
    def get_imports(self):
        return self.config['org']['imports']

    # Classes intialized in org_init function
    def lookup_info(self, k1, k2):
        return self.li.lookup_info(k1, k2)

    def run_new_submission_handler(self, t):
        return self.nsh.handle_thread(t)

    def short_name(self, key):
        return self.li.lookup_info('short_name', key.strip())

