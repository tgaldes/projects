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
from copy import copy

from interface import implements

from enums import MailType
import datetime
from Interfaces import ILetterSender, IEmailSender
import spreadsheet_constants as sc
from global_funcs import safe_get_attr, parse_for_bullets, get_qr_code_url



SHEET_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
DOC_SCOPES = ['https://www.googleapis.com/auth/documents']
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']
GMAIL_SCOPES = ['https://www.googleapis.com/auth/drive']
pp = pprint.PrettyPrinter(indent=4)


class Google(implements(ILetterSender), implements(IEmailSender)):
    def __init__(self, \

            # PROD
            parent_mailer_folder_id='197j8yOL5i_EBdjt_ObneXDXj6NtZsDXs',
            spreadsheet_id='13aEzvGkz1Sa0kflqcW52B_3caILUeB9eErk5vFlsmEc'):
            # TEST
            #parent_mailer_folder_id='15--fLcMPKG_Au0HIbo4Q30VCWzw9j0vl',
            #spreadsheet_id='10vKsgzKeakj7N06Oxufghq1_NNJ8HSye23NaTCSeURI'):

        self.sheet_creds = self.__load_creds('pickles/cfldv1_sheet_secret.pickle', '/home/tgaldes/Dropbox/Fraternity PM/dev_private/cfldv1_secret.json', SHEET_SCOPES)
        self.letter_creds = self.__load_creds('pickles/cfldv1_letter_secret.pickle', '/home/tgaldes/Dropbox/Fraternity PM/dev_private/docs_credentials.json', DOC_SCOPES)
        self.drive_creds = self.__load_creds('pickles/cfldv1_drive_secret.pickle', '/home/tgaldes/Dropbox/Fraternity PM/dev_private/drive_credentials.json', DRIVE_SCOPES)
        self.gmail_creds = self.__load_creds('pickles/cfldv1_gmail_secret.pickle', '/home/tgaldes/Dropbox/Fraternity PM/dev_private/cfldv1_secret.json', GMAIL_SCOPES)
        self.sheet_service = build('sheets', 'v4', credentials=self.sheet_creds)
        self.spreadsheet_id = spreadsheet_id
        self.spreadsheet = self.__get_spreadsheet(self.spreadsheet_id)
        self.parent_mailer_folder_id = parent_mailer_folder_id

        self.set_up_mailer = False

        # map name of sheet to data
        self.sheets_data, self.sheets = self.__get_sheets(self.spreadsheet, self.spreadsheet_id)

        # TODO: uncomment these
        self.letter_service = build('docs', 'v1', credentials=self.letter_creds)


        self.drive_service = build('drive', 'v3', credentials=self.drive_creds)

        self.gmail_service = build('drive', 'v3', credentials=self.gmail_creds)

        # one off functions for maniuplating data on the google sheet or outputting data we should fix manually
        #self.__strip_whitespace('houses', 'chapter_designation')
        #self.__get_bad_addresses()
        #self.__get_bad_names()
        #self.__get_bad_chapter_designations()
        #self.__separate_emails()
        #self.__move_multiline_email_addresses()

# Will create a sheet for all the addresses, and a folder for the letters on demand
    def __set_up_mailer(self):
        print('Setting up mailer')
        now_string = datetime.datetime.now().strftime('%Y%m%d %H:%M')
        self.folder_id = self.__create_folder(now_string)
        self.address_letter_sheet_id = self.__create_address_sheet(now_string)
        self.address_letter_sheet = self.__get_spreadsheet(self.address_letter_sheet_id)
        self.address_letter_row_num = 0
        self.address_letter_sheet_data, self.address_letter = self.__get_sheets(self.address_letter_sheet, self.address_letter_sheet_id)
        self.snail_mail_contacts_to_log = []

    def confirm_sending_mail(self):
        for data, mail_type in self.snail_mail_contacts_to_log:
            self.__log_contact(data, mail_type)

    def get_clean_data(self, sheet_name, ffill_columns):
        return dch.clean(self.sheets_data[sheet_name], ffill_columns)

    def get_header(self, sheet_name):
        return self.sheets_data[sheet_name][0]
    
    def get_last_date_for_contact(self, data, enum):
        sheet_data = self.sheets_data[sc.sheet_names['contacts']]
        return self.__get_last_mailed_date(data, enum, sheet_data, sc.columns_that_define_unique_contact)

    def get_last_date_for_house(self, data, enum):
        sheet_data = self.sheets_data[sc.sheet_names['houses']]
        return self.__get_last_mailed_date(data, enum, sheet_data, sc.columns_that_define_unique_house)

# update the cell at zero indexed location row i, col j
# TODO: append mode
    def update_cell(self, i, j, value, sheet_name):
        col_num = j + 1
        row_num = i + 1
        r = sc.range_builder[col_num] + str(row_num)
        range_name = '{}!{}'.format(sheet_name, r)

        values = [[value]]
        body = {
            'values' : values,
        }

        return self.__exponential_backoff('''self.sheet_service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=args[0], valueInputOption='RAW', body=args[1]).execute()''', range_name, body)

# one off functions --------------------------------------------------- 
    def create_qr_codes(self, output_dir, overwrite=False):
        # go through all the houses/contacts
        # if the qr month isn't populated, create a qr code pointing to the desired link and with the desired filename
        # save the code in the output_dir
        # update the qr month
        try:
            os.make_dirs(output_dir)
        except:
            pass
        raw_cmd = 'qrencode -o "{}/{}" "{}"'
        date_string = datetime.datetime.now().date().strftime('%Y%m')
        sheet_data = self.sheets_data[sc.sheet_names['houses']]
        for i, row in enumerate(sheet_data):
            if i == 0: continue
            if overwrite or not row[sc.house_data_header.index(sc.qr_date_column_name)]:
                cmd = raw_cmd.format(output_dir,
                        row[sc.house_data_header.index(sc.qr_file_name_column_name)],
                        row[sc.house_data_header.index(sc.unique_url_column_name)])
                rc = os.system(cmd)
                if rc != 0:
                    pdb.set_trace()
                    print('Error creating qr code with filename {}'.format(row[sc.house_data_header.index(sc.qr_file_name_column_name)]))
                    continue
                j = sheet_data[0].index(sc.qr_date_column_name)
                self.update_cell(i, j, date_string, sc.sheet_names['houses'])
# TODO: import the house/contact data named tuple instead of indexing into the header
# Contacts
        sheet_data = self.sheets_data[sc.sheet_names['contacts']]
        for i, row in enumerate(sheet_data):
            if i == 0: continue
            # at least address/email/links need to be populated
            if (overwrite or not row[sc.contact_data_header.index(sc.qr_date_column_name)]) \
                        and \
                        (row[sc.contact_data_header.index(sc.address_column_name)] or row[sc.contact_data_header.index(sc.email_column_name)] or row[sc.contact_data_header.index(sc.links_column_name)] or row[sc.contact_data_header.index(sc.name_column_name)]):
                cmd = raw_cmd.format(output_dir,
                        row[sc.contact_data_header.index(sc.qr_file_name_column_name)],
                        row[sc.contact_data_header.index(sc.unique_url_column_name)])
                rc = os.system(cmd)
                if rc != 0:
                    pdb.set_trace()
                    print('Error creating qr code with filename {}'.format(row[sc.contact_data_header.index(sc.qr_file_name_column_name)]))
                    continue
                j = sheet_data[0].index(sc.qr_date_column_name)
                self.update_cell(i, j, date_string, sc.sheet_names['contacts'])
# Houses



# Take a list of urls visited and add any new dates to the rows of the csv with the matching url
# visits is list of [(url, date)....]
    def update_page_visits(self, visits):
# TODO: the matching is similar to __log_contact, we can have a generic func that finds the matching row based on the info we have availble
        total_logged = 0
        for url, date in visits:
            # try to find a match in the contact data
            row_num = 1
# try to match a contact
            sheet_data = self.sheets_data[sc.sheet_names['contacts']]
            range_name = "addresses_clean!{}"
            for i, row in enumerate(sheet_data):
# only match when we look at the contact sheet, otherwise look at a match in houses # TODO: this is a kind of hacky way to figure out how we know if we're using a contact or a house
                if row \
                        and url in row[sc.contact_data_header.index('unique_url')]:
                        row_num += i
                        print('match for {} at row {} in contacts sheet'.format(url, i + 1))
                        break
            if row_num == 1:
                # try to find a match in the house data
                sheet_data = self.sheets_data[sc.sheet_names['houses']]
                range_name = "houses!{}"
                for i, row in enumerate(sheet_data):
                    if row \
                            and url in row[sc.house_data_header.index('unique_url')]:
                        row_num += i
                        print('match for {} at row {} in house sheet'.format(row[sc.contact_data_header.index('unique_url')], i + 1))
                        break

            if row_num == 1:
                print('No match for url {}'.format(url)) # There will be urls in the log that don't match anyone from my testing
                continue
# get column from constants
            col_num = 1 + sheet_data[0].index(sc.unique_url_visited_column_name)
            if col_num == 1:
                raise Exception('Column number of unique url visited on sheet is misconfigured, aborting.')
            r = sc.range_builder[col_num] + str(row_num)
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
# end one off functions --------------------------------------------------- 

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
        file = self.__exponential_backoff('''self.drive_service.files().create(body=args[0], fields='id', supportsAllDrives=True).execute()''', file_metadata)
        return file.get('id')

    def __get_last_mailed_date(self, data, enum, haystack, num_columns):
        header = haystack[0]
        if enum == MailType.EMAIL:
            col_name = sc.email_date_column_name
        elif enum == MailType.MAIL:
            col_name = sc.mail_date_column_name
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
            range_name='{}!A1:AM2500'.format(title) # TODO: maybe can hardcode the name of the last column we need in python per sheet, get the whole first row, and then get the column letter from that then re get the whole sheet to that column
            sheets[title] = self.__exponential_backoff('''self.sheet_service.spreadsheets().values().get(spreadsheetId=args[0], range=args[1]).execute()''', id_, range_name)
            m[title] = sheets[title].get('values', [])
        return m, sheets


#IEmailSender
    def send_email(self, subject, msg, contact_info):
        print('Implement sending email with msg: {}'.format(msg))
        #self.__log_contact(contact_info, MailType.EMAIL)
#ILetterSender
    def send_mail(self, address, msg, contact):
        if not self.set_up_mailer:
            self.__set_up_mailer()
            self.set_up_mailer = True
        doc = self.__create_doc(contact.data)
        if not self.__update_address_list(address, doc, contact.get_name()):
            return
        self.__append_to_letter_doc(msg, doc, contact.data)
        self.snail_mail_contacts_to_log.append((contact.data, MailType.MAIL))
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
        r = sc.range_builder[1] + str(self.address_letter_row_num) + ':' + sc.range_builder[5] + str(self.address_letter_row_num)
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
            #return False
            raise Exception('Address had too many lines: {}'.format(address_lines))
        else:
            print('ERROR: Address had only one line: {}'.format(address_lines))
            #return False
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
        #TODO: log error on qr code not found and use default
        text_reqs, format_reqs, full_msg_size = self.__create_text_inserts_to_doc(msg)
        requests = [
        {
            'insertInlineImage': 
            {
                'location': 
                {
                    'index': 1
                },
                #'uri': 'https://cleanfloorslockingdoors.com/wp-content/uploads/2020/09/default.png',#get_qr_code_url(contact_info), TODO
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
        sheet_data = self.sheets_data[sc.sheet_names['contacts']]
        range_name = "addresses_clean!{}"
        row_num = 1
# try to match a contact
        for i, row in enumerate(sheet_data):
# only match when we look at the contact sheet, otherwise look at a match in houses # TODO: this is a kind of hacky way to figure out how we know if we're using a contact or a house
            if row and 'name' in contact_info._fields \
                    and row[0] == contact_info.short_name \
                    and row[1] == contact_info.fraternity:
                if mail_type_enum == MailType.MAIL and row[sc.contact_data_header.index('address')] == contact_info.address:
                    row_num += i
                    print('match for {} at row {} in contacts sheet'.format(row[2], i + 1))
                    break
        if row_num == 1:
# try to match a house
            sheet_data = self.sheets_data[sc.sheet_names['houses']]
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
        col_num = 1 + sheet_data[0].index(sc.mail_type_enum_to_column_name[mail_type_enum])
        if col_num == 1:
            raise Exception('Column number of mail date tracking column on sheet is misconfigured, aborting.')
        r = sc.range_builder[col_num] + str(row_num)
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
        max_attempts = 6
        start_backoff = 2
        while True:
            attempts += 1
            try:
                exec(local_request)
                return locals()['local_result']
            except Exception as e:
                print(local_request)
                print(str(e))
                if attempts >= max_attempts:
                    break
                print('Received error from google, backing off {} seconds and retrying. ({}/{}) attempts made.'.format(start_backoff, attempts, max_attempts))
                sleep(start_backoff)
                start_backoff *= 2
        raise Exception('Reach max exponential backoff attempts ({}), raising exception'.format(attempts))
                
# -------------- One/two of test functions ----------------------- #
# output the row numbers of addresses that are only one line
    def __get_bad_addresses(self):
        sheet_data = self.sheets_data[sc.sheet_names['contacts']]
        address_col_num = sheet_data[0].index(sc.address_column_name)
        rows = []
        one_line = []
        city_rows = []
        four_or_more_lines = []
        for i, row in enumerate(sheet_data):
            if i == 0: continue # skip header
            if row and row[address_col_num] and row[address_col_num].count('\n') == 0:
                one_line.append(i + 1)
            if len(row[address_col_num].split('\n')) > 3:
                four_or_more_lines.append((i + 1, row[address_col_num]))
            elif row and ('address' in row[address_col_num].lower()
                    or 'state' in row[address_col_num].lower()
                    or 'zip' in row[address_col_num].lower()):
                rows.append(i + 1)
            elif row and 'city' in row[address_col_num].lower():
                city_rows.append(i + 1)
        print('The following rows have bad addresses :')
        for row in rows:
            print(row)
        print('The following rows contain "city" and might be good or might need to be fixed :')
        for row in city_rows:
            print(row)
        print('Now looking at house addresses')
        sheet_data = self.sheets_data[sc.sheet_names['houses']]
        address_col_num = sheet_data[0].index(sc.address_column_name)
        rows = []
        for i, row in enumerate(sheet_data):
            if i == 0: continue # skip header
            if row and row[address_col_num] and row[address_col_num].count('\n') == 0:
                one_line.append(i + 1)
            if len(row[address_col_num].split('\n')) > 3:
                four_or_more_lines.append((i + 1, row[address_col_num]))
            elif row and ('address' in row[address_col_num].lower()
                    or 'state' in row[address_col_num].lower()
                    or 'zip' in row[address_col_num].lower()):
                rows.append(i + 1)
            elif row and 'city' in row[address_col_num].lower():
                city_rows.append(i + 1)
        print('The following rows have bad addresses :')
        for row in rows:
            print(row)
        print('The following address have four or more lines:')
        for row in four_or_more_lines:
            print(row)
        print('The following rows have one line addresses :')
        for row in one_line:
            print(row)
    def __get_bad_names(self):
        sheet_data = self.sheets_data[sc.sheet_names['contacts']]
        name_col_num = sheet_data[0].index('name')
        rows = []
        for i, row in enumerate(sheet_data):
            if i == 0: continue # skip header
            if row and row[sc.contact_data_header.index(sc.code_column_name)] != 'agent_corp' and row[name_col_num] and ((len(row[name_col_num].split()) != 2 and len(row[name_col_num].split()) != 3) or ',' in row[name_col_num]):
                rows.append((i + 1, row[name_col_num]))
        print('The following names might be more than (first, last)')
        for row in rows:
            print(row)
        rows = []
        for i, row in enumerate(sheet_data):
            if i == 0: continue # skip header
            if row and row[name_col_num].strip() != row[name_col_num]:
                rows.append((i + 1, row[name_col_num]))
        print('The following names need whitespace at the start and end changed.')
        for row in rows:
            print(row)
    def __get_bad_chapter_designations(self):
        sheet_data = self.sheets_data[sc.sheet_names['houses']]
        name_col_num = sheet_data[0].index('chapter_designation')
        rows = []
        ok_names = ['XXX']
        for i, row in enumerate(sheet_data):
            if i == 0: continue # skip header
            if row and (row[name_col_num].title() != row[name_col_num] or len(row[name_col_num]) == 1 or 'chapter' in row[name_col_num].lower()) and row[name_col_num] not in ok_names:
                rows.append((i + 1, row[name_col_num]))
        print('The following chapter designations might need their capitalization fixed')
        for row in rows:
            print(row)

    def __strip_whitespace(self, sheet_name, col_name):
        sheet_data = self.sheets_data[sc.sheet_names[sheet_name]]
        raw_range='{}!'.format(sc.sheet_names[sheet_name]) + '{}'
        col_num = sheet_data[0].index(col_name)
        for i, row in enumerate(sheet_data):
            if row[col_num] and row[col_num].strip() != row[col_num]:
                print(row[col_num])
                row_num = i + 1
                r = sc.range_builder[col_num + 1] + str(row_num)
                range_name = raw_range.format(r)
                values = [[row[col_num].strip()]]
                body = { 'values' : values, }
                result = self.__exponential_backoff('''self.sheet_service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=args[0], valueInputOption='RAW', body=args[1]).execute()''', range_name, body)
        
                
    def __separate_emails(self):
        sheet_data = self.sheets_data[sc.sheet_names['contacts']]
        raw_range='{}!'.format(sc.sheet_names['contacts']) + '{}'
        email_col_num = sheet_data[0].index('email')
        for i, row in enumerate(sheet_data):
            if i == 0: continue # skip header
            email_string = row[email_col_num]
            if not email_string:
                continue
            elif email_string.split()[0] != email_string:
                print(email_string.split())
                row_num = i + 1
                r = sc.range_builder[email_col_num + 1] + str(row_num)
                if len(email_string.split()) > 1:
                    r += ':' + sc.range_builder[email_col_num + len(email_string.split())] + str(row_num)
                range_name = raw_range.format(r)
                values = [email_string.split()]
                body = { 'values' : values, }
                result = self.__exponential_backoff('''self.sheet_service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=args[0], valueInputOption='RAW', body=args[1]).execute()''', range_name, body)

    def __move_multiline_email_addresses(self):
        # we'll create an entirely new sheet that only has one email column
        new_sheet_data = []
        new_sheet_header = []
        email_column_prefix = 'email'
        sheet_data = self.sheets_data[sc.sheet_names['contacts']]
        header = sheet_data[0]
        for i, row in enumerate(sheet_data):
            if i == 0:
                added_email_header = False
                start_email_index = -1
                end_email_index = -1
                for j, val in enumerate(row):
                    if val[:len(email_column_prefix)] == email_column_prefix:
                        if start_email_index == -1:
                            start_email_index = j
                        end_email_index = j
                        if not added_email_header:
                            new_sheet_header.append(val)
                            added_email_header = True
                        else:
                            continue
                    else:
                        new_sheet_header.append(val)
                print('New header is: {}'.format(new_sheet_header))
                new_sheet_data.append(new_sheet_header)
                continue
            # populate all the non email values and leave the email blank for the moment
            new_base_row = row[:start_email_index] + [''] + row[end_email_index + 1:]
            added_row = False
            for email in row[start_email_index:end_email_index + 1]:
                if email != '':
                    new_base_row[start_email_index] = email
                    new_sheet_data.append(copy(new_base_row))
                    added_row = True
            # if we didn't have any email for this line, add one instance of it anyway
            if not added_row:
                    new_sheet_data.append(copy(new_base_row))
        for row in new_sheet_data:
            print(row)

        # hardcoded :(
        range_name = 'addresses_clean_new_data!A1:AH2642'
        body = { 'values' : new_sheet_data }
        result = self.__exponential_backoff('''self.sheet_service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=args[0], valueInputOption='RAW', body=args[1]).execute()''', range_name, body)






        

if __name__=='__main__':
    g = Google()
    #g.create_qr_codes('/tmp/qr_codes', False)
    '''with open('pickles/google.pickle', 'wb') as f:
        pickle.dump(g, f)
    with open('pickles/google.pickle', 'rb') as f:
        g2 = pickle.load(f)'''
