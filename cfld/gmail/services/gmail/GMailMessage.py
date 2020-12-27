import base64
import pdb
from framework.Logger import Logger

# Message specific utils
def extract_email(email_string):
    if not email_string:
        return email_string
    return email_string.split(' ')[-1].strip('<').strip('>')
def extract_emails(emails_string):
    if not emails_string:
        return []
    if len(emails_string.split('@')) == 2 and len(emails_string.split(' ')) == 1:
        return [emails_string.strip('<').strip('>')]
    # pick up a string like 'email@one.com, email@two.com'
    elif emails_string.find('<') == -1 \
            and emails_string.find('>') == -1 \
            and emails_string.find('"') == -1:
        return [x.strip() for x in emails_string.split(',')]
    insert_mode = False
    res = []
    current_email = ''
    for char in emails_string:
        if char == '<':
            insert_mode = True
        elif char == '>':
            insert_mode = False
            res.append(current_email)
            current_email = ''
        elif insert_mode:
            current_email += char
    return res

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
        delimiters = ['\r\n\r\nOn ', '________________________________']
        for delimiter in delimiters:
            index = ret.find(delimiter)
            if index > 0:
                return ret[:index]
        return ret

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
