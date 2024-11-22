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

from framework.Config import Config

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# This class provides a base to connect to google sheets api and get rule construction information, which every org will need
class SheetService(Logger):
    def __init__(self, email, spreadsheet_id, secret_path, token_dir):
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
        self.rule_construction_data = None

        # load data from the 'config' sheet in the spreadsheet
        config_data = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='{}!A1:Z300'.format('config')).execute().get('values', [])
        if not config_data:
            self.lf('No info loaded for config data. Aborting.')
            exit(1)
        d = {}
        for row in config_data:
            if len(row) == 2:
                d[row[0]] = row[1]
            else:
                d[row[0]] = row[1:]

        self.config_data = d


    def set_rule_sheet_name(self, rule_sheet_name):
        self.rule_construction_data = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='{}!A1:P300'.format(rule_sheet_name)).execute().get('values', [])
        if not self.rule_construction_data:
            self.lf('No info loaded for rule construction data. Aborting.')
            exit(1)
        else:
            self.li('Loaded info to construct {} rules.'.format(len(self.rule_construction_data) - 1))

    def get_action_info(self):
        info = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='actions!A4:G200').execute().get('values', [])
        # info is a list of lists. each inner list has a single string element
        # combine them all into a single string then return
        d = {}
        for i, key in enumerate(info[0]):
            d[key] = ''
            for j in info[1:]:
                if len(j) <= i:
                    continue
                d[key] += j[i] + ' '
        return d

    def organize_llm_data_map(self, data):
        # data is a list of lists. each inner list has a single string element
        # combine them all into a single string then return
        d = {}
        for i, key in enumerate(data[0]):
            d[key] = []
            for j in data[1:]:
                if len(j) <= i:
                    continue
                d[key].append(j[i])
        return d

    def get_llm_draft_info(self):
        info = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='llm_draft_context!A4:G200').execute().get('values', [])
        return self.organize_llm_data_map(info)

    def get_llm_label_info(self):
        info = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='llm_label_context!A4:G200').execute().get('values', [])
        return self.organize_llm_data_map(info)

    def get_rule_construction_data(self):
        return self.rule_construction_data

    def check_reload(self):
        try:
            reload = int(self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='reload!A2:A2').execute().get('values', [])[0][0])
            if reload == 1:
                # reset reload flag on the sheet
                self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range='reload!A2:A2', body={'values': [[0]]}, valueInputOption='RAW').execute()
                return True
            else:
                return False
        except:
            return False

if __name__=='__main__':
    ss = SheetService('apply@cleanfloorslockingdoors.com')
    print(ss.get_rule_construction_data())
