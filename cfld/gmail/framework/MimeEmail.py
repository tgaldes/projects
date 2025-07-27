from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage


def list_of_emails_to_string_of_emails(l):
    if type(l) == str:
        return l
    ret = ''
    for item in l:
        ret = ret + item + ', '
    return ret[:-2]

def create_multipart(destinations, from_email, subject, in_reply_to, references, body, attachments, body_encoding='html'):

    multipart = MIMEMultipart()
    mimetext = MIMEText(body, body_encoding)
    multipart.attach(mimetext)
    for attachment_data, fn in attachments:
        # Refactor- if we want to support multiple file formats in the future we can get the subtype from the filename
        if fn[-3:] == 'pdf':
            attachment = MIMEApplication(attachment_data, _subtype='pdf')
            attachment.add_header('Content-Disposition', 'attachment', filename=fn)
            multipart.attach(attachment)
        elif fn[-3:] == 'png':
            #attachment = MIMEApplication(attachment_data, _subtype='png')
            attachment = MIMEImage(attachment_data)
            attachment.add_header('Content-Disposition', 'attachment', filename=fn)
            multipart.attach(attachment)
        # TODO: how to log error here?

    email_string = list_of_emails_to_string_of_emails(destinations)
    if email_string:
        multipart['to'] = email_string
    multipart['from'] = from_email
    multipart['subject'] = subject
    multipart['In-Reply-To'] = in_reply_to
    multipart['References'] = references
    return multipart

