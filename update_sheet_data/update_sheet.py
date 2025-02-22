import os
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=credentials)

from get_sheet_data.get_data import get_last_index
from get_sheet_data.get_data import get_sheet_id

evaluation_sheet_id = get_sheet_id('evaluation')

def update_sheet(sheet_range, values):
    """구글 시트에 데이터를 업데이트하는 함수"""
    logger.debug(f"Updating sheet range: {sheet_range} with values: {values}")
    try:
        body = {'values': [values]}
        sheets_service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=sheet_range,
            valueInputOption='RAW',
            body=body
        ).execute()
        logger.info(f"Successfully updated sheet range: {sheet_range}")
    except Exception as e:
        logger.error(f"Error updating sheet: {str(e)}")
        raise

def insert_row():
    """evaluation 시트의 2번째 행에 새로운 행을 삽입하는 함수"""
    logger.debug("Inserting new row at row 2 in evaluation sheet")
    try:
        request = {
            "requests": [
                {
                    "insertDimension": {
                        "range": {
                            "sheetId": evaluation_sheet_id,  # 동적으로 가져온 sheetId 사용
                            "dimension": "ROWS",
                            "startIndex": 1,  # 0-based index, 2번째 행
                            "endIndex": 2
                        }
                    }
                }
            ]
        }

        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=request
        ).execute()

        logger.info("Successfully inserted new row")
    except Exception as e:
        logger.error(f"Error inserting row: {str(e)}")
        raise

def update_index():
    """evaluation 시트의 2행의 index 열에 새로운 index 값을 넣는 함수"""
    logger.debug("Updating index in row 2")
    try:
        last_index = get_last_index()
        new_index = last_index + 1
        update_sheet('evaluation!A2', [new_index])
        logger.info(f"Successfully updated index to: {new_index}")
    except Exception as e:
        logger.error(f"Error updating index: {str(e)}")
        raise

def update_evaluation_sheet(data):
    """evaluation 시트의 2행의 값을 업데이트하는 함수"""
    update_sheet('evaluation!D2', [data['result']])
    update_sheet('evaluation!F2', [data['model_name']])
    update_sheet('evaluation!G2', [data['temperature']])
    update_sheet('evaluation!H2', [data['translation_model_name']])
    update_sheet('evaluation!I2', [data['translation_temperature']])
    update_sheet('evaluation!J2', [data['cost']])
    update_sheet('evaluation!K2', [data['prompt_tokens']])
    update_sheet('evaluation!L2', [data['completion_tokens']])
    update_sheet('evaluation!M2', [data['total_tokens']])
    update_sheet('evaluation!N2', [data['translation_prompt_tokens']])
    update_sheet('evaluation!O2', [data['translation_completion_tokens']])
    update_sheet('evaluation!P2', [data['translation_total_tokens']])
    total_tokens = data['total_tokens'] + data['translation_total_tokens']
    update_sheet('evaluation!Q2', [total_tokens])
    