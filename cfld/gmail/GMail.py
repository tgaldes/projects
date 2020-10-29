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
import pdb

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GMail:
    def __init__(self):
        creds = None
        if os.path.exists('token.gmail.tyler.pickle'): # TODO: take name of email in the constructor, that should have reliable mapping to secret and token path
            with open('token.gmail.tyler.pickle', 'rb') as token:
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
            with open('token.gmail.tyler.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)
        results = self.service.users().messages().list(userId='me', maxResults = 10, labelIds=('INBOX')).execute() # TODO: unread query in a refresh function
        results = self.service.users().messages().list(userId='me', maxResults = 10).execute()
        self.mails = results.get('messages', [])

        results = self.service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        self.label_string_2_id = {}
        if not labels:
            print('No labels found.')
        else:
            print('Labels:')
            for label in labels:
                self.label_string_2_id[label['name']] = label['id']
                print(label['name'], label['id'])
        return
    def get_one_email(self):
        for mail in self.mails:
            indiv_mail = self.service.users().messages().get(userId='me', id='1756f9403f66ac1d').execute() # TODO: hardcoded to get the message that will trigger our hardcoded rule
            print(mail)
            return indiv_mail

    def get_subject(self, email):
        header = email['payload']['headers']
        for m in header:
            if m['name'] == 'Subject':
                return m['value']

    def set_label(self, email, label_string):
# TODO: same expo backoff function as v1
        payload = { 'addLabelIds' : [self.label_string_2_id[label_string]],
                    'removeLabelIds' : []
                  }
        message = self.service.users().messages().modify(userId='me',
                                              id=email['id'],
                                              body=payload).execute()
        return message


g_instance = GMail()
