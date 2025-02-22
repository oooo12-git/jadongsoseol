from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv
import logging
import os

load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=credentials)

def get_data(data_type):
    """시트에서 특정 타입의 데이터를 가져오는 통합 함수"""
    logger.debug(f"Fetching data for type: {data_type}")
    
    # 데이터 타입별 시트와 열 정보 매핑
    data_config = {
        'situation': {'sheet': 'setting', 'column': 'C:C'},
        'role': {'sheet': 'setting', 'column': 'B:B'},
        'knowledge': {'sheet': 'setting', 'column': 'D:D'},
        'company': {'sheet': 'info', 'column': 'B:B'},
        'job': {'sheet': 'info', 'column': 'C:C'},
        'job_posting': {'sheet': 'info', 'column': 'D:D'},
        'core_experience': {'sheet': 'info', 'column': 'E:E'},
        'question': {'sheet': 'info', 'column': 'F:F'},
        'prompt_structure': {'sheet': 'prompt_structure', 'column': 'B:B'},
        'model': {'sheet': 'model_setting', 'column': 'B:B'},
        'temperature': {'sheet': 'model_setting', 'column': 'C:C'},
        'translation_model': {'sheet': 'translation_model_setting', 'column': 'B:B'},
        'translation_temperature': {'sheet': 'translation_model_setting', 'column': 'C:C'}
    }
    
    try:
        logger.info(f"Data config: {data_config[data_type]}")
        if data_type not in data_config:
            raise ValueError(f"Invalid data type: {data_type}")
            
        config = data_config[data_type]
        range_str = f"{config['sheet']}!{config['column']}"
        logger.info(f"Fetching data from range: {range_str}")
        
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_str
        ).execute()
        
        values = result.get('values', [])
        if not values:
            logger.warning(f"No data found for {data_type}")
            return None
            
        # 나머지 타입들은 마지막 비어있지 않은 값 반환
        non_empty_rows = [row[0] for row in values if row]
        if not non_empty_rows:
            return None
            
        last_value = non_empty_rows[-1]
        logger.info(f"Successfully fetched {data_type}: {last_value}")
        return last_value
        
    except Exception as e:
        logger.error(f"Error fetching {data_type}: {str(e)}")
        raise

def get_sheet_id(sheet_name):
    """시트 이름으로 sheetId를 가져오는 함수"""
    logger.debug(f"Fetching sheet ID for sheet: {sheet_name}")
    try:
        # 스프레드시트의 메타데이터를 가져옴
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID
        ).execute()

        # 시트 이름으로 sheetId 찾기
        for sheet in spreadsheet['sheets']:
            if sheet['properties']['title'] == sheet_name:
                sheet_id = sheet['properties']['sheetId']
                logger.info(f"Found sheet ID: {sheet_id} for sheet: {sheet_name}")
                return sheet_id

        logger.warning(f"No sheet found with name: {sheet_name}")
        return None

    except Exception as e:
        logger.error(f"Error fetching sheet ID: {str(e)}")
        raise

# evaluation 시트의 sheetId 가져오기
evaluation_sheet_id = get_sheet_id('evaluation')
print(f"Evaluation Sheet ID: {evaluation_sheet_id}")

# prompt_structure 시트의 sheetId 가져오기
prompt_structure_sheet_id = get_sheet_id('prompt_structure')
print(f"Prompt Structure Sheet ID: {prompt_structure_sheet_id}")

def get_last_index():
    """evaluation 시트의 3행의 index 값을 가져오는 함수"""
    logger.debug("Fetching index from row 3")
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='evaluation!A3'
        ).execute()

        values = result.get('values', [])
        if not values:
            logger.warning("No index found in row 3")
            return 0

        last_index = int(values[0][0])
        logger.info(f"Successfully fetched last index: {last_index}")
        return last_index

    except Exception as e:
        logger.error(f"Error fetching last index: {str(e)}")
        raise
