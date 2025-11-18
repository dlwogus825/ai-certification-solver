# 🧠 AI Certification Solver Platform
AI 기반 자격증 문제 풀이 & 해설 자동 생성 플랫폼

문제 텍스트와 보기를 입력하면, LLM(Claude/Gemini)이 정답·해설·개념 설명을 자동으로 생성해주는 학습 도우미 서비스입니다.

---

## 🚀 주요 기능
- 문제/보기 등록 및 조회 (JSON 구조)
- Claude/Gemini 기반 AI 해설 생성
- 난이도·개념·추가 학습 팁 자동 생성
- Vue.js 기반 웹 UI (로그인/대시보드/문제풀이 화면)
- PDF → OCR → 문제 자동 추출 기능 (진행 중)
- Admin Panel(문제/공지 관리)

---

## 🛠 기술 스택
**Backend:** FastAPI, Python  
**Frontend:** Vue.js  
**DB:** MySQL / MariaDB  
**AI:** Claude 3.5 Sonnet, Gemini API  
**Infra:** Docker, .env, GitHub  
**OCR:** Python + Tesseract (예정)

---

## ⚙ 설치 & 실행 (요약)

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

---
cd frontend
npm install
npm run serve



---

# ✔️ 특징
- **1분 안에 읽힘**
- **딱 필요한 정보만** 들어 있음
- 깔끔하고 정리된 구조
- HR 담당자가 가장 좋아하는 형태

---

원하면  
📌 *노션용 프로젝트 소개 페이지도 콤팩트 버전으로 만들어줄까?*
