# Google Sheets API 및 OpenAI API 필요한 라이브러리 import
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv
import logging
from get_sheet_data.get_data import get_data
from update_sheet_data.update_sheet import update_sheet, insert_row, update_index, update_evaluation_sheet
from use_llm.generate import generate_cover_letter, translate_to_english

load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

situation = get_data('situation')
company = get_data('company')
job = get_data('job')
situation = situation.format(company=company, job=job)
prompt_structure = get_data('prompt_structure')
role = get_data('role')
question = get_data('question')
knowledge = get_data('knowledge')
core_experience = get_data('core_experience')
job_posting = get_data('job_posting')
formatted_prompt = prompt_structure.format(role=role, situation=situation, job_posting=job_posting, question=question, core_experience=core_experience, knowledge=knowledge)

# 2번째 행에 새로운 행 삽입
insert_row()

# 새로운 index 값 업데이트
update_index()

# 구글 시트에 prompt 저장
update_sheet('evaluation!B2', [formatted_prompt])

# prompt를 영어로 번역
translation_model = get_data('translation_model')
translation_temperature = get_data('translation_temperature')
prompt_english, translation_prompt_tokens, translation_completion_tokens, translation_total_tokens, translation_model_name = translate_to_english(formatted_prompt, model=translation_model,temperature=translation_temperature)

# 번역된 prompt를 구글 시트에 저장
update_sheet('evaluation!C2', [prompt_english])

# 자기소개서 작성
temperature = get_data('temperature')
model = get_data('model')
result, completion_tokens, prompt_tokens, total_tokens, model_name = generate_cover_letter(prompt_english,model=model,temperature=temperature)
data = {'result': result, 
        'model_name': model_name, 
        'temperature': temperature,
        'translation_model_name': translation_model_name,
        'translation_temperature': translation_temperature,
        'prompt_tokens': prompt_tokens, 
        'completion_tokens': completion_tokens, 
        'total_tokens': total_tokens,
        'translation_prompt_tokens': translation_prompt_tokens,
        'translation_completion_tokens': translation_completion_tokens,
        'translation_total_tokens': translation_total_tokens}
# 작성된 자기소개서를 구글 시트에 저장
update_evaluation_sheet(data)

logger.info("Successfully updated sheet")
