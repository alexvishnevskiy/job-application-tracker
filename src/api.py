import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm
from email import message_from_bytes
from base64 import urlsafe_b64decode
from bs4 import BeautifulSoup
from logger import log
import re
from typing import List, Tuple
from datetime import datetime, timedelta

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


# function to preprocess text
def _preprocess(text):
    http_pattern = r'https?:\/\/(?:[-\w]+\.)+[-\w]+(?:\/[-\w\d%_.~+]*)*\s*'
    http_pattern1 = r'http\S+|:\s*\S+'
    white_space_pattern = r'\s+'
    dash_pattern = r'\-|\_+'
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F1E0-\U0001F1FF"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)

    text = re.sub(http_pattern, '', text)
    text = re.sub(http_pattern1, '', text)
    text = re.sub(white_space_pattern, ' ', text)
    text = re.sub(dash_pattern, '', text)
    text = emoji_pattern.sub(r'', text)
    text = text.replace('\u200b', '').replace('\u200c', '')
    text = re.sub('\.{2,}', '', text)
    return text


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

    #TODO: mark as read mail after read
    @log
    def read_mails(self, unread=True, date_range: Tuple[str, str] = None):
        query = 'in:inbox'
        if unread:
            query += ' is:unread'

        format_string = "%Y/%m/%d"
        if date_range is not None:
            start_date, end_date = date_range
            try:
                start_time = datetime.strptime(start_date, format_string)
                end_time = datetime.strptime(end_date, format_string)
            except ValueError as error:
                raise error
        else:
            # 6-month interval
            end_time = datetime.today().date()
            start_time = (end_time - timedelta(days=30*6))

            start_date = start_time.strftime(format_string)
            end_date = end_time.strftime(format_string)

        query += f' after:{start_date} before:{end_date}'

        # retrieve the list of emails matching the query
        try:
            result = []
            messages = []

            # gmail api can only retrieve 500 mails maximum
            while end_time > start_time:
                response = self.service.users().messages().list(userId='me', q=query, maxResults=500).execute()
                if response['resultSizeEstimate'] == 0:
                    break
                messages += response['messages']

                message = self.service.users() \
                    .messages().get(userId='me', id=response['messages'][-1]['id'], format='raw').execute()
                msg_str = urlsafe_b64decode(message['raw'].encode('ASCII')).decode('utf-8')
                email_message = message_from_bytes(msg_str.encode('utf-8'))

                end_time_format = '%a, %d %b %Y %H:%M:%S %z'
                if email_message['Date'].find('(UTC)') != -1:
                    end_time_format += ' (%Z)'

                end_time = datetime.strptime(email_message['Date'], end_time_format) \
                    .replace(tzinfo=None)
                end_date = end_time.strftime('%Y/%m/%d')
                query = f' after:{start_date} before:{end_date}'

            # iterate through each email message and print the snippet
            for message in tqdm(messages):
                mail_info = {}
                # TODO: make asynchronous calls
                msg = self.service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                payload = msg['payload']
                headers = payload['headers']

                data = ''
                if 'parts' in payload:
                    parts = payload['parts']
                    for part in parts:
                        if part['body'].get('data'):
                            data += part['body']['data']

                    soup = BeautifulSoup(urlsafe_b64decode(data).decode(), 'html.parser')
                    data = soup.get_text()

                mail_info['text'] = data or msg['snippet']
                mail_info['text'] = _preprocess(mail_info['text'])
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

    @log
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
            raise error

    @log
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
            raise error

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
            raise error


# api = SheetsAPI(spreadsheet_id="1W0cESqOEZAV7cpIXYuh0kGouxWiL0zg1nfmHzTHnwlk")
# api = GmailAPI()
# print(api.read_mails(date_range=("2023/03/12", "2023/03/13")))