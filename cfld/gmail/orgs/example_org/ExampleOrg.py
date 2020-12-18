import pdb
from interface import implements
from framework.Interfaces import IOrg

org = None
# Define external so we can overwrite while testing different rule configurations
# Default is two rule groups
# One is IfElse with Subject Matchers and Label Actions
# One is IfAny with LabelMatchers and Draft Action that uses our example_org code to
# run the function signature
header = ['name', 'email', 'dest_email', 'label_regex', 'subject_regex', 'body_regex', 'expression_match', 'action', 'value', 'finder', 'destinations', 'group', 'group_type', 'rule_type']
example_rule_construction_data = [header, ['Label by school', 'tyler', '', '', 'Zumper tenant lead for (.*) -.*', '', '', 'label', '"Schools"', '', '', '1', 'ifelse'], ['Label by school', 'tyler', '', '', '[\\S^]* is requesting information about (.*?)[#,]', '', '', 'label', '"Schools"', '', '', '1', 'ifelse'], ['Label by school', 'tyler', '', '', 'RentPath Lead from .* \\((.*)\\)', '', '', 'label', '"Schools"', '', '', '1', 'ifelse'], ['Label by school', 'tyler', '', '', '[\\S^]* wants to tour (.*) -', '', '', 'label', '"Schools"', '', '', '1', 'ifelse'], ['Label by school', 'tyler', '', '', '[\\S^]* is requesting an application for (.*) #.*', '', '', 'label', '"Schools"', '', '', '1', 'ifelse'], ['Remove catch all', 'tyler', '', 'Schools.*', '', '', '', 'unlabel', '"Catch all"', '', '', '1', 'ifelse'], ['Label by school', 'tyler', '', '', 'test subject', '', '', 'label', '"Schools"', '', '', '1', 'ifelse'], ['Add catch all', 'tyler', '', '', '.*', '', '', 'label', '"Catch all"', '', '', '1', 'ifelse'], \
['Add signature in draft', 'tyler', '', 'Schools', '', '', '', 'draft', 'signature(thread)', '', 'thread.default_reply()', '2', 'ifany', 'if'],['Add greeting in draft', 'tyler', '', 'Schools', '', '', '', 'prepend_draft', 'thread.salutation()', '', 'thread.default_reply()', '2', 'ifany', 'any']]
class ExampleOrg(implements(IOrg)):
    def __init__(self, config):
        self.config = config
    # IOrg
    def get_rule_construction_data(self):
        return example_rule_construction_data
    def get_imports(self):
        return self.config['org']['imports']

def signature(thread):
    return 'test signature for thread id {}'.format(thread.identifier)

def org_init(config):
    org = ExampleOrg(config)
    return org



# ------------ Functions created for test_Integration ----------------

def get_new_application_email(thread):
    return 'tgaldes@gmail.com'
