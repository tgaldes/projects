import pdb
from framework.BaseValidator import BaseValidator


def get_substring_after_delim(haystack, delimiter, end_delimiter='<'):
    start_index = haystack.find(delimiter) + len(delimiter)
    if start_index == -1:
        if not BaseValidator.force_matches:
            raise Exception('Could not find the delimiter: {} in {}'.format(delimiter, haystack))
        else:
            return 'test applicant'
    end_index = haystack[start_index:].index(end_delimiter) + start_index
    return haystack[start_index:end_index]


# parse the thread created when a tenant submits their application 
# and return the tenant email address
def get_new_application_email(thread):
    decoded_html = thread.last_message_text()
    substring = '<tr><th>Email:</th><td>'
    return get_substring_after_delim(decoded_html, substring)

def get_new_application_name(thread, return_as_list=False):
    decoded_html = thread.last_message_text()
    substring = '<tr><th>Applicant:</th><td>'
    name = get_substring_after_delim(decoded_html, substring)
    if not return_as_list:
        return name
    else:
        return name.split()[:2]

def get_approved_application_name(thread, return_as_list=False):
    decoded_html = thread.last_message_text()
    substring = '<tr><th>Applicant name:</th><td>'
    name = get_substring_after_delim(decoded_html, substring)
    if not return_as_list:
        return name
    else:
        return name.split()[:2]

def get_approved_application_email(thread):
    decoded_html = thread.last_message_text()
    substring = '<tr><th>Applicant email:</th><td>'
    return get_substring_after_delim(decoded_html, substring)

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


# When we send out a lease doc to an owner and a tenant, we want to return just the tenant email here for the redirect to search on
# arg will look like 'j.stan.hill@gmail.com and ivan.gonzalez@cimat.mx'
# or 'ivan.gonzalez@cimat.mx'
def get_lease_sent_out_email(email_list_from_subject, all_owner_emails):
    #all_owner_emails = lookup_info('lease_owners', 'lease_owners')
    emails = []
    for token in email_list_from_subject.split():
        if '@' in token and token not in all_owner_emails:
            emails.append(token)
    if len(emails) != 1:
        raise Exception('In get_lease_sent_out_email with arg: {} we found {} non owner emails when we expected 1: {}'.format(email_list_from_subject, len(emails), emails))
    return emails[0]

def get_signed_lease_email(thread):
    # Since Adobe doesn't know how to set the 'Reply-To' header in emails they send
    # out we added a hack that optionally allows you to work around that
    for email in thread.default_reply(force_all=True):
        if email.split('@')[1].split('.')[0] in ['cleanfloorslockingdoors', 'echosign']:
            continue
        return email

    

