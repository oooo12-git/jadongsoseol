import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from get_data.get_token_price import get_token_price
import logging
import yfinance as yf
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def calculation_cost(model_name, translation_model_name, prompt_tokens, completion_tokens, translation_prompt_tokens, translation_completion_tokens):
    logger.debug("Starting cost calculation")

    token_price = get_token_price(model_name, translation_model_name)
    input_token_price = token_price['input_token_price']
    translation_input_token_price = token_price['translation_input_token_price']
    output_token_price = token_price['output_token_price']
    translation_output_token_price = token_price['translation_output_token_price']

    prompt_cost = (prompt_tokens * float(input_token_price))
    completion_cost = (completion_tokens * float(output_token_price))
    translation_prompt_cost = (translation_prompt_tokens * float(translation_input_token_price))
    translation_completion_cost = (translation_completion_tokens * float(translation_output_token_price))
    
    total_cost = prompt_cost + completion_cost + translation_prompt_cost + translation_completion_cost
    
    return total_cost

def usd_to_krw(dollar_amount):
    """
    yfinance를 사용하여 실시간 원달러 환율을 가져와 달러를 원화로 변환합니다.
    
    Args:
        dollar_amount (float): 변환할 달러 금액
        
    Returns:
        int: 원화로 변환된 금액 (정수로 반올림)
    """
    logger.debug(f"Converting {dollar_amount} USD to KRW")
    
    try:
        # USD/KRW 환율 정보 가져오기
        ticker = "KRW=X"  # Yahoo Finance에서 원달러 환율 티커
        
        # 오늘과 어제 날짜 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # 최근 7일 데이터 요청 (데이터 누락 가능성 대비)
        
        # 환율 데이터 가져오기
        exchange_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if exchange_data.empty:
            logger.warning("환율 데이터를 가져오지 못했습니다. 기본값 1300 사용")
            exchange_rate = 1300
        else:
            # 가장 최근 종가 사용 (float 값으로 변환) - 경고 메시지 수정
            exchange_rate = float(exchange_data['Close'].iloc[-1].item())
            logger.info(f"현재 원달러 환율: {exchange_rate:.2f}")
        
        # 달러를 원화로 변환
        krw_amount = dollar_amount * exchange_rate
        logger.debug(f"변환 결과: {dollar_amount} USD = {krw_amount:.2f} KRW (환율: {exchange_rate:.2f})")
        
        # 정수로 반올림하여 반환
        return round(krw_amount)
    
    except Exception as e:
        logger.error(f"환율 변환 중 오류 발생: {str(e)}")
        logger.warning("기본 환율 1300 사용")
        return round(dollar_amount * 1300)