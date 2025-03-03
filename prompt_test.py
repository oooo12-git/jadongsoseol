# Google Sheets API 및 OpenAI API 필요한 라이브러리 import
import logging
import os
from dotenv import load_dotenv
from get_sheet_data.get_data import get_last_data
from update_sheet_data.update_sheet import update_sheet, insert_row, update_index, update_evaluation_sheet
from use_llm.generate import generate_cover_letter, translate_to_english
from calculation_cost.cost import calculation_cost, usd_to_krw

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

situation = get_last_data('situation')
company = get_last_data('company')
job = get_last_data('job')
situation = situation.format(company=company, job=job)
prompt_structure = get_last_data('prompt_structure')
role = get_last_data('role')
question = get_last_data('question')
knowledge = get_last_data('knowledge')
core_experience = get_last_data('core_experience')
job_posting = get_last_data('job_posting')
formatted_prompt = prompt_structure.format(role=role, situation=situation, job_posting=job_posting, question=question, core_experience=core_experience, knowledge=knowledge)

# 2번째 행에 새로운 행 삽입
insert_row()

# 새로운 index 값 업데이트
update_index()

# 구글 시트에 prompt 저장
update_sheet('evaluation!B2', [formatted_prompt])

# prompt를 영어로 번역
translation_model = get_last_data('translation_model')
translation_temperature = get_last_data('translation_temperature')
prompt_english, translation_prompt_tokens, translation_completion_tokens, translation_total_tokens, translation_model_name = translate_to_english(formatted_prompt, model=translation_model,temperature=translation_temperature)

# 번역된 prompt를 구글 시트에 저장
update_sheet('evaluation!C2', [prompt_english])

# 자기소개서 작성
temperature = get_last_data('temperature')
model = get_last_data('model')
max_tokens = get_last_data('max_tokens')
result, completion_tokens, prompt_tokens, total_tokens, model_name = generate_cover_letter(prompt_english,model=model,temperature=temperature,max_tokens=max_tokens)

cost = calculation_cost(model_name, translation_model_name, prompt_tokens, completion_tokens, translation_prompt_tokens, translation_completion_tokens)
krw_cost = usd_to_krw(cost)

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
        'translation_total_tokens': translation_total_tokens,
        'cost': cost,
        'krw_cost': krw_cost}

update_evaluation_sheet(data)

logger.info("Successfully updated sheet")