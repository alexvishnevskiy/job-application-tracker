import argparse
from api import GmailAPI, ChatGPT, SheetsAPI
from logger import log, logger
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key
import os

load_dotenv()
gpt_api = ChatGPT(os.getenv('OPENAI_API_KEY'))
gmail_api = GmailAPI()
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# as we are using crontab job, we need to save it somewhere
if os.getenv('spreadsheet_id') is None:
    sheets_api = SheetsAPI('job-applications')
    os.putenv('spreadsheet_id', sheets_api.get_id())
    set_key(os.path.join(parent_path, '.env'), 'spreadsheet_id', sheets_api.get_id())
else:
    spreadsheet_id = os.getenv('spreadsheet_id')
    sheets_api = SheetsAPI('job-applications', spreadsheet_id)


@log
def update(unread, start_date, end_date):
    mails = gmail_api.read_mails(unread, (start_date, end_date))
    answers = gpt_api.answer(mails)
    for answer in answers:
        if isinstance(answer, dict) and len(answer.keys()) == 2:
            company, status = answer.keys()
            to_insert = [[answer[company], answer[status]]]
            fields = sheets_api.find(answer[company])

            if fields != -1:
                sheets_api.update_values(fields, to_insert)
            else:
                sheets_api.append_values("A1:B1", to_insert)


@log
def main(unread, start_date, end_date):
    format_str = "%Y/%m/%d"
    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)
    today = today.strftime(format_str)
    tomorrow = tomorrow.strftime(format_str)

    if os.getenv('INIT_API') is None:
        os.putenv('INIT_API', '1')
        set_key(os.path.join(parent_path, '.env'), 'INIT_API', '1')
        logger.info("Fetching for the first time")
        update(unread, start_date, end_date)
    else:
        logger.info("Updating information every day")
        update(False, today, tomorrow)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A program that updates the current status of job application')
    parser.add_argument('start_date', nargs='?', default='2023/03/20', help='from where to start scrapping, format %Y/%m/%d')
    parser.add_argument('end_date', nargs='?', default='2023/03/29', help='until what time to end scrapping, %Y/%m/%d')
    parser.add_argument('--unread', action="store_true", help='whether to read unread mails or not')
    args = parser.parse_args()

    main(args.unread, args.start_date, args.end_date)
