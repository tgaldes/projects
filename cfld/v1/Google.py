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
from Interfaces import ILetterSender, IEmailSender
import spreadsheet_constants
from global_funcs import safe_get_attr



SHEET_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
DOC_SCOPES = ['https://www.googleapis.com/auth/documents']
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']

class Google(implements(ILetterSender), implements(IEmailSender)):
    def __init__(self, \
            # PROD
            #spreadsheet_id='1dtHBRLoCbR5XJtl8T6DAZtdn_mpW1y4FR25myf1MK2g', \
            # TEST
            spreadsheet_id='1FXTd8S0OUK-dUV2flsX68G71YLFw37e2zY5DH-wqfoM', \
            letter_id='1pHxpyICZrnwbNxyg8jBW_hXppQgqQNOVXnqWIdiucjU'):

        self.sheet_creds = self.__load_creds('pickles/cfldv1_sheet_secret.pickle', '/home/tgaldes/Dropbox/Fraternity PM/dev_private/cfldv1_secret.json', SHEET_SCOPES)
        self.letter_creds = self.__load_creds('pickles/cfldv1_letter_secret.pickle', '/home/tgaldes/Dropbox/Fraternity PM/dev_private/docs_credentials.json', DOC_SCOPES)
        self.drive_creds = self.__load_creds('pickles/cfldv1_drive_secret.pickle', '/home/tgaldes/Dropbox/Fraternity PM/dev_private/drive_credentials.json', DRIVE_SCOPES)
        self.sheet_service = build('sheets', 'v4', credentials=self.sheet_creds)
        self.spreadsheet_id = spreadsheet_id
        self.spreadsheet = self.__get_spreadsheet(self.spreadsheet_id)

        # map name of sheet to data
        self.sheets_data, self.sheets = self.__get_sheets(self.spreadsheet, self.spreadsheet_id)

        # get sheet we'll output letters to
        #self.letter_id = letter_id
        self.letter_service = build('docs', 'v1', credentials=self.letter_creds)


        self.drive_service = build('drive', 'v3', credentials=self.drive_creds)
        self.address_letter_sheet_id = '1ebQ9mO9ciodQX7DtkrQ-k_zbK-94A_mkHX4kO8TWIDs'
        self.address_letter_sheet = self.__get_spreadsheet(self.address_letter_sheet_id)
        self.address_letter_sheet_data, self.address_letter = self.__get_sheets(self.address_letter_sheet, self.address_letter_sheet_id)
        self.address_letter_row_num = 0
        #self.__get_one_line_addresses()

    def get_clean_data(self, sheet_name, ffill_columns):
        return dch.clean(self.sheets_data[sheet_name], ffill_columns)

    def get_header(self, sheet_name):
        return self.sheets_data[sheet_name][0]


    def __load_creds(self, pickle_path, json_path, scopes):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(pickle_path):
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
    
    def __get_spreadsheet(self, id_):
        # Call the Sheets API
        return self.sheet_service.spreadsheets().get(spreadsheetId=id_).execute()

    def __get_sheets(self, spreadsheet, id_):
        m = {}
        sheets = {}
        for sheet in spreadsheet.get('sheets'):
            title = sheet.get('properties').get('title')
# Get the data from this sheet
            range_name='{}!A1:Z2500'.format(title) # TODO
            sheets[title] = self.sheet_service.spreadsheets().values().get(spreadsheetId=id_, range=range_name).execute()
            m[title] = sheets[title].get('values', [])
        return m, sheets


#IEmailSender
    def send_email(self, subject, msg, contact_info):
        print('Implement sending email with msg: {}'.format(msg))
        self.__log_contact(contact_info, MailType.EMAIL)
#ILetterSender
    def send_mail(self, address, msg, contact_info):
        print('Sending: "{}"\nAddress:\n{}'.format(msg, address))
        doc = self.__create_doc(contact_info)
        if not self.__update_address_list(address, doc):
            return
        self.__append_to_letter_doc(msg, doc)
        self.__log_contact(contact_info, MailType.MAIL)
# will add the name of the document and address it should be sent to
    def __update_address_list(self, address, doc):
        title = doc.get('title') + '.pdf'
        sheet_data = self.address_letter_sheet_data['Sheet1']

        if self.address_letter_row_num == 0:
            self.address_letter_row_num = len(sheet_data) + 1
        else:
            self.address_letter_row_num += 1
# schema is A:Address line 1, B:Address line 2, C:Address line 3, D:file name
# get column from constants
        r = spreadsheet_constants.range_builder[1] + str(self.address_letter_row_num) + ':' + spreadsheet_constants.range_builder[4] + str(self.address_letter_row_num)
        rangeName = "Sheet1!{}".format(r)

# get the current value of the cell so we can append today's datetime
        address_lines = address.split('\n')
        for line in address_lines:
            line = line.strip().strip(',')
        if len(address_lines) == 3:
            pass
        elif len(address_lines) == 2:
            address_lines.insert(1, '')
        elif len(address_lines) > 3:
            print('Address had too many lines: {}'.format(address_lines))
            return False # TODO
            #raise Exception('Address had too many lines: {}'.format(address_lines))
        else:
            print('Address had only one line: {}'.format(address_lines))
            return False # TODO: would rather throw and fix the issue in the data
            #raise Exception('Address had only one line: {}'.format(address_lines))
        values = [[*address_lines, title]]
        Body = {
            'values' : values,
        }

        result = self.sheet_service.spreadsheets().values().update(
        spreadsheetId=self.address_letter_sheet_id, range=rangeName,
        valueInputOption='RAW', body=Body).execute()
        return True

# will create a doc and move it to the appropriate folder
    def __create_doc(self, contact_info):
        folder_id = '1XDba_UUbCoXkbRnjF9N0ju22ksWHcBGm' # TODO: not hardcoded/update to prod folder
        title = '{} {} {}'.format(contact_info.short_name, contact_info.fraternity, safe_get_attr(contact_info, 'name')) # TODO: same format as creating the letter
        body = {
                'title': title
        }
        doc = self.letter_service.documents() \
        .create(body=body).execute()
        print('Created document with title: {0}'.format(
            doc.get('title')))
        file_id = doc.get('documentId')
# move it to dev sandbox
        file = self.drive_service.files().get(fileId=file_id,
                                         fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
# Move the file to the new folder
        file = self.drive_service.files().update(fileId=file_id,
                                            addParents=folder_id,
                                            removeParents=previous_parents,
                                            fields='id, parents').execute()
        return doc

# TODO: don't format 'full_msg' and have the caller send that themselves, they can still pass address as a separate arg so we can do whatever our letter service needs here
    def __append_to_letter_doc(self, msg, doc):
        full_msg = '\n\n\n\n\n{}\n'.format(msg)
        requests = [
        {
            'insertInlineImage': 
            {
                'location': 
                {
                    'index': 1
                },
                'uri':
                'https://cleanfloorslockingdoors.com/wp-content/uploads/2020/07/frame.png',
                'objectSize': 
                {
                    'height': 
                    {
                        'magnitude': 100,
                        'unit': 'PT'
                    },
                    'width': 
                    {
                        'magnitude': 100,
                        'unit': 'PT'
                    }
                }
            }
        }
        , \
        {
            'insertText': 
            {
                'location': 
                {
                    'index': 1,
                },
                'text': full_msg
            } \
        }, \
        {
            "updateParagraphStyle": 
            {
                "range": 
                {
                    "startIndex": 1,
                    "endIndex": len(full_msg) + 1
                },
                "paragraphStyle": 
                {
                    "alignment": "START"
                },
                "fields": "alignment"
            }
        } \
        ,{
            "updateParagraphStyle": 
            {
                "range": 
                {
                    "startIndex": len(full_msg) + 1,
                    "endIndex": len(full_msg) + 1,
                },
                "paragraphStyle": 
                {
                    "alignment": "END"
                },
                "fields": "alignment"
            }
        }
        ]
        result = self.letter_service.documents().batchUpdate(
                documentId=doc.get('documentId'), body={'requests': requests}).execute()

# This will allow classes to make a note of the dates on which Contacts were messaged via email or snail mail
    def __log_contact(self, contact_info, mail_type_enum):
# get row number
        sheet_data = self.sheets_data[spreadsheet_constants.sheet_names['contacts']]
        row_num = 1
        # TODO: look at house data as well here
        for i, row in enumerate(sheet_data):
            if row[0] == contact_info.short_name \
                    and row[1] == contact_info.fraternity \
                    and row[2] == safe_get_attr(contact_info, 'name'):
                row_num += i
                print('match for {} at row {}'.format(row[2], i + 1))
                break
        if row_num == 1:
            print('ERROR: could not find a match for {} {} {}'.format(contact_info.short_name, contact_info.fraternity, safe_get_attr(contact_info, 'name')))
            return
# get column from constants
        col_num = 1 + sheet_data[0].index(spreadsheet_constants.mail_type_enum_to_column_name[mail_type_enum])
        if col_num == 1:
            raise Exception('Column number of mail date tracking column on sheet is misconfigured, aborting.')
        r = spreadsheet_constants.range_builder[col_num] + str(row_num)
        rangeName = "addresses_clean!{}".format(r)

# get the current value of the cell so we can append today's datetime
        current_value = sheet_data[row_num - 1][col_num - 1]
        values = [[current_value + datetime.date.today().strftime('%Y%m%d') + '\n']]
        Body = {
            'values' : values,
        }

        result = self.sheet_service.spreadsheets().values().update(
        spreadsheetId=self.spreadsheet_id, range=rangeName,
        valueInputOption='RAW', body=Body).execute()

# output the row numbers of addresses that are only one line
    def __get_one_line_addresses(self):
        sheet_data = self.sheets_data[spreadsheet_constants.sheet_names['contacts']]
        address_col_num = sheet_data[0].index(spreadsheet_constants.address_column_name)
        rows = []
        for i, row in enumerate(sheet_data):
            if i == 0: continue # skip header
            if row and row[address_col_num] and row[address_col_num].count('\n') == 0:
                rows.append(i + 1)
        print('The following rows have addresses that only have one line:')
        for row in rows:
            print(row)
                

        


if __name__=='__main__':
    g = Google()
    '''with open('pickles/google.pickle', 'wb') as f:
        pickle.dump(g, f)
    with open('pickles/google.pickle', 'rb') as f:
        g2 = pickle.load(f)'''
    b = dch.pad_short_rows(g2.sheets['addresses_clean'])
    a = dch.ffill(b, ['university', 'fraternity'])
