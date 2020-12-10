import pdb
import inspect
from flatten_dict import flatten 
from flatten_dict import unflatten 
import globals

def lookup_info(k1, k2):
    return globals.g_li.lookup_info(k1, k2)

def run_new_submission_handler(t):
    return globals.g_nsh.handle_thread(t)

def list_of_emails_to_string_of_emails(l):
    if type(l) == str:
        return l
    ret = ''
    for item in l:
        ret = ret + item + ', '
    return ret[:-2]

def match(index):
    frame = inspect.currentframe()
    kw = frame.f_back.f_locals['kwargs']
    return kw['matches'][index]

def link(link_dest, link_text=None):
    if not link_text:
        link_text = link_dest
    return '<a href="{}">{}</a>'.format(link_dest, link_text)

def evaluate_expression(expression, **kwargs):
    local_request = __get_imports() + 'local_result = ' + expression.replace('thread', 'kwargs["thread"]')
    exec(local_request)
    return locals()['local_result']

def short_name(key):
    return lookup_info('short_name', key.strip())

def __get_imports():
    try:
        org_name = globals.org_name
        if org_name == 'cfld':
            return 'from orgs.cfld.NewSubmissionHandler import NewSubmissionHandler\nfrom orgs.cfld.util import get_new_application_email\n'
    except:
        return ''
