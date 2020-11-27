from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pdb

from Logger import Logger

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# This class is kept very simple for now
# Will just load and make available a 2D array of the prod_rules named sheet
class SheetService(Logger):
    def __init__(self, email, sheet_name):
        super(SheetService, self).__init__(__name__)
        self.li('Creating {} for {}'.format(__name__, email))

        self.spreadsheet_id = '1cJ4fUFiOak98GAVBwqwcdJmN34cXPtWTzdLzMruisoI'


        self.user = email.split('@')[0]
        creds = None
        pickle_path = 'token.sheets.{}.pickle'.format(self.user)
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
        self.service = build('sheets', 'v4', credentials=creds)
        self.rule_construction_data = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='{}_rules!A1:N100'.format(sheet_name)).execute().get('values', [])
        if not self.rule_construction_data:
            self.lf('No info loaded for rule construction data. Aborting.')
            exit(1)
        else:
            self.li('Loaded info to construct {} rules.'.format(len(self.rule_construction_data) - 1))

        self.lookup_info_data = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='lookup_info!A1:C100'.format(sheet_name)).execute().get('values', [])

        self.availability = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='availability!A1:E100'.format(sheet_name)).execute().get('values', [])
        self.availability_blurbs = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='availability!I1:N3'.format(sheet_name)).execute().get('values', [])

    def get_rule_construction_data(self):
        return self.rule_construction_data

    def get_lookup_info_data(self):
        return self.lookup_info_data

    def get_availability(self):
        return self.availability

    def get_availability_blurbs(self):
        return self.availability_blurbs

if __name__=='__main__':
    ss = SheetService('apply@cleanfloorslockingdoors.com')
    print(ss.get_rule_construction_data())
