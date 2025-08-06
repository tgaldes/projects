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

def create_forward_multipart(destinations, from_email, subject, original_message, body, body_encoding='html'):
    """
    Create a forward draft message for the given original_message,
    quoting the original content and including its attachments.
    """
    import pdb
    # Build forwarded header block
    header_lines = [
        '---------- Forwarded message ---------<br>',
        f"From: {original_message.sender()}<br>",
        f"Subject: {original_message.subject()}<br>",
        f"To: {list_of_emails_to_string_of_emails(original_message.recipients())}<br><br><br>",
        ''
    ]
    forwarded = '\n'.join(header_lines) + '\n' + original_message.content()
    # Include original attachments
    attachments = original_message.attachments()
    # For forwarding, do not set In-Reply-To or References
    return create_multipart(
        destinations,
        from_email,
        subject,
        in_reply_to='',
        references='',
        body=body + forwarded,
        attachments=attachments,
        body_encoding=body_encoding
    )
