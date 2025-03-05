from sheet.modify_sheet import GoogleSheet
from use_llm.generate import generate_cover_letter, translate_to_english
from calculation_cost.cost import calculation_cost, usd_to_krw


sheet = GoogleSheet('core_experience')
# sheet.go_to_sheet()

situation = sheet.get_last_data('situation')
company = sheet.get_last_data('company')
job = sheet.get_last_data('job')
situation = situation.format(company=company, job=job)
prompt_structure = sheet.get_last_data('prompt_structure')
role = sheet.get_last_data('role')
question = sheet.get_last_data('question')
knowledge = sheet.get_last_data('knowledge')
core_experience = sheet.get_last_data('core_experience')
job_posting = sheet.get_last_data('job_posting')
# issue = sheet.get_last_data('issue')
formatted_prompt = prompt_structure.format(role=role, situation=situation, job_posting=job_posting, question=question, core_experience=core_experience, knowledge=knowledge)

sheet.insert_row('evaluation', 2)
sheet.update_index('evaluation', 2)
sheet.update_sheet('evaluation!B2', [formatted_prompt])

translation_model = sheet.get_last_data('translation_model')
translation_temperature = sheet.get_last_data('translation_temperature')
prompt_english, translation_prompt_tokens, translation_completion_tokens, translation_total_tokens, translation_model_name = translate_to_english(formatted_prompt, model=translation_model,temperature=translation_temperature)

sheet.update_sheet('evaluation!C2', [prompt_english])

model = sheet.get_last_data('model')
temperature = sheet.get_last_data('temperature')
max_tokens = sheet.get_last_data('max_tokens')
thinking = sheet.get_last_data('thinking')
budget_tokens = sheet.get_last_data('budget_tokens')
result, thinking_result, completion_tokens, prompt_tokens, total_tokens, model_name = generate_cover_letter(prompt_english,model=model,temperature=temperature,max_tokens=max_tokens, thinking=thinking, budget_tokens=budget_tokens)

cost = calculation_cost(model_name, translation_model_name, prompt_tokens, completion_tokens, translation_prompt_tokens, translation_completion_tokens)
krw_cost = usd_to_krw(cost)

data = {'result': result, 
        'thinking': thinking_result,
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

sheet.update_evaluation_sheet(data)