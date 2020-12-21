import pdb

# parse the thread created when a tenant submits their application 
# and return the tenant email address
def get_new_application_email(thread):
    decoded_html = thread.last_message_text()
    substring = '<tr><th>Email:</th><td>'
    start_index = decoded_html.find(substring) + len(substring)
    if start_index == -1:
        raise Exception('Could not find the substring: {} in the first message of the thread.'.format(substring))
    end_index = decoded_html[start_index:].index('<') + start_index
    return decoded_html[start_index:end_index]

# Since this is an org specific implementation we can have a hardcoded name mapping
def signature(thread):
    my_message_count = thread.get_user_message_count()
    name = thread.get_user_name()
    first, last = '', ''
    if name == 'tyler':
        first = 'Tyler'
        last = 'Galdes'
    elif name == 'wyatt':
        first = 'Wyatt'
        last = 'Cornelius'
    elif name == 'apply':
        first = 'Tyler'
        last = 'Galdes'
    if my_message_count == 0:
        return 'Best,<br>{} {}<br>Clean Floors & Locking Doors Team<br>'.format(first, last)
    elif my_message_count == 1:
        return 'Best,<br>{}<br>CF&LD Team<br>'.format(first)
    return 'Best,<br>{}<br>'.format(first)

# Retun a string representing the short name of the school
# empty string if we can't find a label matching 'Schools/.*'
def short_name_from_thread(thread):
    delim = 'Schools/'
    for label_name in thread.labels():
        if label_name and label_name.find(delim) == 0:
            return label_name[len(delim):]
    return 'the campus'

    

