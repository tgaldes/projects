from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import collections

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1sQZiAi--Gj3V0O9oYfMsz78EJUHeDjjve2A5AsWDB-Y'
SAMPLE_RANGE_NAME = 'houses!A1:F'
def sheet():
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

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    return service.spreadsheets()

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
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

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        fields = values[0]
        HouseData = collections.namedtuple('HouseData', values[0])
        tups = []
        for row in values[:10]:
            tups.append(HouseData(*row))
        for tup in tups:
            for field in fields:
                print('{}: {}'.format(field, getattr(tup, field)))
        

if __name__ == '__main__':
    main()
