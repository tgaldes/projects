from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pdb
from interface import implements

from framework.Logger import Logger
from framework.Interfaces import IOrg

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# This class provides a base to connect to google sheets api and get rule construction information, which every org will need
class SheetService(Logger):
    def __init__(self, email, sheet_name, spreadsheet_id, secret_path, token_dir):
        super(SheetService, self).__init__(__class__)
        self.li('Creating: for {}'.format(email))

        self.spreadsheet_id = spreadsheet_id


        self.user = email.split('@')[0]
        creds = None
        pickle_path = os.path.join(token_dir, 'token.sheets.{}.pickle'.format(self.user))
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
        self.service = build('sheets', 'v4', credentials=creds)
        self.rule_construction_data = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='{}!A1:P300'.format(sheet_name)).execute().get('values', [])
        if not self.rule_construction_data:
            self.lf('No info loaded for rule construction data. Aborting.')
            exit(1)
        else:
            self.li('Loaded info to construct {} rules.'.format(len(self.rule_construction_data) - 1))


    def get_rule_construction_data(self):
        return self.rule_construction_data

if __name__=='__main__':
    ss = SheetService('apply@cleanfloorslockingdoors.com')
    print(ss.get_rule_construction_data())
