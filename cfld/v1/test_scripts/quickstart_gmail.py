from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import base64
from email import encoders

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.gmail.pickle'):
        with open('token.gmail.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/home/tgaldes/Dropbox/Fraternity PM/dev_private/cfldv1_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.gmail.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
#    results = service.users().labels().list(userId='me').execute()
#    labels = results.get('labels', [])
#    label_strings = []
#    if not labels:
#        print('No labels found.')
#    else:
#        print('Labels:')
#        for label in labels:
#            print(label['name'])
#            label_strings.append(label['name'])
#    # now print some unread emails in the inbox
#    #results = service.users().messages().list(userId='me', maxResults = 10, labelIds=('INBOX'), q='is:unread').execute()
#    results = service.users().messages().list(userId='me', maxResults = 10).execute()
#    mails = results.get('messages', [])
#    for mail in mails:
#        indiv_mail = service.users().messages().get(userId='me', id=mail['id']).execute()
#        print(mail)
#        #print(indiv_mail)
## list of {'name' : .... , 'value' : .....} dicts 
#        header = indiv_mail['payload']['headers']
#        for m in header:
#            if m['name'] == 'Subject':
#                print(m['value'])
#
#    # now create a label and label the first message in the inbox with that label
#    name = 'frompythonwithlove'
#    label = {
#        "messageListVisibility": 'show',
#        'labelListVisibility': 'labelShow',
#        'name' : name
#    }
#    if name not in label_strings:
#        results = service.users().labels().create(userId='me', body=label).execute()
    #email_pre_body = """<pre> Congratulations! We've successfully created account. Go to the page: """
    link_text = \
    '''Dear Mr. Joshnson,<br><br> 
Here is an email with a link: <a href="https://www.cf-ld.com/">here.</a><br><br>

Best,<br>
Tyler Galdes<br>
Founder, CF&LD<br><img src="cid:image1"><br>'''

    # now create a draft to tgaldes@gmail.com with a link
    email = MIMEMultipart('related')
    #email = MIMEMultipart('related')
    #email.attach(alt)
    email['to'] = 'tgaldes@gmail.com'
    email['from'] = 'tyler@cf-ld.com'
    email['subject'] = 'beep boop :)'
    #body1 = MIMEText(email_pre_body, 'plain')
    body2 = MIMEText(link_text, 'html')
    f_img = open('/home/tgaldes/Downloads/output-onlinepngtools.png', 'rb')
    footer_image = MIMEImage(f_img.read(), _subtype='image')
    footer_image.add_header('Content-ID', '<image1>')
    footer_image.add_header("Content-Disposition", "inline", filename="image1")
    email.attach(body2)
    print(email.as_string())
    email.attach(footer_image)
    print(email.as_string())
    #email.attach(body1)
    email_body = {'message' : {'raw' : base64.urlsafe_b64encode(email.as_string().encode('utf-8')).decode()}}
    draft = service.users().drafts().create(userId='me', body=email_body).execute()
    print(draft)


def send_image(): # unused
    # now create a draft to tgaldes@gmail.com with a link
    email = MIMEMultipart('related')
    #email = MIMEMultipart('related')
    #email.attach(alt)
    email['to'] = 'tgaldes@gmail.com'
    email['from'] = 'tyler@cf-ld.com'
    email['subject'] = 'beep boop :)'
    #body1 = MIMEText(email_pre_body, 'plain')
    body2 = MIMEText(link_text, 'html')
    f_img = open('/home/tgaldes/Downloads/output-onlinepngtools.png', 'rb')
    footer_image = MIMEImage(f_img.read(), _subtype='image')
    footer_image.add_header('Content-ID', '<image1>')
    footer_image.add_header("Content-Disposition", "inline", filename="image1")
    email.attach(body2)
    print(email.as_string())
    email.attach(footer_image)
    print(email.as_string())
    #email.attach(body1)
    email_body = {'message' : {'raw' : base64.urlsafe_b64encode(email.as_string().encode('utf-8')).decode()}}
    draft = service.users().drafts().create(userId='me', body=email_body).execute()
    print(draft)

    


if __name__ == '__main__':
    main()
