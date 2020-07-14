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
import datetime
from Interfaces import ILetterSender
import spreadsheet_constants
SHEET_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
DOC_SCOPES = ['https://www.googleapis.com/auth/documents']

class Google(implements(ILetterSender)):
    def __init__(self, spreadsheet_id='1FXTd8S0OUK-dUV2flsX68G71YLFw37e2zY5DH-wqfoM', letter_id='1pHxpyICZrnwbNxyg8jBW_hXppQgqQNOVXnqWIdiucjU'):
        self.sheet_creds = self.__load_creds('pickles/cfldv1_sheet_secret.pickle', '/home/tgaldes/Dropbox/Fraternity PM/dev_private/cfldv1_secret.json', SHEET_SCOPES)
        self.letter_creds = self.__load_creds('pickles/cfldv1_letter_secret.pickle', '/home/tgaldes/Dropbox/Fraternity PM/dev_private/docs_credentials.json', DOC_SCOPES)
        self.sheet_service = build('sheets', 'v4', credentials=self.sheet_creds)
        self.spreadsheet_id = spreadsheet_id
        self.spreadsheet = self.__get_spreadsheet()

        # map name of sheet to data
        self.sheets_data, self.sheets = self.__get_sheets()

        # get sheet we'll output letters to
        self.letter_id = letter_id
        self.letter_service = build('docs', 'v1', credentials=self.letter_creds)

    def get_clean_data(self, sheet_name, ffill_columns):
        return dch.clean(self.sheets_data[sheet_name], ffill_columns)

    def get_header(self, sheet_name):
        return self.sheets_data[sheet_name][0]


    def __load_creds(self, pickle_path, json_path, scopes):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.pickle_path.exists(pickle_path):
            with open(pickle_path, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    json_path, scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            try:
                os.mkdir('pickles')
            except:
                pass
            with open(pickle_path, 'wb') as token:
                pickle.dump(creds, token)
        return creds
    
    def __get_spreadsheet(self):
        # Call the Sheets API
        return self.sheet_service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()

    def __get_sheets(self):
        m = {}
        sheets = {}
        for sheet in self.spreadsheet.get('sheets'):
            title = sheet.get('properties').get('title')
# Get the data from this sheet
            range_name='{}!A1:Z1000'.format(title) # TODO
            sheets[title] = self.sheet_service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
            m[title] = sheets[title].get('values', [])
        return m, sheets


# TODO: letter sending interface
# This will allow classes to append a string to a Google Sheet
#ILetterSender
    def send_mail(self, address, msg, contact_info):
        print('Sending: "{}"\nAddress:\n{}'.format(msg, address))
        self.__append_to_letter_doc(address, msg)
        self.__log_contact(contact_info, MailType.MAIL)
    def __append_to_letter_doc(self, address, msg):
        # TODO: append the page break instead of prepend
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

# This will allow classes to make a note of the dates on which Contacts were messaged via email or snail mail
    def __log_contact(self, contact_info, mail_type_enum):
        #print('Implement log_contact so that we can make a note of contacting {} via {} on {}:\n'.format(contact_info.short_name, mail_type_enum, date.today()))
        #print(self.sheets_data['addresses_clean'])
# get row number
        sheet_data = self.sheets_data[spreadsheet_constants.sheet_names['contacts']]
        sheet = self.sheets[spreadsheet_constants.sheet_names['contacts']]
        row_num = 1
        for i, row in enumerate(sheet_data):
            if row[0] == contact_info.short_name \
                    and row[1] == contact_info.fraternity \
                    and row[2] == contact_info.name:
                row_num += i
                print('match for {} at row {}'.format(row[2], i + 1))
                break

# get column from constants
        col_num = 1 + sheet_data[0].index(spreadsheet_constants.mail_date_column_name)
        r = spreadsheet_constants.range_builder[col_num] + str(row_num)
        rangeName = "addresses_clean!{}".format(r)
        values = [[datetime.date.today().strftime('%Y%m%d')]]
        Body = {
            'values' : values,
        }

        result = self.sheet_service.spreadsheets().values().update(
        spreadsheetId=self.spreadsheet_id, range=rangeName,
        valueInputOption='RAW', body=Body).execute()
# create range
# update request


if __name__=='__main__':
    g = Google()
    with open('pickles/google.pickle', 'wb') as f:
        pickle.dump(g, f)
    with open('pickles/google.pickle', 'rb') as f:
        g2 = pickle.load(f)
    pdb.set_trace()
    b = dch.pad_short_rows(g2.sheets['addresses_clean'])
    a = dch.ffill(b, ['university', 'fraternity'])
