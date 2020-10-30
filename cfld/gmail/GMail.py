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

from util import list_of_emails_to_string_of_emails

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
        self.threads = self.service.users().threads().list(userId='me').execute().get('threads', [])

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
    def get_one_thread(self):
        for mail in self.mails
            indiv_mail = self.service.users().messages().get(userId='me', id=mail['id']).execute() # TODO: hardcoded to get the message that will trigger our hardcoded rule
            #indiv_thread = self.service.users().threads().get(userId='me', id=thread['id']).execute() # TODO: hardcoded to get the message that will trigger our hardcoded rule
            print(thread)
            #pdb.set_trace()
            #return indiv_thread
            return indiv_mail

    def get_subject(self, email):
        return self.get_field(email, 'Subject')
    def get_field(self, email, field_name):
# handle a thread
        if 'payload' not in email or 'headers' not in email['payload']:
            email = email['messages'][0]
        header = email['payload']['headers']
        for m in header:
            if m['name'] == field_name:
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

    def get_default_reply(self, email): # TODO: reply all?
        return self.get_field(email, 'From').split(' ')[-1].strip('<').strip('>')
    
    def add_draft(self, email, body, destinations):
        message = MIMEText(body)
        message['to'] = list_of_emails_to_string_of_emails(destinations)
        print(list_of_emails_to_string_of_emails(destinations))
        message['from'] = 'tyler@cleanfloorslockingdoors.com'
        message['subject'] = self.get_field(email, 'Subject')
        message['In-Reply-To'] = self.get_field(email, 'Message-ID')
        message['References'] = self.get_field(email, 'Message-ID')# + ',' + self.get_field_a(email, 'References')
        email_body = {'message' : {'threadId' : email['threadId'], 'raw' : base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode()}}
# TODO: set the 
        draft = self.service.users().drafts().create(userId='me', body=email_body).execute()
        return draft


g_instance = GMail()
