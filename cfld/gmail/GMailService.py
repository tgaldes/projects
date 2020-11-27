from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pdb

from util import list_of_emails_to_string_of_emails
from Logger import Logger

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GMailService(Logger):
    def __init__(self, email):
        super(GMailService, self).__init__(__name__)
        self.email = email
        self.user = email.split('@')[0]
        self.li('Creating {} for {}'.format(__name__, email))
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
        self.all_threads = self.service.users().threads().list(userId='me', labelIds=('INBOX'), maxResults = 30, q='label:INBOX').execute().get('threads', [])
        self.all_full_threads = []
        for item in self.all_threads:
            self.all_full_threads.append(self.service.users().threads().get(userId='me', id=item['id'], format='full').execute())

        self.unread_threads = self.service.users().threads().list(userId='me', labelIds=('INBOX'), maxResults = 10, q='label:unread').execute().get('threads', [])
        self.unread_full_threads = []
        for item in self.unread_threads:
            self.unread_full_threads.append(self.service.users().threads().get(userId='me', id=item['id'], format='full').execute())


        self.drafts = self.service.users().drafts().list(userId='me').execute().get('drafts', [])

        results = self.service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        self.label_string_2_id = {}
        self.label_id_2_string = {}
        if not labels:
            self.lw('No labels found for user: {}'.format(self.email))
        else:
            for label in labels:
                self.label_string_2_id[label['name']] = label['id']
                self.label_id_2_string[label['id']] = label['name']
        self.thread_index = 0
        self.ld('Loaded labels: {}'.format(self.label_string_2_id.keys()))

    def get_label_id(self, label_string): # TODO: create label on demand? Or force an exception when the desired label doesn't match somehting I've already created
        if label_string in self.label_string_2_id:
            return self.label_string_2_id[label_string]
        return None

    def get_label_name(self, label_id):
        if label_id in self.label_id_2_string:
            return self.label_id_2_string[label_id]
        return None

    def get_email(self):
        return self.email

    def get_unread_threads(self):
        return self.unread_full_threads
    def get_all_threads(self):
        return self.all_full_threads

    def set_label(self, id, payload, userId='me'):
# TODO: same expo backoff function as v1
        message = self.service.users().threads().modify(userId=userId,
                                              id=id,
                                              body=payload).execute()
        return message

    def get_drafts(self):
        return self.drafts

    def delete_draft(self, draft_id, userId='me'):
        return self.service.users().drafts().delete(userId=userId, id=draft_id).execute()
    def __update_drafts(self, new_draft):
        for i, old_draft in enumerate(self.drafts):
            if new_draft['id'] == old_draft['id']:
                self.drafts[i] = new_draft # update with the new message id
                return
        self.drafts.append(new_draft)

# if id=None we will create a new draft, otherwise update draft with id = id
# add the new draft to our internal state
# return the MESSAGE object of the associated draft
    def append_or_create_draft(self, payload, draft_id=None, userId='me'):
# update an existing draft
        if draft_id:
            draft = self.service.users().drafts().update(userId=userId, id=draft_id, body=payload).execute()
            self.li('Appended to existing draft with id: {}'.format(draft_id))
# create a new draft!
        else:
            draft = self.service.users().drafts().create(userId=userId, body=payload).execute()
            self.li('Created new draft with id: {}'.format(draft['id']))
        self.__update_drafts(draft)
        message = self.service.users().messages().get(userId=userId, id=draft['message']['id']).execute()
        return message

if __name__=='__main__':
    gs = GMailService('apply@cleanfloorslockingdoors.com')
    while True:
        gs.get_next_thread()

