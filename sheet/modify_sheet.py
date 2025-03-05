from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv
import logging
import os
import webbrowser
load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleSheet:
    def __init__(self, purpose):
        self.__purpose = purpose
        self.__spreadsheet_id = None
        if purpose == 'motivation':
            self.__spreadsheet_id = os.getenv('MOTIVATION_SPREADSHEET_ID')
        elif purpose == 'core_experience':
            self.__spreadsheet_id = os.getenv('CORE_EXPERIENCE_SPREADSHEET_ID')
        elif purpose == 'cost':
            self.__spreadsheet_id = os.getenv('COST_SPREADSHEET_ID')
        else:
            raise ValueError(f"Invalid purpose: {purpose}")

        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        self.credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
    
    def go_to_sheet(self):
        self.url = f"https://docs.google.com/spreadsheets/d/{self.__spreadsheet_id}"
        webbrowser.open(self.url)

    def get_last_data(self, data_type):
        self.data_config = {}
        self.range_str = ''
        if self.__purpose == 'core_experience': 
            self.data_config = {
                # setting 시트
                'situation': {'sheet': 'setting', 'column': 'C:C'},
                'role': {'sheet': 'setting', 'column': 'B:B'},
                'knowledge': {'sheet': 'setting', 'column': 'D:D'},
                # info 시트
                'company': {'sheet': 'info', 'column': 'B:B'},
                'job': {'sheet': 'info', 'column': 'C:C'},
                'job_posting': {'sheet': 'info', 'column': 'D:D'},
                'core_experience': {'sheet': 'info', 'column': 'E:E'},
                'question': {'sheet': 'info', 'column': 'F:F'},
                # prompt_structure 시트
                'prompt_structure': {'sheet': 'prompt_structure', 'column': 'B:B'},
                # model_setting 시트
                'model': {'sheet': 'model_setting', 'column': 'B:B'},
                'temperature': {'sheet': 'model_setting', 'column': 'C:C'},
                'max_tokens': {'sheet': 'model_setting', 'column': 'D:D'},
                'thinking': {'sheet': 'model_setting', 'column': 'E:E'},
                'budget_tokens': {'sheet': 'model_setting', 'column': 'F:F'},
                # translation_model_setting 시트
                'translation_model': {'sheet': 'translation_model_setting', 'column': 'B:B'},
                'translation_temperature': {'sheet': 'translation_model_setting', 'column': 'C:C'}
            }
            if data_type not in self.data_config:
                raise ValueError(f"Invalid data type: {data_type}")
            config = self.data_config[data_type]
            self.range_str = f"{config['sheet']}!{config['column']}"
        elif self.__purpose == 'motivation':
            self.data_config = {
                # prompt_structure 시트
                'prompt_structure': {'sheet': 'prompt_structure', 'column': 'B:B'},
                # model_setting 시트
                'model': {'sheet': 'model_setting', 'column': 'B:B'},
                'temperature': {'sheet': 'model_setting', 'column': 'C:C'},
                'max_tokens': {'sheet': 'model_setting', 'column': 'D:D'},
                'thinking': {'sheet': 'model_setting', 'column': 'E:E'},
                'budget_tokens': {'sheet': 'model_setting', 'column': 'F:F'},
                # translation_model_setting 시트
                'translation_model': {'sheet': 'translation_model_setting', 'column': 'B:B'},
                'translation_temperature': {'sheet': 'translation_model_setting', 'column': 'C:C'},
                # setting 시트
                'situation': {'sheet': 'setting', 'column': 'C:C'},
                'role': {'sheet': 'setting', 'column': 'B:B'},
                'knowledge': {'sheet': 'setting', 'column': 'D:D'},
                # info 시트
                'company': {'sheet': 'info', 'column': 'B:B'},
                'job': {'sheet': 'info', 'column': 'C:C'},
                'job_posting': {'sheet': 'info', 'column': 'D:D'},
                'core_experience': {'sheet': 'info', 'column': 'E:E'},
                'question': {'sheet': 'info', 'column': 'F:F'},
                'issue': {'sheet': 'info', 'column': 'G:G'},
            }
            config = self.data_config[data_type]
            self.range_str = f"{config['sheet']}!{config['column']}"
            
        try:
            logger.info(f"Fetching data from spreadsheet: {self.__purpose}, range: {self.range_str}")
            
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.__spreadsheet_id,
                range=self.range_str
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.warning(f"No data found for range: {self.range_str}")
                return None
                
            non_empty_rows = [row[0] for row in values if row]
            if not non_empty_rows:
                return None
                
            last_value = non_empty_rows[-1]
            logger.info(f"Successfully fetched data: {last_value}")
            return last_value
            
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            raise

    def get_whole_data(self, sheet_name, range):
        """시트에서 특정 range의 모든 데이터를 가져오는 함수"""
        logger.debug(f"Fetching data from {sheet_name}: {range}")
        self.range_str = f"{sheet_name}!{range}"
        
        try:
            logger.info(f"Fetching data from spreadsheet ID: {self.__spreadsheet_id}, range: {self.range_str}")

            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.__spreadsheet_id,
                range=self.range_str
            ).execute()

            values = result.get('values', [])
            if not values:
                logger.warning(f"No data found for range: {self.range_str}")
                return None

            logger.info(f"Successfully fetched data: {values}")
            return values
        
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            raise

    def get_sheet_id(self, sheet_name):
        """스프레드시트 내의 특정 시트 ID를 가져오는 함수
        
        Args:
            sheet_name (str): 시트 이름
            
        Returns:
            int: 시트 ID
            
        Raises:
            ValueError: 시트를 찾을 수 없는 경우
        """
        logger.debug(f"Getting sheet ID for sheet: {sheet_name}")
        
        try:
            # 스프레드시트의 모든 시트 정보 가져오기
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=self.__spreadsheet_id
            ).execute()
            
            # 시트 이름으로 시트 ID 찾기
            sheets = spreadsheet.get('sheets', [])
            for sheet in sheets:
                properties = sheet.get('properties', {})
                if properties.get('title') == sheet_name:
                    sheet_id = properties.get('sheetId')
                    logger.info(f"Found sheet ID {sheet_id} for sheet: {sheet_name}")
                    return sheet_id
            
            # 시트를 찾지 못한 경우
            logger.error(f"Sheet not found: {sheet_name}")
            raise ValueError(f"Sheet not found: {sheet_name}")
            
        except Exception as e:
            logger.error(f"Error getting sheet ID: {str(e)}")
            raise

    def update_sheet(self, sheet_range, values):
        """구글 시트에 데이터를 업데이트하는 함수"""
        logger.debug(f"Updating sheet range: {sheet_range} with values: {values}")
        try:
            body = {'values': [values]}
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=self.__spreadsheet_id,
                range=sheet_range,
                valueInputOption='RAW',
                body=body
            ).execute()
            logger.info(f"Successfully updated sheet range: {sheet_range}")
        except Exception as e:
            logger.error(f"Error updating sheet: {str(e)}")
            raise

    def insert_row(self, sheet_name, row_index):
        """시트에 새로운 행을 삽입하는 함수
        
        Args:
            sheet_name (str): 행을 삽입할 시트 이름
            row_index (int): 삽입할 행의 인덱스 (1부터 시작)
        """
        logger.debug(f"Inserting new row at sheet: {sheet_name}, row: {row_index}")
        self.row_index = row_index - 1  # 0-based index로 변환
        
        try:
            # 시트 ID 가져오기
            sheet_id = self.get_sheet_id(sheet_name)
            
            request = {
                "requests": [
                    {
                        "insertDimension": {
                            "range": {
                                "sheetId": sheet_id,  # 동적으로 가져온 sheetId 사용
                                "dimension": "ROWS",
                                "startIndex": self.row_index,
                                "endIndex": self.row_index + 1
                            }
                        }
                    }
                ]
            }

            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=self.__spreadsheet_id,
                body=request
            ).execute()

            logger.info(f"Successfully inserted new row in sheet: {sheet_name} at row: {row_index}")
        except Exception as e:
            logger.error(f"Error inserting row: {str(e)}")
            raise
    
    def get_second_row_index(self, sheet_name):
        """시트의 두 번째 행(제목 행 제외)의 인덱스를 가져오는 함수"""
        logger.debug(f"Getting second row index for sheet: {sheet_name}")
        self.range_str = f"{sheet_name}!A:A"
        try:
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.__spreadsheet_id,
                range=self.range_str
            ).execute()
            values = result.get('values', [])
            logger.info(f"Values: {values}")
            if not values:
                logger.warning(f"No data found for range: {self.range_str}")
                return None
            prev_index_list = values[2]
            logger.info(f"Prev index list: {prev_index_list}")
            if not prev_index_list:
                logger.warning(f"No data found in previous row index for range: {self.range_str}")
                return None
            prev_index = prev_index_list[0]
            logger.info(f"Successfully got previous row index: {prev_index}")
            return prev_index
        except Exception as e:
            logger.error(f"Error getting previous row index: {str(e)}")
            raise

    def update_index(self, sheet_name, row_index):
        """시트 행의 index 열에 새로운 index 값을 넣는 함수"""
        logger.debug(f"Updating index in row {row_index}")
        try:
            prev_index = self.get_second_row_index(sheet_name)
            # prev_index를 정수로 변환
            prev_index = int(prev_index)
            new_index = prev_index + 1
            self.update_sheet(f'{sheet_name}!A{row_index}', [new_index])
            logger.info(f"Successfully updated index to: {new_index}")
        except Exception as e:
            logger.error(f"Error updating index: {str(e)}")
            raise

    def update_evaluation_sheet(self, data):
        """evaluation 시트에 데이터를 업데이트하는 함수"""
        self.update_sheet('evaluation!D2', [data['thinking']])
        self.update_sheet('evaluation!E2', [data['result']])
        self.update_sheet('evaluation!G2', [data['model_name']])
        self.update_sheet('evaluation!H2', [data['temperature']])
        self.update_sheet('evaluation!I2', [data['translation_model_name']])
        self.update_sheet('evaluation!J2', [data['translation_temperature']])
        self.update_sheet('evaluation!K2', [data['cost']])
        self.update_sheet('evaluation!L2', [data['krw_cost']])
        self.update_sheet('evaluation!M2', [data['prompt_tokens']])
        self.update_sheet('evaluation!N2', [data['completion_tokens']])
        self.update_sheet('evaluation!O2', [data['total_tokens']])
        self.update_sheet('evaluation!P2', [data['translation_prompt_tokens']])
        self.update_sheet('evaluation!Q2', [data['translation_completion_tokens']])
        self.update_sheet('evaluation!R2', [data['translation_total_tokens']])
        self.update_sheet('evaluation!S2', [data['total_tokens'] + data['translation_total_tokens']])

