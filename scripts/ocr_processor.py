import os
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from typing import List, Dict, Optional

# Tesseract OCR 설치 경로를 여기에 지정하세요 (필요한 경우)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_pdf_for_text(pdf_path: str) -> str:
    """
    PDF 파일에서 OCR을 수행하여 텍스트를 추출하는 함수.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return ""

    print(f"Processing PDF for OCR: {pdf_path}")
    extracted_text = []

    try:
        # PDF를 이미지로 변환
        images = convert_from_path(pdf_path)

        for i, image in enumerate(images):
            # 각 이미지에 대해 OCR 수행
            text = pytesseract.image_to_string(image, lang='kor+eng') # 한국어 및 영어 OCR
            extracted_text.append(f"--- Page {i+1} ---\n{text}")

    except Exception as e:
        print(f"Error during OCR processing: {e}")
        # PyPDF2를 사용하여 텍스트 기반 PDF에서 텍스트 추출 시도 (OCR 실패 시 대체)
        try:
            reader = PdfReader(pdf_path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    extracted_text.append(f"--- Page {i+1} (Text Extraction) ---\n{text}")
                else:
                    extracted_text.append(f"--- Page {i+1} (No Text Extracted) ---\n")
        except Exception as e_fallback:
            print(f"Fallback text extraction failed: {e_fallback}")

    return "\n".join(extracted_text)


def process_pdf_for_questions(pdf_path: str) -> List[Dict]:
    """
    PDF 파일에서 OCR을 수행하고 문제와 보기를 파싱하는 함수.
    현재는 더미 데이터를 반환하며, 실제 파싱 로직은 여기에 구현되어야 합니다.
    """
    full_text = process_pdf_for_text(pdf_path)
    print("Full text extracted. Now, implement question parsing logic here.")

    # TODO: 추출된 full_text를 기반으로 문제와 보기를 파싱하는 로직 구현
    # 예: 정규 표현식, 키워드 매칭, 또는 LLM (OpenAI API) 활용
    # 반환되는 데이터 구조는 ParsedQuestion 모델과 일치해야 합니다.

    # 임시 반환 값 (실제 구현 시 교체)
    dummy_questions = [
        {
            "question_text": "다음 중 인공지능의 주요 분야가 아닌 것은?",
            "question_type": "multiple_choice",
            "difficulty": 3,
            "options": [
                {"option_text": "머신러닝", "is_correct": False},
                {"option_text": "딥러닝", "is_correct": False},
                {"option_text": "로봇 공학", "is_correct": False},
                {"option_text": "양자 역학", "is_correct": True}
            ]
        },
        {
            "question_text": "파이썬에서 리스트의 길이를 반환하는 함수는?",
            "question_type": "short_answer",
            "difficulty": 2,
            "options": [] # 단답형이므로 보기는 비워둠
        },
        {
            "question_text": "OCR은 무엇의 약자인가요?",
            "question_type": "short_answer",
            "difficulty": 1,
            "options": []
        }
    ]
    return dummy_questions

if __name__ == "__main__":
    # 예시 사용법
    # 테스트용 PDF 파일을 준비하고 경로를 지정하세요.
    # test_pdf_path = "path/to/your/test.pdf"
    # if os.path.exists(test_pdf_path):
    #     extracted_content = process_pdf_for_text(test_pdf_path)
    #     print("\n--- Extracted Content ---\n")
    #     print(extracted_content)
    # else:
    #     print(f"Test PDF not found at {test_pdf_path}")

    # questions = process_pdf_for_questions(test_pdf_path)
    # for q in questions:
    #     print(f"Question: {q['question_text']}")
    #     print(f"Options: {q['options']}")
    pass