from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import re
from dotenv import load_dotenv
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class CoverLetterGenerator:
    def __init__(self):
        try:
            self.llm = ChatOpenAI(model_name="o1-mini")
            logger.info("ChatOpenAI 초기화 성공")
        except Exception as e:
            logger.error(f"ChatOpenAI 초기화 실패: {str(e)}")
            raise
        
    def count_korean_chars(self, text):
        try:
            # 공백을 제거하지 않고 전체 문자열 길이를 계산
            count = len(text)
            logger.debug(f"글자 수 계산: {count}자")
            return count
        except Exception as e:
            logger.error(f"글자 수 계산 중 오류 발생: {str(e)}")
            raise
    
    def generate_answer(self, question, char_limit):
        try:
            logger.info(f"답변 생성 시작 - 질문: {question[:50]}... (글자수 제한: {char_limit}자)")
            prompt_limit = char_limit * 2
            
            initial_prompt = ChatPromptTemplate.from_messages([
                ("user", f"""당신은 자기소개서 작성을 돕는 전문가입니다.
                답변은 반드시 공백을 포함하여 정확히 {char_limit}자여야 합니다.
                
                답변을 작성한 후 반드시 글자수를 확인하고,
                {char_limit}자가 될 때까지 수정하세요.
                답변 내용에는 글자 수에 대한 언급을 하지 마세요.
                
                Assistant: 네, 답변을 작성하고 글자수를 확인하겠습니다.
                
                Human: 그럼 답변을 작성해주세요."""),
                ("user", f"다음 질문에 대해 답변해주세요: {question}")
            ])
            
            logger.debug("첫 번째 답변 생성 시도")
            answer = (
                initial_prompt | 
                self.llm
            ).invoke({
                "char_limit": char_limit,
                "prompt_limit": prompt_limit,
                "question": question
            }).content
            
            max_attempts = 5
            attempt = 1
            
            while attempt < max_attempts:
                current_length = self.count_korean_chars(answer)
                logger.info(f"시도 {attempt}: 현재 글자수 {current_length}자")
                
                if current_length == char_limit:
                    logger.info("목표 글자수 달성")
                    break
                    
                diff = char_limit - current_length
                direction = "추가" if diff > 0 else "삭제"
                prompt_diff = abs(diff)
                
                # 총 {char_limit}자가 되도록 수정해주세요.

                logger.debug(f"글자수 조정 필요: {abs(diff)}자 {direction} 필요")
                adjust_prompt = ChatPromptTemplate.from_messages([
                    ("user", f"""당신은 자기소개서 작성을 돕는 전문가입니다.
                    현재 답변을 수정하여 정확히 {char_limit}자가 되도록 해주세요.
                    
                    답변을 수정할 때마다 글자수를 확인하세요.
                    
                    {char_limit}자가 될 때까지 수정하세요.
                    의미는 최대한 유지하면서 자연스럽게 수정해주세요.
                    답변 내용에는 글자 수에 대한 언급을 하지 마세요.
                    
                    Assistant: 네, 답변을 수정하고 글자수를 확인하겠습니다.
                    
                    Human: 그럼 답변을 수정해주세요."""),
                    ("assistant", answer),
                    ("user", "답변을 자연스럽게 수정해주세요.")
                ])
                
                logger.debug(f"답변 조정 시도 {attempt}")
                answer = (
                    adjust_prompt | 
                    self.llm
                ).invoke({
                    "char_limit": char_limit,
                    "diff": abs(diff),
                    "current_length": current_length
                }).content
                
                attempt += 1
            
            final_length = self.count_korean_chars(answer)
            if final_length != char_limit:
                logger.warning(f"최종 글자수 불일치 (목표: {char_limit}자, 최종: {final_length}자)")
            else:
                logger.info("글자수 조정 성공")
                
            return answer
            
        except Exception as e:
            logger.error(f"답변 생성 중 오류 발생: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        generator = CoverLetterGenerator()
        question = "본인의 장점과 단점을 서술해주세요."
        answer = generator.generate_answer(question, 1000)
        final_count = generator.count_korean_chars(answer)
        logger.info("답변 생성 성공")
        logger.debug(f"생성된 답변 ({final_count}자): {answer}")
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류 발생: {str(e)}")