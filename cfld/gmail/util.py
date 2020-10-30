import pdb
import inspect
def list_of_emails_to_string_of_emails(l):
    ret = ''
    for item in l:
        ret = ret + item + ', '
    return ret[:-2]

def match(index):
    frame = inspect.currentframe()
    kw = frame.f_back.f_locals['kwargs']
    return kw['matches'][index]

def evaluate_expression(expression, **kwargs):
    local_request = 'local_result = ' + expression
    exec(local_request)
    return locals()['local_result']

def get_short_name(val):
    names = {'2715 Portland Street' : 'USC'} # TODO: read from sheets
    return names[val]
