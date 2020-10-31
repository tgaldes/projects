from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pdb

from util import list_of_emails_to_string_of_emails

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GMailService:
    def __init__(self, email):
        self.user = email.split('@')[0]
        creds = None
        pickle_path = 'token.gmail.{}.pickle'.format(self.user)
        if os.path.exists(pickle_path):
            with open(pickle_path, 'rb') as token:
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
            with open(pickle_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)
        results = self.service.users().messages().list(userId='me', maxResults = 10, labelIds=('INBOX')).execute() # TODO: unread query in a refresh function
        results = self.service.users().messages().list(userId='me', maxResults = 10).execute()
        self.mails = results.get('messages', [])
        self.threads = self.service.users().threads().list(userId='me').execute().get('threads', [])
        self.drafts = self.service.users().drafts().list(userId='me').execute().get('drafts', [])

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

    def get_label_id(self, label_string): # TODO: create label on demand? Or force an exception when the desired label doesn't match somehting I've already created
        if label_string in self.label_string_2_id:
            return self.label_string_2_id[label_string]
        return None
    def get_one_thread(self):
        for thread in self.threads:
            indiv_thread = self.service.users().threads().get(userId='me', id=thread['id']).execute() # TODO: hardcoded to get the message that will trigger our hardcoded rule
            print(indiv_thread)
            return indiv_thread


    def set_label(self, id, payload, userId='me'):
# TODO: same expo backoff function as v1
        message = self.service.users().threads().modify(userId=userId,
                                              id=id,
                                              body=payload).execute()
        return message

    def get_drafts(self):
        return self.drafts

# if id=None we will create a new draft, otherwise update draft with id = id
# add the new draft to our internal state
# return the MESSAGE object of the associated draft
    def append_or_create_draft(self, payload, draft_id=None, userId='me'):
# update an existing draft
        if draft_id:
            draft = self.service.users().drafts().update(userId=userId, id=draft_id, body=payload).execute()
# create a new draft!
        else:
            draft = self.service.users().drafts().create(userId=userId, body=payload).execute()
            self.drafts.append(draft)

        message = self.service.users().messages().get(userId=userId, id=draft['message']['id']).execute()
        return message