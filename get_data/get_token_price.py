import logging
from sheet.modify_sheet import GoogleSheet


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_token_price(model_name, translation_model_name):
    cost_sheet = GoogleSheet('cost')
    cost_model_data = cost_sheet.get_whole_data('cost', 'B:B')
    model_index = 0
    translation_model_index = 0
    
    logger.debug(f"모델 이름: {model_name}, 번역 모델 이름: {translation_model_name}")
    logger.debug(f"가져온 모델 데이터 길이: {len(cost_model_data)}")
    
    model_found = False
    for i in range(len(cost_model_data)):
        if cost_model_data[i][0] == model_name:
            model_index = i
            model_found = True
            logger.debug(f"모델 '{model_name}' 찾음: 인덱스 {i}")
            break
    
    if not model_found:
        logger.warning(f"모델 '{model_name}'을(를) 데이터에서 찾을 수 없습니다. 기본 인덱스 0을 사용합니다.")
    
    translation_model_found = False
    for i in range(len(cost_model_data)):
        if cost_model_data[i][0] == translation_model_name:
            translation_model_index = i
            translation_model_found = True
            logger.debug(f"번역 모델 '{translation_model_name}' 찾음: 인덱스 {i}")
            break
    
    if not translation_model_found:
        logger.warning(f"번역 모델 '{translation_model_name}'을(를) 데이터에서 찾을 수 없습니다. 기본 인덱스 0을 사용합니다.")
    
    input_token_price_data = cost_sheet.get_whole_data('cost', 'I:I')
    input_token_price = input_token_price_data[model_index][0]
    logger.info(f"input_token_price: {input_token_price}")
    translation_input_token_price = input_token_price_data[translation_model_index][0]
    logger.info(f"translation_input_token_price: {translation_input_token_price}")

    output_token_price_data = cost_sheet.get_whole_data('cost', 'J:J')
    output_token_price = output_token_price_data[model_index][0]
    logger.info(f"output_token_price: {output_token_price}")
    translation_output_token_price = output_token_price_data[translation_model_index][0]
    logger.info(f"translation_output_token_price: {translation_output_token_price}")

    return {
        'input_token_price': input_token_price,
        'translation_input_token_price': translation_input_token_price,
        'output_token_price': output_token_price,
        'translation_output_token_price': translation_output_token_price
    }
