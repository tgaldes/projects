import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/contacts"]
# a class to hold information about a contact group
class ContactGroup:
    def __init__(self, group_name, token_path='/home/tgaldes/Dropbox/Fraternity PM/dev_private/cfldv1_people_api_token.json', creds_path='/home/tgaldes/Dropbox/Fraternity PM/dev_private/cfldv1_people_credentials.json'):
        self.group_name = group_name
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                        creds_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, "w") as token:
                token.write(creds.to_json())

        self.service = build("people", "v1", credentials=creds)
        results = (
                self.service.contactGroups()
                .list(pageSize=100)
                .execute()
        )
        groups = results.get("contactGroups", [])
        for group in groups:
            if group["name"] == self.group_name:
                self.group = group
                break

        # get the group id
        # get the people in the group
        results = (
                self.service.people()
                .connections()
                .list(
                    resourceName="people/me",
                    pageSize=2000,
                    personFields="emailAddresses,memberships"
                    )
                .execute())
        members = results.get("connections", [])
        group_resource_name = self.group["resourceName"]
        self.people = []
        for member in members:
            memberships = member.get("memberships", [])
            if memberships:
                for membership in memberships:
                    if "domainMembership" in membership:
                        continue
                    # people's memberships are mapped to groups via the membership's contactGroupResourceName and the groups resourceName
                    if membership["contactGroupMembership"]["contactGroupResourceName"] == group_resource_name:
                        self.people.append(member)
        # populate a set of the emails of the people in the group
        self.emails = set()
        for person in self.people:
            email_addresses = person.get("emailAddresses", [])
            if email_addresses:
                for email_address in email_addresses:
                    self.emails.add(email_address["value"].lower())

    def has_email(self, email):
        return email.lower() in self.emails

