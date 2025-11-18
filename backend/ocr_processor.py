import os
import json
import sys
import anthropic
from dotenv import load_dotenv

from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import re # Moved import re to the top

# .env 파일 로드
load_dotenv()



# Anthropic 클라이언트 초기화
api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"OCR DEBUG: API Key loaded: {api_key[:20] if api_key else 'None'}...")
if not api_key or api_key == "sk-test-key":
    print("Info: Running in development mode - AI features disabled.")
    client = None
else:
    client = anthropic.Anthropic(api_key=api_key)
    print("OCR DEBUG: Anthropic client initialized successfully!")


pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD", '')

def process_pdf_for_text(pdf_path: str) -> str:
    """
    PDF 파일에서 OCR을 수행하여 텍스트를 추출하는 함수.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return ""

    print(f"Processing PDF for OCR: {pdf_path}")
    extracted_text_pages = []

    try:
        # PDF를 이미지로 변환
        images = convert_from_path(pdf_path)

        for i, image in enumerate(images):
            # 각 이미지에 대해 OCR 수행
            text = pytesseract.image_to_string(image, lang='kor+eng') # 한국어 및 영어 OCR
            extracted_text_pages.append(f"--- Page {i+1} ---\n{text}")

    except Exception as e:
        print(f"Error during OCR processing (image conversion/tesseract): {e}")
        # OCR 실패 시, PyPDF2를 사용하여 텍스트 기반 PDF에서 텍스트 추출 시도
        try:
            reader = PdfReader(pdf_path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    extracted_text_pages.append(f"--- Page {i+1} (Text Extraction) ---\n{text}")
                else:
                    extracted_text_pages.append(f"--- Page {i+1} (No Text Extracted) ---\n")
        except Exception as e_fallback:
            print(f"Fallback text extraction failed: {e_fallback}")
            return "" # 모든 시도 실패 시 빈 문자열 반환

    return "\n".join(extracted_text_pages)


def parse_questions_from_text(text: str) -> list:
    """
    Anthropic Claude를 사용하여 텍스트에서 문제와 보기를 파싱하는 함수.
    """
    if not client:
        print("Error: Anthropic client is not configured.")
        return []

    try:
        prompt = (
            f"Human: 당신은 주어진 텍스트에서 객관식 문제와 그에 따른 보기, 정답을 정확하게 추출하여 JSON 형식으로 만드는 전문가입니다.\n\n"
            f"다음 규칙에 따라 텍스트에서 문제 정보를 추출해 주세요:\n"
            f"1.  문제는 일반적으로 숫자로 시작합니다 (예: `1.`, `2.`).\n"
            f"2.  보기는 일반적으로 원 문자 또는 괄호 숫자로 시작합니다 (예: `①`, `②`, `③`, `④` 또는 `1)`, `2)`, `3)`, `4)`).\n"
            f"3.  정답은 텍스트 내에 `정답: ①` 또는 `답: 1` 과 같은 명시적인 표시가 있을 수 있습니다. 이 표시를 찾아 `is_correct` 필드를 `true`로 설정해야 합니다.\n"
            f"4.  만약 명시적인 정답 표시를 찾을 수 없다면, 그 문제는 추출하지 마세요.\n"
            f"5.  객관식 보기가 4개 미만인 문제, 또는 문제로 보기 어려운 텍스트는 결과에 포함하지 마세요.\n"
            f"6.  추출된 각 문제는 `question_text` 필드를 가져야 합니다.\n"
            f"7.  추출된 각 보기는 `option_text` (보기 내용)와 `is_correct` (정답 여부, boolean) 필드를 가져야 합니다.\n"
            f"8.  최종 결과는 반드시 아래 예시와 동일한 `questions` 키를 가진 JSON 객체 안에 리스트 형태로 반환해야 합니다. 다른 어떤 텍스트도 추가하지 마세요.\n\n"
            f"**JSON 출력 형식 예시:**\n"
            f"```json\n{{\n  \"questions\": [\n    {{\n      \"question_text\": \"여기에 첫 번째 문제의 내용이 들어갑니다.\",\n      \"options\": [\n        {{\"option_text\": \"첫 번째 보기 내용\", \"is_correct\": false}},\n        {{\"option_text\": \"두 번째 보기 내용(이것이 정답)\", \"is_correct\": true}},\n        {{\"option_text\": \"세 번째 보기 내용\", \"is_correct\": false}},\n        {{\"option_text\": \"네 번째 보기 내용\", \"is_correct\": false}}\n      ]\n    }},\n    {{\n      \"question_text\": \"여기에 두 번째 문제의 내용이 들어갑니다.\",\n      \"options\": [\n        {{\"option_text\": \"보기 A\", \"is_correct\": false}},\n        {{\"option_text\": \"보기 B\", \"is_correct\": false}},\n        {{\"option_text\": \"보기 C(이것이 정답)\", \"is_correct\": true}},\n        {{\"option_text\": \"보기 D\", \"is_correct\": false}}\n      ]\n    }}\n  ]\n}}\n```\n\n"
            f"**추출할 원본 텍스트:**\n"
            f"---\n{text}\n---\n\n"
            f"Assistant:\n"
            f"```json\n"
        )

        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",  # 최신 Claude 모델
            max_tokens=4096,
            temperature=0.3,  # 낮은 온도로 더 일관된 결과 생성
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = message.content[0].text
        try:
            # 응답 텍스트에서 가장 먼저 나오는 '{'와 가장 마지막의 '}'를 찾아 JSON을 파싱
            start_index = response_text.find(chr(123))
            end_index = response_text.rfind(chr(125)) + 1
            if start_index != -1 and end_index != 0:
                json_string = response_text[start_index:end_index]
                parsed_result = json.loads(json_string)
                return parsed_result.get("questions", [])
            else:
                raise ValueError("No JSON object found in Claude's response.")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error parsing JSON from Anthropic response: {e}")
            print(f"Received content: {response_text}")
            return []


    except Exception as e:
        print(f"An error occurred during Anthropic API call: {e}")
        return []


    
