import pickle
import pdb
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64

from framework.util import list_of_emails_to_string_of_emails
from framework.Logger import Logger
from framework.Thread import Thread
from services.gmail.GMailMessage import GMailMessage

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GMailService(Logger):
    def __init__(self, email, domains, secret_path, token_dir):
        super(GMailService, self).__init__(__class__)
        self.email = email
        self.user = email.split('@')[0]
        self.domains = domains
        self.li('Creating for {}'.format(email))
        creds = None
        pickle_path = os.path.join(token_dir, 'token.gmail.{}.pickle'.format(self.user))
        if os.path.exists(pickle_path):
            with open(pickle_path, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    secret_path, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(pickle_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)
        self.drafts = self.service.users().drafts().list(userId='me').execute().get('drafts', [])

        self.default_thread_ids = self.service.users().threads().list(userId='me', maxResults = 20, q='label:INBOX').execute().get('threads', [])
        #self.default_thread_ids = self.service.users().threads().list(userId='me', maxResults = 1, q='Rent payment reversed').execute().get('threads', [])


        # We want to create no more than one Thread instance per thread id
        # That way we don't need to make a state change on a Thread and also
        # update the state on all the other Thread instances for the same id
        self.thread_id_2_full_threads = {}
        # Map queries to a list of created Thread instances
        self.full_threads_by_query = {}

        default_threads = []
        for item in self.default_thread_ids:
            thread_map = self.service.users().threads().get(userId='me', id=item['id'], format='full').execute()
            thread = self.__create_thread_from_raw(thread_map)
            self.thread_id_2_full_threads[thread.id()] = thread
            '''fn = './test/integration_test_inputs/conversation_between_apply_inbox_and_tenant.txt'
            with open(fn, 'w') as f:
                import json
                json.dump(thread_map, f, indent=4)'''
            default_threads.append(thread)
        self.full_threads_by_query[''] = default_threads

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
    def get_user(self):
        return self.user
    def get_domains(self):
        return self.domains
    def get_label_name(self, label_id):
        if label_id in self.label_id_2_string:
            return self.label_id_2_string[label_id]
        return None

    def get_email(self):
        return self.email

    # Empty q gets us all_full_threads
    def query(self, q, limit):
        if q in self.full_threads_by_query:
            return self.full_threads_by_query[q]
        res = []
        q_result = self.service.users().threads().list(userId='me', maxResults = limit, q='{}'.format(q)).execute().get('threads', [])
        self.ld('Query {} returned {} threads.'.format(q, len(q_result)))
        for item in q_result:
            # Before we call the service, check if we already have this thread locally
            if item['id'] in self.thread_id_2_full_threads:
                self.ld('Returning existing thread: {}'.format(self.thread_id_2_full_threads[item['id']]))
                res.append(self.thread_id_2_full_threads[item['id']])
            else:
                thread = self.__create_thread_from_raw(self.service.users().threads().get(userId='me', id=item['id'], format='full').execute())
                self.thread_id_2_full_threads[item['id']] = thread
                res.append(thread)
            # Save this id for future use
        # Save full result of the query
        self.full_threads_by_query[q] = res
        return res

    def set_label(self, id, label_id, unset=False, userId='me'):
# TODO: same expo backoff function as v1
        payload = { 'addLabelIds' : [],
                    'removeLabelIds' : []
                  }
        if unset:
            payload['removeLabelIds'] = [label_id]
        else:
            payload['addLabelIds'] = [label_id]
        resp = self.service.users().threads().modify(userId=userId,
                                              id=id,
                                              body=payload).execute()
        if 'labelIds' in resp:
            return resp['labelIds']
        elif 'messages' in resp:
            return resp['messages'][0]['labelIds']
        self.lw('No labelIds in response to set_label call for label_id: {} label_string: {}'.format(label_id, label_id_2_string[label_id]))
        return []

    def get_drafts(self):
        return self.drafts

    def delete_draft(self, draft_id, userId='me'):
        return self.service.users().drafts().delete(userId=userId, id=draft_id).execute()

    def get_attachment(self, attachment_id, message_id):
        return self.service.users().messages().attachments().get(userId='me', messageId=message_id, id=attachment_id).execute()

# if id=None we will create a new draft, otherwise update draft with id = id
# add the new draft to our internal state
# return the MESSAGE object of the associated draft
    def append_or_create_draft(self, mime_email, thread_id, draft_id=None, userId='me'):
        payload = {'message' : {'threadId' : thread_id, 'raw' : base64.urlsafe_b64encode(mime_email.as_string().encode('utf-8')).decode()}}
# update an existing draft
        if draft_id:
            draft = self.service.users().drafts().update(userId=userId, id=draft_id, body=payload).execute()
            self.li('Appended to existing draft with id: {}'.format(draft_id))
# create a new draft!
        else:
            draft = self.service.users().drafts().create(userId=userId, body=payload).execute()
            self.li('Created new draft with id: {}'.format(draft['id']))
        self.__update_drafts(draft)
        message_data = self.service.users().messages().get(userId=userId, id=draft['message']['id']).execute()
        return GMailMessage(message_data, self)


    def __create_thread_from_raw(self, raw_thread):
        messages = []
        for message in raw_thread['messages']:
            messages.append(GMailMessage(message, self))
        return Thread(raw_thread['id'], messages, self)

    def __update_drafts(self, new_draft):
        for i, old_draft in enumerate(self.drafts):
            if new_draft['id'] == old_draft['id']:
                self.drafts[i] = new_draft # update with the new message id
                return
        self.drafts.append(new_draft)

if __name__=='__main__':
    gs = GMailService('apply@cleanfloorslockingdoors.com', ["cleanfloorslockingdoors.com", "cf-ld.com"], "/home/tgaldes/Dropbox/Fraternity PM/dev_private/cfldv1_secret.json", "/home/tgaldes/Dropbox/Fraternity PM/dev_private/")

