#!/usr/bin/env python3
import logging
import math
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from dotenv import load_dotenv

load_dotenv()

# 로깅 설정: DEBUG 레벨
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_answer(question: str, max_length: int, max_attempts: int = 10) -> str:
    """
    LLM을 통해 자기소개서 문항에 대해 답변을 생성하며, 생성된 답변의 길이가
    max_length의 0.5% 오차 범위(최소: max_length * 0.995, 최대: max_length) 내에 있는지 확인한다.
    만약 조건을 만족하지 않으면, 최대 max_attempts만큼 재시도하며, 부족한 문자 수를 LLM에 안내한다.
    """
    # 답변 길이 허용 범위 설정
    lower_bound = math.ceil(max_length * 0.995)
    logger.debug(f"요청된 최대 길이: {max_length}자, 허용 최소 길이: {lower_bound}자")
    
    # 프롬프트 템플릿 구성 (추가 지시사항을 위한 변수 추가)
    prompt_template_str = (
        "자기소개서 문항: {question}\n\n"
        "위 문항에 대해 답변을 작성해 주세요. "
        "답변은 최대 {max_length}자 이내이며, 최소 {lower_bound}자 이상 작성되어야 합니다.\n"
        "{additional_instruction}"
        "답변은 해당 조건을 엄격하게 준수해야 합니다."
    )
    prompt_template = PromptTemplate(
        template=prompt_template_str,
        input_variables=["question", "max_length", "lower_bound", "additional_instruction"]
    )
    
    # LangChain LLM 및 체인 초기화
    llm = ChatOpenAI(model_name="o1-mini", temperature=1)
    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    attempt = 1
    additional_instruction = ""  # 첫 시도에서는 추가 안내 없음
    while attempt <= max_attempts:
        logger.debug(f"답변 생성 시도: {attempt}회")
        try:
            answer = chain.run(
                question=question,
                max_length=str(max_length),
                lower_bound=str(lower_bound),
                additional_instruction=additional_instruction
            )
            answer_length = len(answer)
            logger.debug(f"생성된 답변 길이: {answer_length}자")
            
            if lower_bound <= answer_length <= max_length:
                logger.info("생성된 답변이 조건을 만족합니다.")
                return answer
            else:
                # 부족하거나 초과하는 경우, LLM에 추가 정보를 제공하기 위한 안내 메시지 구성
                if answer_length < lower_bound:
                    missing_min = lower_bound - answer_length
                    missing_max = max_length - answer_length
                    additional_instruction = (
                        f"현재 생성된 답변이 {answer_length}자입니다. "
                        f"최소 추가로 {missing_min}자에서 최대 {missing_max}자를 더 작성하여 전체 조건(총 {lower_bound}~{max_length}자)을 만족하도록 보완해 주세요.\n"
                        f"현재까지 생성된 답변: {answer}\n"
                    )
                    logger.warning(
                        f"생성된 답변 길이({answer_length}자)가 조건({lower_bound}-{max_length}자)에 맞지 않음. "
                        f"추가 안내: {additional_instruction.strip()}"
                    )
                else:  # answer_length > max_length 인 경우
                    excess = answer_length - max_length
                    additional_instruction = (
                        f"현재 생성된 답변이 {answer_length}자입니다. "
                        f"초과된 {excess}자를 제거하여 전체 조건(총 {lower_bound}~{max_length}자)을 만족하도록 보완해 주세요.\n"
                        f"현재까지 생성된 답변: {answer}\n"
                    )
                    logger.warning(
                        f"생성된 답변 길이({answer_length}자)가 조건({lower_bound}-{max_length}자)에 맞지 않음. "
                        f"추가 안내: {additional_instruction.strip()}"
                    )
        except Exception as e:
            logger.error(f"답변 생성 중 오류 발생: {e}", exc_info=True)
        attempt += 1
    
    error_msg = f"최대 {max_attempts}회 시도 후에도 적절한 답변을 생성하지 못했습니다."
    logger.error(error_msg)
    raise ValueError(error_msg)

def get_user_input() -> (str, int):
    """
    사용자로부터 자기소개서 문항과 답변 최대 길이를 입력받는다.
    """
    try:
        question = input("자기소개서 문항을 입력하세요: ").strip()
        if not question:
            raise ValueError("입력된 문항이 비어 있습니다.")
        max_length_input = input("생성할 답변의 최대 문자 수를 입력하세요 (예: 1000): ").strip()
        max_length = int(max_length_input)
        if max_length <= 0:
            raise ValueError("답변 길이는 양의 정수여야 합니다.")
        return question, max_length
    except Exception as e:
        logger.error(f"입력 처리 중 오류 발생: {e}", exc_info=True)
        raise

def main():
    """
    메인 함수: 사용자 입력을 받고, 답변을 생성하여 출력한다.
    """
    try:
        question, max_length = get_user_input()
        answer = generate_answer(question, max_length)
        print("\n생성된 답변:\n")
        print(answer)
    except Exception as e:
        logger.error(f"메인 함수에서 오류 발생: {e}", exc_info=True)

if __name__ == "__main__":
    main()