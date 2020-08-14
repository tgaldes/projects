from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pdb

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents']

# The ID of a sample document.
#DOCUMENT_ID = '1pHxpyICZrnwbNxyg8jBW_hXppQgqQNOVXnqWIdiucjU'
DOCUMENT_ID = '1BuRTdSA6zVNiyw4NcPWV0pKdTeU6HlfIPumhM8IRAGE'

def main():
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file( \
                #'/home/tgaldes/Dropbox/Fraternity PM/dev_private/docs_credentials.json', SCOPES)
'/home/tgaldes/Dropbox/Fraternity PM/dev_private/cfldv1_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('docs', 'v1', credentials=creds)
    title = 'USC Kappa Alpha George Bremer'
    body = {
            'title': title
    }
    doc = service.documents() \
    .create(body=body).execute()
    print('Created document with title: {0}'.format(
        doc.get('documentId')))
    print(doc)
    # Retrieve the documents contents from the Docs service.
    document = service.documents().get(documentId=DOCUMENT_ID).execute()
    print(document)
    print(document['body']['content'][-1])

    print('The title of the document is: {}'.format(document.get('title')))
    smarket = 'BULLETS'
    emarker = 'ENDBULLETS'
    fs = '\tThis is the first paragraph.\n'
    ss = '\n\tThis is the second paragraph.\n'
    #+ smarker + 'test first line\ntest second\ntest third' + emarker
    bullets = 'test first line\ntest second\ntest third\n'
    '''{
        'insertInlineImage': {
            'location': {
                'index': 1
            },
            'uri':
                'https://cleanfloorslockingdoors.com/wp-content/uploads/2020/07/frame.png',
            'objectSize': {
                'height': {
                    'magnitude': 100,
                    'unit': 'PT'
                },
                'width': {
                    'magnitude': 100,
                    'unit': 'PT'
                }
            }
        }
    }, '''
    requests = [
        {
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': ss
            }
        }, \
        {
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': bullets
            }
        }, \
        {
            'insertText': {
                'location': {
                    'index': 1,
                },
                'text': fs
            }
        }, \
        {
            'createParagraphBullets': {
                'range': {
                    'startIndex': len(fs) + 1,
                    'endIndex':  len(bullets) + 1 + len(fs)
                },
                'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE',
            }
        }

    ]
    result = service.documents().batchUpdate(
            documentId=DOCUMENT_ID, body={'requests': requests}).execute()


if __name__ == '__main__':
    main()
