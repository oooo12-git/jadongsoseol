import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from get_sheet_data.get_data import get_whole_data, get_token_price
from update_sheet_data.update_sheet import update_evaluation_sheet
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def calculation_cost(model_name, translation_model_name, prompt_tokens, completion_tokens, translation_prompt_tokens, translation_completion_tokens):
    logger.debug("Starting cost calculation")

    input_token_price, translation_input_token_price, output_token_price, translation_output_token_price = get_token_price(model_name, translation_model_name)

    prompt_cost = (prompt_tokens * float(input_token_price))
    completion_cost = (completion_tokens * float(output_token_price))
    translation_prompt_cost = (translation_prompt_tokens * float(translation_input_token_price))
    translation_completion_cost = (translation_completion_tokens * float(translation_output_token_price))
    
    total_cost = prompt_cost + completion_cost + translation_prompt_cost + translation_completion_cost
    
    return total_cost