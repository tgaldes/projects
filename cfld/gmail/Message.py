import base64
import pdb
from Logger import Logger

# Message specific utils
def extract_email(email_string):
    if not email_string:
        return email_string
    return email_string.split(' ')[-1].strip('<').strip('>')

class Message(Logger):
    def __init__(self, fields):
        super(Message, self).__init__(__name__)
        self.fields = fields
    def update_all(self, fields):
        self.fields = fields
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

    def add_label_id(self, label_id):
        if 'labelIds' not in self.fields:
            self.fields['labelIds'] = [label_id]
        else:
            self.fields['labelIds'].append(label_id)
# ------------- end slightly advanced accessors ------------------

# ----------- wrappers around finding a single item from fields -------------------
    def subject(self):
        return self.__field('Subject', default='')
    def message_id(self):
        return self.__field('Message-ID')
    def sender(self):
        return extract_email(self.__field('From', default=''))
    def recipients(self):
        res = self.__field('To', default='')
        if not res:
            res = self.__field('to', default='')
        to_emails = []
        if res:
            res = res.split(',')
            for i, to_email in enumerate(res):
                to_emails.append(extract_email(to_email))
        return to_emails
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
        cc_emails = []
        if res:
            res = res.split(',')
            for i, cc_email in enumerate(res):
                cc_emails.append(extract_email(cc_email))
        return cc_emails

    def ts(self):
        return int(int(self.__field('internalDate')) / 1000)

    def id(self):
        return self.__field('id')





# ----------- end wrappers around finding a single item from fields ----------------

    # of html formatting
    def content(self, ignore_old_messages=True):
        payload = self.__field('payload')
        data = ''
        if 'parts' in payload:
            for part in payload['parts']:
                data += part['body']['data']
        else:
            data = payload['body']['data']
        ret = base64.urlsafe_b64decode(data.encode('UTF8')).decode('UTF8')
        if not ignore_old_messages:
            return ret
        # Here we'll filter out all the b.s. that we get in gmail when we hit 'reply'
        delimiter = '\r\n\r\nOn '
        index = ret.find(delimiter)
        if index > 0:
            return ret[:index]
        return ret
