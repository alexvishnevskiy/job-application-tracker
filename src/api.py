import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Tuple
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/gmail.readonly']


def _build_services():
    creds = None
    if os.path.exists('../token.json'):
        creds = Credentials.from_authorized_user_file('../token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('../token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


class GmailAPI:
    def __init__(self):
        self.service = self._build()

    def _build(self):
        try:
            creds = _build_services()
            service = build('gmail', 'v1', credentials=creds)
            return service
        except HttpError as error:
            raise error

    def read_mails(self, unread=True, date_range: Tuple[str, str] = None):
        query = 'in:inbox'
        if unread:
            query += ' is:unread'

        if date_range is not None:
            start_date, end_date = date_range
            format_string = "%Y/%m/%d"
            try:
                datetime.strptime(start_date, format_string)
                datetime.strptime(end_date, format_string)
            except ValueError as error:
                raise error

            query += f' after:{start_date} before:{end_date}'

        # retrieve the list of emails matching the query
        try:
            result = []
            response = self.service.users().messages().list(userId='me', q=query).execute()
            messages = response['messages']

            # iterate through each email message and print the snippet
            for message in messages:
                mail_info = {}
                msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                payload = msg['payload']
                headers = payload['headers']

                mail_info['text'] = msg['snippet']
                for header in headers:
                    if header['name'] == 'From':
                        sender_email = header['value']
                        mail_info['mail'] = sender_email
                    if header['name'] == 'Subject':
                        subject = header['value']
                        mail_info['subject'] = subject
                result.append(mail_info)
            return result
        except HttpError as error:
            raise error


class SheetsAPI:
    def __init__(self, spreadsheet_name='job-applications', spreadsheet_id=None):
        self.__spreadsheet_name = spreadsheet_name
        self.__spreadsheet_id = spreadsheet_id
        self.service = self._build()

    def get_name(self):
        return self.__spreadsheet_name

    def get_id(self):
        return self.__spreadsheet_id

    def append_values(self, range_name: str, values: List[List[str]]):
        try:
            body = {
                'values': values
            }
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.__spreadsheet_id, range=range_name,
                insertDataOption="INSERT_ROWS", valueInputOption="USER_ENTERED",
                body=body).execute()
            return result
        except HttpError as error:
            return error

    def update_values(self, range_name: str, values: List[List[str]]):
        try:
            body = {
                'values': values
            }
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.__spreadsheet_id, range=range_name,
                valueInputOption="USER_ENTERED", body=body).execute()
            return result
        except HttpError as error:
            return error

    def find(self, company_name):
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.__spreadsheet_id,
            range="A1:B10000"
        ).execute()
        result = result.get('values', [])

        for i, (name, _) in enumerate(result, 1):
            if name == company_name:
                return f"A{i}:B{i}"
        return -1

    def _build(self):
        try:
            creds = _build_services()
            service = build('sheets', 'v4', credentials=creds)
            if self.__spreadsheet_id is None:
                spreadsheet = {
                    'properties': {
                        'title': self.__spreadsheet_name
                    }
                }
                spreadsheet = service.spreadsheets() \
                    .create(body=spreadsheet, fields='spreadsheetId') \
                    .execute()
                self.__spreadsheet_id = spreadsheet.get('spreadsheetId')

            self.service = service
            # insert columns names
            self.update_values("A1:B1", [["Company", "Status"]])
            return service
        except HttpError as error:
            return error


# api = SheetsAPI(spreadsheet_id="1W0cESqOEZAV7cpIXYuh0kGouxWiL0zg1nfmHzTHnwlk")
# api = GmailAPI()
# print(api.read_mails(date_range=("2023/03/10", "2023/03/11")))