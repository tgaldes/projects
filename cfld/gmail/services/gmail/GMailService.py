import pickle
import pdb
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64

from framework.MimeEmail import list_of_emails_to_string_of_emails
from framework.Logger import Logger
from framework.Thread import Thread
from services.gmail.GMailMessage import GMailMessage

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GMailService(Logger):
    def __init__(self, email, domains, secret_path, token_dir, default_query_limit=60, default_query_string='label:INBOX'):
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

        self.default_query = default_query_string
        self.default_limit = default_query_limit


        # We want to create no more than one Thread instance per thread id
        # That way we don't need to make a state change on a Thread and also
        # update the state on all the other Thread instances for the same id
        self.thread_id_2_full_threads = {}
        # Map queries to a list of created Thread instances
        self.full_threads_by_query = {}

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

    def get_all_history_ids(self):
        ret = {}
        for thread_id in self.thread_id_2_full_threads:
            ret[thread_id] = self.thread_id_2_full_threads[thread_id].history_id()
        return ret

    def __history_id(self, thread_id):
        if thread_id in self.thread_id_2_full_threads:
            return self.thread_id_2_full_threads[thread_id].history_id()
        return 0

    def __populate_query_result(self, q, limit):
        res = []
        self.ld('Bumping limit from {} to {} so we can make sure we get the most recent thread.'.format(limit, limit + 2))
        limit += 2
        q_result = self.service.users().threads().list(userId='me', maxResults = limit, q='{}'.format(q)).execute()
        threads = q_result.get('threads')

        if threads is None:
            self.ld('Query {} returned 0 threads from gmail api'.format(q))
            self.full_threads_by_query[q] = []
            return

        self.ld('Query {} returned {} threads from gmail api.'.format(q, len(q_result.get('threads'))))
        while True:
            for item in q_result.get('threads', []):
                # Before we call the service, check if we already have this up to date thread locally
                if item['id'] in self.thread_id_2_full_threads:
                    self.ld('History id for id: {}. gmail: {} cached: {}'.format(item['id'], item['historyId'], self.__history_id(item['id'])))
                if item['id'] in self.thread_id_2_full_threads \
                        and int(item['historyId']) <= self.__history_id(item['id']):
                    self.ld('Returning existing thread: {}'.format(self.thread_id_2_full_threads[item['id']]))
                    res.append(self.thread_id_2_full_threads[item['id']])
                else:
                    thread_map = self.service.users().threads().get(userId='me', id=item['id'], format='full').execute()
                    try:
                        thread = self.__create_thread_from_raw(thread_map)
                        # Save this id for future use
                        self.thread_id_2_full_threads[item['id']] = thread
                        self.__update_history_id(thread.id(), thread_map['historyId'])
                        res.append(thread)
                    except Exception as e:
                        self.li('Couldn\'t create thread id {} because of: {}'.format(item['id'], e))
            # see if we need to load the next page
            next_page_token = q_result.get('nextPageToken', [])
            if not next_page_token:
                break
            if len(res) >= limit:
                break
            q_result = self.service.users().threads().list(userId='me', maxResults = limit, q='{}'.format(q), pageToken=next_page_token).execute()


        # Sort by the latest timestamp of the last message on each thread
        res = sorted(res, key=lambda x: x.last_ts(), reverse=True)
        # Save full result of the query
        self.full_threads_by_query[q] = res

    def __update_history_id(self, thread_id, history_id=None):
        if history_id is None:
            history_id = self.service.users().threads().get(userId='me', id=thread_id, format='full').execute()['historyId']
        if thread_id not in self.thread_id_2_full_threads:
            self.le('Could not find thread id {} to update history id to {}'.format(thread_id, history_id))
            return
        self.thread_id_2_full_threads[thread_id]._set_history_id(history_id)
                
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
    def __load_drafts(self):
        draft_request = self.service.users().drafts().list(userId='me').execute()
        self.drafts = []
        while True:
            self.drafts.extend(draft_request.get('drafts', []))
            next_page_token = draft_request.get('nextPageToken', [])
            if not next_page_token:
                break
            draft_request = self.service.users().drafts().list(userId='me', pageToken=next_page_token).execute()

    def refresh(self):
        self.__populate_query_result(self.default_query, self.default_limit)
        self.__load_drafts()

    # Empty q is translated to the default query and is NOT rerequeried on the service
    # any other query we re run the actualy query to get an updated list of thread ids
    def query(self, q, limit):
        if q == '':
            q = self.default_query
        if limit <= 0:
            limit = self.default_limit
        # default query is preloaded
        if q in self.full_threads_by_query and q == self.default_query:
            return self.full_threads_by_query[q][:limit]

        # repopulate other queries each time to get the latest state
        # e.g. rule 1 adds an automation label, rule 2 has query label:automation
        # we'll need to run that query after executing rule 1
        self.__populate_query_result(q, limit)
        self.li('Query: \'{}\', limit {}, return: {}'.format(q, limit, self.full_threads_by_query[q][:limit]))
        return self.full_threads_by_query[q][:limit]

    def set_label(self, id, label_id, unset=False, userId='me'):
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
        self.__update_history_id(resp['id'], history_id=None)
        if 'labelIds' in resp:
            self.lw('Got small resp on set_label api call. label_id: {} label_name: {} unset {} Resp: {}'.format(label_id, self.label_id_2_string[label_id], unset, resp))
        return resp

    def get_drafts(self):
        return self.drafts

    def delete_draft(self, draft_id, userId='me'):
        # find the thread id
        for draft in self.drafts:
            if draft['id'] == draft_id:
                thread_id = draft['message']['threadId']
                break
        ret = self.service.users().drafts().delete(userId=userId, id=draft_id).execute()
        self.__update_history_id(thread_id, history_id=None)
        return ret
    def send_draft(self, draft_id):
        try:
            message_data = self.service.users().drafts().send(userId='me', body={'id' : draft_id }).execute()
            # get the full message
            full_message_data = self.service.users().messages().get(userId='me', id=message_data['id']).execute()
            message = GMailMessage(full_message_data, self)
            if message: # remove this draft id
                # TODO: better design to hold drafts in a map with draft id as the key
                for i, d in enumerate(self.drafts):
                    if d['id'] == draft_id:
                        del self.drafts[i]
                        break
            thread_map = self.service.users().threads().get(userId='me', id=full_message_data['threadId'], format='full').execute()
            thread = self.__create_thread_from_raw(thread_map)
            # Overwrite cached thread so we get the new history id on the THREAD when we send. Message history id is less 
            # than the thread history after a send
            self.thread_id_2_full_threads[thread.id()] = thread
            self.__update_history_id(thread.id(), thread_map['historyId'])
            return message
        except:
            return None

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
        self.__update_history_id(message_data['threadId'], message_data['historyId'])
        thread_map = self.service.users().threads().get(userId='me', id=message_data['threadId'], format='full').execute()
        thread_history_id = thread_map['historyId']
        if thread_history_id != message_data['historyId']:
            self.lw('append_or_create t hid: {} message hid {} thread {}'.format(thread_history_id, message_data['historyId'], thread_map['id']) )
        return GMailMessage(message_data, self)


    def __create_thread_from_raw(self, raw_thread):
        messages = []
        for message in raw_thread['messages']:
            messages.append(GMailMessage(message, self))
        return Thread(raw_thread['id'], messages, self, raw_thread['historyId'])
        #output_raw_thread('test/gmail_message_inputs/test_delimiter_2.txt', raw_thread)

    def __update_drafts(self, new_draft):
        for i, old_draft in enumerate(self.drafts):
            if new_draft['id'] == old_draft['id']:
                self.drafts[i] = new_draft # update with the new message id
                return
        self.drafts.append(new_draft)

def output_raw_thread(fn, thread_map):
    with open(fn, 'w+') as f:
        import json
        json.dump(thread_map, f, indent=4)

if __name__=='__main__':
    gs = GMailService('tgaldes@gmail.com', ["gmail.com"], "/home/tgaldes/Dropbox/Fraternity PM/dev_private/cfldv1_secret.json", "/home/tgaldes/Dropbox/Fraternity PM/dev_private/")

