from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from framework.util import list_of_emails_to_string_of_emails


def create_multipart(destinations, from_email, subject, in_reply_to, references, body, attachments, body_encoding='html'):

    multipart = MIMEMultipart()
    mimetext = MIMEText(body, body_encoding)
    multipart.attach(mimetext)
    for attachment_data, fn in attachments:
        # Refactor- if we want to support multiple file formats in the future we can get the subtype from the filename
        attachment = MIMEApplication(attachment_data, _subtype='pdf')
        attachment.add_header('Content-Disposition', 'attachment', filename=fn)
        multipart.attach(attachment)

    multipart['to'] = list_of_emails_to_string_of_emails(destinations)
    multipart['from'] = from_email
    multipart['subject'] = subject
    multipart['In-Reply-To'] = in_reply_to
    multipart['References'] = references
    return multipart

