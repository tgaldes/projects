from __future__ import print_function
import sys
import pprint
from time import sleep
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
from global_funcs import safe_get_attr, parse_for_bullets, get_qr_code_url



SHEET_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
DOC_SCOPES = ['https://www.googleapis.com/auth/documents']
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']
pp = pprint.PrettyPrinter(indent=4)


class Google(implements(ILetterSender), implements(IEmailSender)):
    def __init__(self, \
            # PROD
            #spreadsheet_id='1dtHBRLoCbR5XJtl8T6DAZtdn_mpW1y4FR25myf1MK2g', \
            # TEST
            spreadsheet_id='1Hx3ln_nlHuoU7UTRo5ZsEOSqQU2MP8zn27FViQ5wbl8', \
            letter_id='1pHxpyICZrnwbNxyg8jBW_hXppQgqQNOVXnqWIdiucjU'):

        self.sheet_creds = self.__load_creds('pickles/cfldv1_sheet_secret.pickle', '/home/tgaldes/Dropbox/Fraternity PM/dev_private/cfldv1_secret.json', SHEET_SCOPES)
        self.letter_creds = self.__load_creds('pickles/cfldv1_letter_secret.pickle', '/home/tgaldes/Dropbox/Fraternity PM/dev_private/docs_credentials.json', DOC_SCOPES)
        self.drive_creds = self.__load_creds('pickles/cfldv1_drive_secret.pickle', '/home/tgaldes/Dropbox/Fraternity PM/dev_private/drive_credentials.json', DRIVE_SCOPES)
        self.sheet_service = build('sheets', 'v4', credentials=self.sheet_creds)
        self.spreadsheet_id = spreadsheet_id
        self.spreadsheet = self.__get_spreadsheet(self.spreadsheet_id)
        self.parent_mailer_folder_id = '15--fLcMPKG_Au0HIbo4Q30VCWzw9j0vl'

        # map name of sheet to data
        self.sheets_data, self.sheets = self.__get_sheets(self.spreadsheet, self.spreadsheet_id)

        # get sheet we'll output letters to
        #self.letter_id = letter_id
        self.letter_service = build('docs', 'v1', credentials=self.letter_creds)


        self.drive_service = build('drive', 'v3', credentials=self.drive_creds)

        now_string = datetime.datetime.now().strftime('%Y%m%d %H:%M')
        self.folder_id = self.__create_folder(now_string)
        self.address_letter_sheet_id = self.__create_address_sheet(now_string)
        self.address_letter_sheet = self.__get_spreadsheet(self.address_letter_sheet_id)
        self.address_letter_sheet_data, self.address_letter = self.__get_sheets(self.address_letter_sheet, self.address_letter_sheet_id)
        self.address_letter_row_num = 0
        self.__get_one_line_addresses()
        self.__get_bad_names()

    def get_clean_data(self, sheet_name, ffill_columns):
        return dch.clean(self.sheets_data[sheet_name], ffill_columns)

    def get_header(self, sheet_name):
        return self.sheets_data[sheet_name][0]
    
    def get_last_date_for_contact(self, data, enum):
        sheet_data = self.sheets_data[spreadsheet_constants.sheet_names['contacts']]
        return self.__get_last_mailed_date(data, enum, sheet_data, spreadsheet_constants.columns_that_define_unique_contact)

    def get_last_date_for_house(self, data, enum):
        sheet_data = self.sheets_data[spreadsheet_constants.sheet_names['houses']]
        return self.__get_last_mailed_date(data, enum, sheet_data, spreadsheet_constants.columns_that_define_unique_house)

# Take a list of urls visited and add any new dates to the rows of the csv with the matching url
# visits is list of [(url, date)....]
    def update_page_visits(self, visits):
# TODO: the matching is similar to __log_contact, we can have a generic func that finds the matching row based on the info we have availble
        total_logged = 0
        for url, date in visits:
            # try to find a match in the contact data
            row_num = 1
# try to match a contact
            sheet_data = self.sheets_data[spreadsheet_constants.sheet_names['contacts']]
            range_name = "addresses_clean!{}"
            for i, row in enumerate(sheet_data):
# only match when we look at the contact sheet, otherwise look at a match in houses # TODO: this is a kind of hacky way to figure out how we know if we're using a contact or a house
                if row \
                        and url in row[spreadsheet_constants.contact_data_header.index('unique_url')]:
                        row_num += i
                        print('match for {} at row {} in contacts sheet'.format(url, i + 1))
                        break
            if row_num == 1:
                # try to find a match in the house data
                sheet_data = self.sheets_data[spreadsheet_constants.sheet_names['houses']]
                range_name = "houses!{}"
                for i, row in enumerate(sheet_data):
                    if row \
                            and url in row[spreadsheet_constants.house_data_header.index('unique_url')]:
                        row_num += i
                        print('match for {} at row {} in house sheet'.format(row[spreadsheet_constants.contact_data_header.index('unique_url')], i + 1))
                        break

            if row_num == 1:
                print('No match for url {}'.format(url)) # There will be urls in the log that don't match anyone from my testing
                continue
# get column from constants
            col_num = 1 + sheet_data[0].index(spreadsheet_constants.unique_url_visited_column_name)
            if col_num == 1:
                raise Exception('Column number of unique url visited on sheet is misconfigured, aborting.')
            r = spreadsheet_constants.range_builder[col_num] + str(row_num)
            range_name = range_name.format(r)

# get the current value of the cell so we can append today's datetime
            current_value = sheet_data[row_num - 1][col_num - 1]
            values = [[current_value + date.strftime('%Y%m%d') + '\n']]
            body = {
                'values' : values,
            }

            result = self.__exponential_backoff('''self.sheet_service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=args[0], valueInputOption='RAW', body=args[1]).execute()''', range_name, body)
            total_logged += 1
        print('Recorded a total of {} visits, it is now safe to clear the logs of redirect in wordpress to avoid seeing duplicates'.format(total_logged))

    def __create_address_sheet(self, now_string):
        file_metadata = {
            'name': 'addresses_{}'.format(now_string),
            'parents': [self.folder_id],
            'mimeType': 'application/vnd.google-apps.spreadsheet',
        }
        response = self.__exponential_backoff('''self.drive_service.files().create(body=args[0]).execute()''', file_metadata)
        return response.get('id')
    def __create_folder(self, now_string):
        file_metadata = {
                'name': 'mailer_{}'.format(now_string),
                'mimeType': 'application/vnd.google-apps.folder',
                'parents' : [self.parent_mailer_folder_id]
        }
        file = self.__exponential_backoff('''self.drive_service.files().create(body=args[0], fields='id').execute()''', file_metadata)
        return file.get('id')

    def __get_last_mailed_date(self, data, enum, haystack, num_columns):
        header = haystack[0]
        if enum == MailType.EMAIL:
            col_name = spreadsheet_constants.email_date_column_name
        elif enum == MailType.MAIL:
            col_name = spreadsheet_constants.mail_date_column_name
        else:
            raise Exception('Unsupported MailType enum')
        last_action_column_index = haystack[0].index(col_name)
        for attempt in haystack:
            if data[:num_columns] == tuple(attempt[:num_columns]):
                last_date_str = attempt[last_action_column_index].strip('\n').split('\n')[-1]
                if not last_date_str:
                    return datetime.date(1970, 1, 1)
                last_date = datetime.datetime.strptime(last_date_str, '%Y%m%d').date()
                return last_date
        raise Exception('Could not find match for last action for type: {} values we tried to match: {}'.format(enum, data[:num_columns])) 


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
        a = self.__exponential_backoff('''self.sheet_service.spreadsheets().get(spreadsheetId=args[0]).execute()''', id_)
        return a

    def __get_sheets(self, spreadsheet, id_):
        m = {}
        sheets = {}
        for sheet in spreadsheet.get('sheets'):
            title = sheet.get('properties').get('title')
# Get the data from this sheet
            range_name='{}!A1:Z2500'.format(title) # TODO
            sheets[title] = self.__exponential_backoff('''self.sheet_service.spreadsheets().values().get(spreadsheetId=args[0], range=args[1]).execute()''', id_, range_name)
            m[title] = sheets[title].get('values', [])
        return m, sheets


#IEmailSender
    def send_email(self, subject, msg, contact_info):
        print('Implement sending email with msg: {}'.format(msg))
        self.__log_contact(contact_info, MailType.EMAIL)
#ILetterSender
    def send_mail(self, address, msg, contact):
        doc = self.__create_doc(contact.data)
        if not self.__update_address_list(address, doc, contact.get_name()):
            return
        self.__append_to_letter_doc(msg, doc, contact.data)
        self.__log_contact(contact.data, MailType.MAIL)
# will add the name of the document and address it should be sent to
    def __update_address_list(self, address, doc, contact_name):
        title = doc.get('title') + '.pdf'
        sheet_data = self.address_letter_sheet_data['Sheet1']

        if self.address_letter_row_num == 0:
            self.address_letter_row_num = len(sheet_data) + 1
        else:
            self.address_letter_row_num += 1
# schema is A:Address line 1, B:Address line 2, C:Address line 3, D:file name, E:recipient name
# get column from constants
        r = spreadsheet_constants.range_builder[1] + str(self.address_letter_row_num) + ':' + spreadsheet_constants.range_builder[5] + str(self.address_letter_row_num)
        range_name = "Sheet1!{}".format(r)

# get the current value of the cell so we can append today's datetime
        address_lines = address.split('\n')
        for i, line in enumerate(address_lines):
            address_lines[i] = line.strip().strip(',')
        if len(address_lines) == 3:
            pass
        elif len(address_lines) == 2:
            address_lines.insert(1, '')
        elif len(address_lines) > 3:
            print('ERROR: Address had too many lines: {}'.format(address_lines))
            return False # TODO
            raise Exception('Address had too many lines: {}'.format(address_lines))
        else:
            print('ERROR: Address had only one line: {}'.format(address_lines))
            return False # TODO: would rather throw and fix the issue in the data
            raise Exception('Address had only one line: {}'.format(address_lines))
        values = [[*address_lines, title, contact_name]]
        body = {
            'values' : values,
        }

        result = self.__exponential_backoff('''self.sheet_service.spreadsheets().values().update(spreadsheetId=self.address_letter_sheet_id, range=args[0], valueInputOption='RAW', body=args[1]).execute()''', range_name, body)
        return True

# will create a doc and move it to the appropriate folder
    def __create_doc(self, contact_info):
        title = '{} {} {}'.format(contact_info.short_name, contact_info.fraternity, safe_get_attr(contact_info, 'name')) # TODO: same format as creating the letter
        title = contact_info.qr_code_file_name[:-4] # remove the '.png'
        body = {
                'title': title
        }
        doc = self.__exponential_backoff('''self.letter_service.documents().create(body=args[0]).execute()''', body)
        print('Created document with title: {0}'.format(
            doc.get('title')))
        file_id = doc.get('documentId')
# move it to dev sandbox
        file = self.__exponential_backoff('''self.drive_service.files().get(fileId=args[0], fields='parents').execute()''', file_id)
        previous_parents = ",".join(file.get('parents'))
# Move the file to the new folder
        self.__exponential_backoff('''self.drive_service.files().update(fileId=args[0], addParents=self.folder_id, removeParents=args[1], fields='id, parents').execute()''', file_id, previous_parents)
        return doc

# return (list of requests for each text/bullet paragraph,
#           list of createParagraphBulletRequests)
# start offset defaulted to 2 since we'll have 1 inline image before the text 
# and google docs is 1 indexed
    def __create_text_inserts_to_doc(self, msg, start_offset=2):
        tups = parse_for_bullets(msg)
        #print(tups)
        insert_text_reqs = []
        format_reqs = []
        index = start_offset
        for p, is_bullet in tups:
            if is_bullet:
                start_index = index
                end_index = index + len(p)
                format_reqs.insert(0,
                {
                    'createParagraphBullets': {
                        'range': {
                            'startIndex': start_index,
                            'endIndex':  end_index
                        },
                        'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE',
                    }
                })
            # we'll update the index and add to the text requests for all text
            insert_text_reqs.insert(0,
            {
                'insertText': 
                {
                    'location': 
                    {
                        'index': 1,
                    },
                    'text': p
                }
            })
            index += len(p)
        #print(insert_text_reqs)
        #print(format_reqs)
        return insert_text_reqs, format_reqs, index


    def __append_to_letter_doc(self, msg, doc, contact_info):
        text_reqs, format_reqs, full_msg_size = self.__create_text_inserts_to_doc(msg)
        requests = [
        {
            'insertInlineImage': 
            {
                'location': 
                {
                    'index': 1
                },
                #'uri': 'https://cleanfloorslockingdoors.com/wp-content/uploads/2020/07/frame.png',#get_qr_code_url(contact_info), TODO
                'uri': get_qr_code_url(contact_info),
                
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
        }, \
        *text_reqs,
        {
            'insertInlineImage': 
            {
                'location': 
                {
                    'index': 1
                },
                'uri':
                'https://cleanfloorslockingdoors.com/wp-content/uploads/2020/08/logo_clipped_rev_1.png',
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
        }, \
        *format_reqs,
        {
            'updateDocumentStyle' : 
            {
                'documentStyle' : 
                {
                    'marginBottom' : 
                    {
                        'magnitude' : 36,
                        'unit' : 'PT'
                    }
                },
                'fields' : 'marginBottom'
            }
        }, \
        {
            'updateDocumentStyle' : 
            {
                'documentStyle' : 
                {
                    'marginTop' : 
                    {
                        'magnitude' : 36,
                        'unit' : 'PT'
                    }
                },
                'fields' : 'marginTop'
            }
        }, \
        {
            "updateParagraphStyle": 
            {
                "range": 
                {
                    "startIndex": full_msg_size + 1,
                    "endIndex": full_msg_size + 1,
                },
                "paragraphStyle": 
                {
                    "alignment": "END"
                },
                "fields": "alignment"
            }
        }
        ]
        #pp.pprint(requests)
        result = self.__exponential_backoff('''self.letter_service.documents().batchUpdate(documentId=args[0], body={'requests': args[1]}).execute()''', doc.get('documentId'), requests)

# This will allow classes to make a note of the dates on which Contacts were messaged via email or snail mail
    def __log_contact(self, contact_info, mail_type_enum):
# get row number
        sheet_data = self.sheets_data[spreadsheet_constants.sheet_names['contacts']]
        range_name = "addresses_clean!{}"
        row_num = 1
# try to match a contact
        for i, row in enumerate(sheet_data):
# only match when we look at the contact sheet, otherwise look at a match in houses # TODO: this is a kind of hacky way to figure out how we know if we're using a contact or a house
            if row and 'name' in contact_info._fields \
                    and row[0] == contact_info.short_name \
                    and row[1] == contact_info.fraternity:
                if mail_type_enum == MailType.MAIL and row[spreadsheet_constants.contact_data_header.index('address')] == contact_info.address:
                    row_num += i
                    print('match for {} at row {} in contacts sheet'.format(row[2], i + 1))
                    break
        if row_num == 1:
# try to match a house
            sheet_data = self.sheets_data[spreadsheet_constants.sheet_names['houses']]
            range_name = "houses!{}"
            for i, row in enumerate(sheet_data):
                if row and row[0] == contact_info.short_name \
                    and row[1] == contact_info.fraternity:
                    row_num += i
                    print('match for {} at row {} in houses sheet'.format(row[1], i + 1))
                    break

        if row_num == 1:
            print('ERROR: could not find a match for {} {} {}'.format(contact_info.short_name, contact_info.fraternity, safe_get_attr(contact_info, 'name')))
            return
# get column from constants
        col_num = 1 + sheet_data[0].index(spreadsheet_constants.mail_type_enum_to_column_name[mail_type_enum])
        if col_num == 1:
            raise Exception('Column number of mail date tracking column on sheet is misconfigured, aborting.')
        r = spreadsheet_constants.range_builder[col_num] + str(row_num)
        range_name = range_name.format(r)

# get the current value of the cell so we can append today's datetime
        current_value = sheet_data[row_num - 1][col_num - 1]
        values = [[current_value + datetime.date.today().strftime('%Y%m%d') + '\n']]
        body = {
            'values' : values,
        }

        result = self.__exponential_backoff('''self.sheet_service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=args[0], valueInputOption='RAW', body=args[1]).execute()''', range_name, body)

    def __exponential_backoff(self, request, *args):
        local_request = 'local_result = ' + request
        attempts = 0
        max_attempts = 5
        start_backoff = 2
        while attempts <= max_attempts:
            attempts += 1
            try:
                exec(local_request)
                return locals()['local_result']
            except Exception as e:
                print(local_request)
                print(str(e))
                print('Received error from google, backing off {} seconds and retrying. ({}/{}) attempts made.'.format(start_backoff, attempts, max_attempts))
                sleep(start_backoff)
                start_backoff *= 2
        raise Exception('Reach max exponential backoff attempts ({}), raising exception'.format(attempts))
                
# -------------- One/two of test functions ----------------------- #
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
    def __get_bad_names(self):
        sheet_data = self.sheets_data[spreadsheet_constants.sheet_names['contacts']]
        name_col_num = sheet_data[0].index('name')
        rows = []
        for i, row in enumerate(sheet_data):
            if i == 0: continue # skip header
            if row and row[name_col_num] and ((len(row[name_col_num].split()) != 2 and len(row[name_col_num].split()) != 3) or ',' in row[name_col_num]):
                rows.append((i + 1, row[name_col_num]))
        print('The following names might be more than (first, last)')
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
