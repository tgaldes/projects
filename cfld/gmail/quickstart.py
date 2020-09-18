from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
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
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
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
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    label_strings = []
    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])
            label_strings.append(label['name'])
    # now print some unread emails in the inbox
    #results = service.users().messages().list(userId='me', maxResults = 10, labelIds=('INBOX'), q='is:unread').execute()
    results = service.users().messages().list(userId='me', maxResults = 10).execute()
    mails = results.get('messages', [])
    for mail in mails:
        indiv_mail = service.users().messages().get(userId='me', id=mail['id']).execute()
        print(mail)
        #print(indiv_mail)
# list of {'name' : .... , 'value' : .....} dicts 
        header = indiv_mail['payload']['headers']
        for m in header:
            if m['name'] == 'Subject':
                print(m['value'])

    # now create a label and label the first message in the inbox with that label
    name = 'frompythonwithlove'
    label = {
        "messageListVisibility": 'show',
        'labelListVisibility': 'labelShow',
        'name' : name
    }
    if name not in label_strings:
        results = service.users().labels().create(userId='me', body=label).execute()

    # now create a draft to tgaldes@gmail.com
#    message = MIMEText('Hello, world!')
#    message['to'] = 'tgaldes@gmail.com'
#    message['from'] = 'tyler@cf-ld.com'
#    message['subject'] = 'beep boop :)'
#    email_body = {'message' : {'raw' : base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode()}}
#    draft = service.users().drafts().create(userId='me', body=email_body).execute()
    


if __name__ == '__main__':
    main()
