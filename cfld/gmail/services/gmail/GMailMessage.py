import base64
import pdb
from framework.Logger import Logger
import re

# Message specific utils
def extract_email(email_string):
    if not email_string:
        return email_string
    return email_string.split(' ')[-1].strip('<').strip('>').strip('"')
# return list of strings of the emails
def extract_emails(emails_string):
    if not emails_string:
        return []
    if len(emails_string.split('@')) == 2 and len(emails_string.split(' ')) == 1:
        return [emails_string.strip('<').strip('>').strip('"')]
    # pick up a string like 'email@one.com, email@two.com'
    elif emails_string.find('<') == -1 \
            and emails_string.find('>') == -1 \
            and emails_string.find('"') == -1:
        return [x.strip() for x in emails_string.split(',')]

    split = re.split('[\s,]', emails_string)
    filtered = list(filter(lambda x : '@' in x, split))
    return [x.strip('<').strip('>').strip('"') for x in filtered]

class GMailMessage(Logger):
    def __init__(self, fields, service):
        super(GMailMessage, self).__init__(__class__)
        self.fields = fields
        self.service = service
    def update_all(self, message):
        self.fields = message.get_all_fields()
    def get_all_fields(self):
        return self.fields
        
    def update_from_many(self, new_messages_fields):
        for new_fields in new_messages_fields:
            if new_fields['id'] == self.__field('id'):
                self.fields.update(new_fields)

    def __field(self, field_name, default=None):
        search_dict = self.fields
        if not search_dict:
            return default
# handle a thread
        if field_name in search_dict:
            return search_dict[field_name]

        if field_name in search_dict:
            return search_dict[field_name]
        header = search_dict['payload']['headers']
        for m in header:
            if m['name'] == field_name:
                return m['value']
        return default

# ------------- slightly advanced accessors ------------------
    def is_draft(self):
        return self.has_label_id('DRAFT')

    def has_label_id(self, label_id):
        if 'labelIds' not in self.fields or label_id not in self.fields['labelIds']:
            return False
        return True
    
    def label_ids(self):
        return self.__field('labelIds', default=[])

    def set_labels(self, gmail_resp):
        if 'messages' in gmail_resp:
            for message_data in gmail_resp['messages']:
                if message_data['id'] == self.__field('id'):
                    self.fields['labelIds'] = message_data['labelIds']
                    return

        if 'labelIds' in gmail_resp and not self.is_draft():
            self.fields['labelIds'] = gmail_resp['labelIds']

        for label_id in self.__field('labelIds', default=[]):
            if type(label_id) != str:
                self.le('not string label id set: {}. for message with id: {}'.format(label_id, self.__fields('id')))

# ------------- end slightly advanced accessors ------------------

# ----------- wrappers around finding a single item from fields -------------------
    def subject(self):
        return self.__field('Subject', default='')
    def message_id(self):
        return self.__field('Message-ID')
    def sender(self):
        ret = extract_email(self.__field('From', default=''))
        if ret:
            return ret
        return extract_email(self.__field('from', default=''))
    def recipients(self):
        res = self.__field('To', default='')
        if not res:
            res = self.__field('to', default='')
        return extract_emails(res)
    def reply_to(self, raw=False):
        res = self.__field('Reply-To', default='')
        if res: 
            if raw:
                return res
            else:
                return extract_email(res)
        res = self.__field('Reply-to', default='')
        if raw:
            return res
        else:
            return extract_email(res)

    def cc(self):
        res = self.__field('Cc', default=None)
        if res:
            return extract_emails(res)
        return []

    def ts(self):
        return int(int(self.__field('internalDate')) / 1000)

    def id(self):
        return self.__field('id')





# ----------- end wrappers around finding a single item from fields ----------------

    # return the recipients of the message, minus any email that appears in filters
    def filtered_recipients(self, filters):
        rec = set(self.recipients())
        f = set(filters)
        return list(rec - f)

    # of html formatting
    def content(self, ignore_old_messages=True):
        payload = self.__field('payload')
        data = ''
        if 'parts' in payload:
            for part in payload['parts']:
                if 'parts' in part:
                    for inner_part in part['parts']:
                        if 'data' in inner_part['body']:
                            data += inner_part['body']['data']
                elif 'data' in part['body']:
                    data += part['body']['data']
        else:
            data = payload['body']['data']
        ret = base64.urlsafe_b64decode(data.encode('UTF8')).decode('UTF8')
        if not ignore_old_messages:
            return ret

        # Here we'll filter out all the b.s. that we get in gmail when we hit 'reply'
        # Look for the earliest of any of the delimiters in the message
        delimiters = ['\r\n\r\nOn ', '________________________________', '">On ','> On ', '/>On ', '\r\n    On ']
        min_index = len(ret)
        min_delim = ''
        for delimiter in delimiters:
            index = ret.find(delimiter)
            if index >= 0 and index < min_index:
                min_index = index
                min_delim = delimiter
        if not min_delim:
            return ret
        return ret[:ret.find(min_delim)]

    # return a list of all the (attachment data, filename), empty if no attachments
    def attachments(self):
        attachment_ids = []
        attachment_fns = []
        payload = self.__field('payload')
        data = ''
        if 'parts' in payload:
            for part in payload['parts']:
                if 'parts' in part:
                    for inner_part in part['parts']:
                        if 'attachmentId' in inner_part['body']:
                            attachment_ids.append(inner_part['body']['attachmentId'])
                            attachment_fns.append(inner_part['filename'])
                elif 'attachmentId' in part['body']:
                    attachment_ids.append(part['body']['attachmentId'])
                    attachment_fns.append(part['filename'])
        elif 'attachmentId' in payload['body']:
            attachment_ids.append(payload['body']['attachmentId'])
            attachment_fns.append(payload['filename'])
        attachment_data = []
        for attachment_id in attachment_ids:
            attachment = self.service.get_attachment(attachment_id, self.__field('id'))
            attachment_data.append(base64.urlsafe_b64decode(attachment['data'].encode('UTF8')))
        return list(zip(attachment_data, attachment_fns))
