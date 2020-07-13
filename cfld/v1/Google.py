from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import collections
import pdb
import pickle
import data_cleanup_helpers as dch

from interface import implements

from enums import MailType
from datetime import date
from Interfaces import ILetterSender

class Google(implements(ILetterSender)):
    def __init__(self, spreadsheet_id='1sQZiAi--Gj3V0O9oYfMsz78EJUHeDjjve2A5AsWDB-Y', letter_id='1pHxpyICZrnwbNxyg8jBW_hXppQgqQNOVXnqWIdiucjU'):
        self.sheet_creds = self.__load_creds('pickles/cfldv1_sheet_secret.pickle')
        self.letter_creds = self.__load_creds('pickles/cfldv1_letter_secret.pickle')
        self.sheet_service = build('sheets', 'v4', credentials=self.sheet_creds)
        self.spreadsheet_id = spreadsheet_id
        self.spreadsheet = self.__get_spreadsheet()

        # map name of sheet to data
        self.sheets = self.__get_sheets()

        # get sheet we'll output letters to
        self.letter_id = letter_id
        self.letter_service = build('docs', 'v1', credentials=self.letter_creds)
        #self.letters = self.__get_letter_sheet()

    '''def __get_letter_sheet(self):

        service = build('docs', 'v1', credentials=creds)
        # Retrieve the documents contents from the Docs service.
        return service.documents().get(documentId=self.letter_id).execute()'''

    def get_clean_data(self, sheet_name, ffill_columns):
        return dch.clean(self.sheets[sheet_name], ffill_columns)

    def get_header(self, sheet_name):
        return self.sheets[sheet_name][0]


    def __load_creds(self, path):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(path):
            with open(path, 'rb') as token:
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
            try:
                os.mkdir('pickles')
            except:
                pass
            with open('pickles/cfldv1_secret.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds
    
    def __get_spreadsheet(self):
        # Call the Sheets API
        return self.sheet_service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()

    def __get_sheets(self):
        m = {}
        for sheet in self.spreadsheet.get('sheets'):
            title = sheet.get('properties').get('title')
# Get the data from this sheet
            range_name='{}!A1:Z1000'.format(title) # TODO
            m[title] = self.sheet_service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute().get('values', [])
        return m


# TODO: letter sending interface
# This will allow classes to append a string to a Google Sheet
#ILetterSender
    def send_mail(self, address, msg):
        print('Sending: "{}"\nAddress:\n{}'.format(msg, address))
        self.__append_to_letter_doc(address, msg)
    def __append_to_letter_doc(self, address, msg):
        # Note: actually preprends but either end is ok :)
        requests = [
        {
            'insertText': 
            {
                'location': 
                {
                    'index': 1,
                },
                'text': '{}\n\n{}'.format(address, msg)
            } \
        }
        , \
        {
            'insertPageBreak': 
            {
                'location' :
                {
                    'index': 1
                }
            }
        }
        ]
        #{'paragraph': {'elements': [{'pageBreak': {'textStyle': {}}, 'startIndex': 1, 'endIndex': 2}
        result = self.letter_service.documents().batchUpdate(
                documentId=self.letter_id, body={'requests': requests}).execute()
        #print('Implement appending to letter doc so that we can append the message:\n {}'.format(msg))
# TODO: track contacts interface
# This will allow classes to make a note of the dates on which Contacts were messaged via email or snail mail
    def log_contact(self, contact, mail_type_enum):
        print('Implement log_contact so that we can make a note of contacting {} via {} on {}:\n {}'.format(contact.name(), mail_type, date.today()))


if __name__=='__main__':
    g = Google()
    with open('pickles/google.pickle', 'wb') as f:
        pickle.dump(g, f)
    with open('pickles/google.pickle', 'rb') as f:
        g2 = pickle.load(f)
    pdb.set_trace()
    b = dch.pad_short_rows(g2.sheets['addresses_clean'])
    a = dch.ffill(b, ['university', 'fraternity'])
