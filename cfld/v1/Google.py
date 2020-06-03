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

class Google:
    def __init__(self, spreadsheet_id='1sQZiAi--Gj3V0O9oYfMsz78EJUHeDjjve2A5AsWDB-Y'):
        self.creds = self.__get_token()
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.spreadsheet_id = spreadsheet_id
        self.spreadsheet = self.__get_spreadsheet()

        # map name of sheet to data
        self.sheets = self.__get_sheets()

    def get_clean_data(self, sheet_name, ffill_columns):
        return dch.clean(self.sheets[sheet_name], ffill_columns)

    def get_header(self, sheet_name):
        return self.sheets[sheet_name][0]


    def __get_token(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('pickles/cfldv1_secret.pickle'):
            with open('pickles/cfldv1_secret.pickle', 'rb') as token:
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
        return self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()

    def __get_sheets(self):
        m = {}
        for sheet in self.spreadsheet.get('sheets'):
            title = sheet.get('properties').get('title')
# Get the data from this sheet
            range_name='{}!A1:Z1000'.format(title) # TODO
            m[title] = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute().get('values', [])
        return m


if __name__=='__main__':
    '''g = Google()
    with open('pickles/google.pickle', 'wb') as f:
        pickle.dump(g, f)'''
    with open('pickles/google.pickle', 'rb') as f:
        g2 = pickle.load(f)
    pdb.set_trace()
    b = dch.pad_short_rows(g2.sheets['addresses_clean'])
    a = dch.ffill(b, ['university', 'fraternity'])
