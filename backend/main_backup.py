# C:\cert\ai_cert_platform\backend\main.py

import os
from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Request
from fastapi.staticfiles import StaticFiles # StaticFiles 임포트
from uuid import uuid4 # 고유한 파일 이름 생성을 위한 uuid 임포트
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship, selectinload
from datetime import datetime, timedelta
from typing import Optional, List
import secrets

# JWT 관련 라이브러리
from jose import JWTError, jwt

# CORS 미들웨어 임포트
from fastapi.middleware.cors import CORSMiddleware

# Rate limiting (temporarily disabled)
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded

# Anthropic 라이브러리 임포트
from dotenv import load_dotenv
import anthropic

# OCR 처리 스크립트 임포트
from ocr_processor import process_pdf_for_text, parse_questions_from_text

# .env 파일 로드
load_dotenv()

# Anthropic 클라이언트 초기화 (개발 모드에서는 임시로 비활성화)
api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key and api_key != "sk-test-key":
    client = anthropic.Anthropic(api_key=api_key)
else:
    client = None  # 개발 모드에서는 AI 기능 비활성화

# 비밀번호 해싱을 위한 컨텍스트 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 데이터베이스 설정
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_cert_platform.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 데이터베이스 모델 정의
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    is_admin = Column(Boolean, default=False) # 관리자 여부 필드 추가
    profile_picture_url = Column(String(255), nullable=True) # 프로필 사진 URL 필드 추가
    created_at = Column(DateTime, default=datetime.utcnow) # 생성일 필드 추가

# 사용자 프로필 확장 테이블 모델
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    real_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    age_group = Column(String(20), nullable=True)
    education_level = Column(String(50), nullable=True)
    target_certifications = Column(Text, nullable=True)  # JSON 문자열로 저장
    bio = Column(Text, nullable=True)
    daily_goal = Column(Integer, default=5)
    study_time_goal = Column(String(20), default="1시간")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")

# 자격증 정보 테이블 모델
class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)

    questions = relationship("Question", back_populates="certification")

# 문제 테이블 모델
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=True) # 자격증과 연결 (선택 사항)
    ocr_document_id = Column(Integer, ForeignKey("ocr_documents.id"), nullable=True) # OCR 문서와 연결 (선택 사항)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50)) # 예: 'multiple_choice', 'short_answer'
    difficulty = Column(Integer) # 1-5

    certification = relationship("Certification", back_populates="questions")
    ocr_document = relationship("OcrDocument") # OcrDocument와의 관계 설정
    options = relationship("Option", back_populates="question")

# 보기 테이블 모델 (객관식 문제용)
class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean) # BOOLEAN으로 변경

    question = relationship("Question", back_populates="options")

# OCR 문서 저장 테이블 모델
class OcrDocument(Base):
    __tablename__ = "ocr_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    extracted_text = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

# 사용자 답안 테이블 모델
class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    submitted_answer = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    question = relationship("Question")


# 데이터베이스 테이블 생성 (애플리케이션 시작 시)
Base.metadata.create_all(bind=engine)

# 초기 관리자 계정 생성 (애플리케이션 시작 시 한 번만 실행)
def create_initial_admin_user():
    print("=== 관리자 계정 생성 시작 ===")
    db = SessionLocal()
    try:
        # 데이터베이스 연결 테스트
        print("데이터베이스 연결 확인...")
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        print("데이터베이스 연결 성공!")
        
        admin_username = "admin"  # 하드코딩으로 확실하게
        admin_password = "1234"   # 하드코딩으로 확실하게
        admin_email = "admin@example.com"  # 하드코딩으로 확실하게

        print(f"관리자 계정 생성 중... (사용자명: {admin_username})")

        # 기존 관리자 계정 삭제 (개발 모드에서만)
        existing_admin = db.query(User).filter(User.username == admin_username).first()
        if existing_admin:
            db.delete(existing_admin)
            db.commit()
            print(f"기존 관리자 계정 '{admin_username}' 삭제됨")

        # 새 관리자 계정 생성
        print("비밀번호 해시 생성 중...")
        hashed_password = pwd_context.hash(admin_password)
        print("관리자 사용자 객체 생성 중...")
        
        admin_user = User(
            username=admin_username,
            email=admin_email,
            password_hash=hashed_password,
            is_admin=True
        )
        
        print("데이터베이스에 사용자 추가 중...")
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"=== 관리자 계정 생성 완료 ===")
        print(f"사용자명: {admin_username}")
        print(f"이메일: {admin_email}")  
        print(f"비밀번호: {admin_password}")
        print(f"관리자 권한: True")
        print(f"사용자 ID: {admin_user.id}")
        print(f"===========================")
        
    except Exception as e:
        print(f"ERROR: 관리자 계정 생성 실패: {e}")
        print(f"오류 타입: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


# 의존성 주입: 데이터베이스 세션 가져오기
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rate limiting 설정
# limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 파일 업로드 크기 제한 설정 (10MB)
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024  # Convert MB to bytes

# 프로필 사진 저장 디렉토리 설정
PROFILE_PICTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profile_pictures")
os.makedirs(PROFILE_PICTURE_DIR, exist_ok=True)
print(f"Serving static files from: {PROFILE_PICTURE_DIR}") # 디버깅을 위한 출력

# 정적 파일 서빙 설정
app.mount("/profile_pictures", StaticFiles(directory=PROFILE_PICTURE_DIR), name="profile_pictures")

# CORS 미들웨어 추가
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:8080")
origins = [origin.strip() for origin in cors_origins.split(",")]

# 개발 환경에서는 와일드카드 허용
if os.getenv("ENVIRONMENT", "development") == "development":
    print(f"개발 모드: CORS origins = {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# JWT 설정
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    # 개발 환경에서만 자동 생성 허용
    if os.getenv("ENVIRONMENT", "development") == "development":
        SECRET_KEY = secrets.token_urlsafe(32)
        print("WARNING: Using auto-generated JWT_SECRET_KEY. Set JWT_SECRET_KEY in production!")
    else:
        raise ValueError("JWT_SECRET_KEY environment variable not set.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 비밀번호 검증 함수
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 이메일 인증 토큰 생성
def generate_verification_token():
    return secrets.token_urlsafe(32)

# 이메일 인증 이메일 발송
async def send_verification_email(email: str, token: str):
    if not fastmail:
        print("이메일 설정이 없어 이메일을 발송할 수 없습니다.")
        return False
    
    try:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8080")
        verification_url = f"{frontend_url}/verify-email?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>이메일 인증</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #1976D2 0%, #42A5F5 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .btn {{ display: inline-block; background: #1976D2; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎓 AI 자격증 학습 플랫폼</h1>
                    <p>이메일 주소를 인증해주세요</p>
                </div>
                <div class="content">
                    <p>안녕하세요!</p>
                    <p>AI 자격증 학습 플랫폼에 가입해주셔서 감사합니다.</p>
                    <p>아래 버튼을 클릭하여 이메일 주소를 인증해주세요:</p>
                    
                    <div style="text-align: center;">
                        <a href="{verification_url}" class="btn">이메일 인증하기</a>
                    </div>
                    
                    <p>버튼이 작동하지 않으면 아래 링크를 복사하여 브라우저에 붙여넣으세요:</p>
                    <p style="word-break: break-all; background: #e9ecef; padding: 10px; border-radius: 5px;">
                        {verification_url}
                    </p>
                    
                    <p><strong>주의:</strong> 이 링크는 24시간 후에 만료됩니다.</p>
                </div>
                <div class="footer">
                    <p>이 이메일은 자동으로 발송되었습니다. 답장하지 마세요.</p>
                    <p>© 2025 AI 자격증 학습 플랫폼. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject="[AI 자격증 학습 플랫폼] 이메일 인증을 완료해주세요",
            recipients=[email],
            body=html_content,
            subtype=MessageType.html
        )
        
        await fastmail.send_message(message)
        return True
        
    except Exception as e:
        print(f"이메일 발송 중 오류 발생: {e}")
        return False

# JWT 토큰 생성 함수
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 사용자 인증 함수
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

# JWT 토큰에서 사용자 가져오기
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="관리자 권한이 필요합니다.")
    return current_user

# 회원가입 요청을 위한 데이터 모델 정의
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# 로그인 응답을 위한 토큰 모델 정의
class Token(BaseModel):
    access_token: str
    token_type: str

# 사용자 정보 응답을 위한 모델 정의 (비밀번호 제외)
class UserInDB(BaseModel):
    username: str
    email: str
    is_admin: bool
    profile_picture_url: Optional[str] = None
    is_email_verified: bool = False

# 이메일 인증 관련 모델들
class EmailVerificationRequest(BaseModel):
    email: str

class EmailVerificationResponse(BaseModel):
    message: str
    verification_sent: bool = True

class VerifyEmailRequest(BaseModel):
    token: str

class VerifyEmailResponse(BaseModel):
    message: str
    email_verified: bool = True

# 문제 보기 응답을 위한 모델 정의
class OptionResponse(BaseModel):
    id: int
    option_text: str
    is_correct: int # 0 or 1

# 문제 응답을 위한 모델 정의
class QuestionResponse(BaseModel):
    id: int
    question_text: str
    question_type: Optional[str] = None
    difficulty: Optional[int] = None
    certification_id: Optional[int] = None
    options: List[OptionResponse] = [] # 보기가 없는 문제도 있을 수 있으므로 기본값 빈 리스트

    class Config:
        from_attributes = True # SQLAlchemy 모델과 Pydantic 모델 간의 매핑을 허용

# AI 해설 요청을 위한 모델 정의
class ExplanationRequest(BaseModel):
    question_text: str
    options: Optional[List[str]] = None # 보기가 있다면 함께 전달

# AI 해설 응답을 위한 모델 정의
class ExplanationResponse(BaseModel):
    explanation: str

# 문제 풀이 요청을 위한 모델
class SubmitAnswerRequest(BaseModel):
    question_id: int
    submitted_answer: str

# 문제 풀이 응답을 위한 모델
class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None

# 파싱된 문제 보기를 위한 모델
class ParsedOption(BaseModel):
    option_text: str
    is_correct: bool = False # 정답 여부 (기본값 False)

# 파싱된 문제를 위한 모델
class ParsedQuestion(BaseModel):
    question_text: str
    question_type: Optional[str] = None
    difficulty: Optional[int] = None
    options: List[ParsedOption] = []

# 비밀번호 재설정 요청을 위한 모델
class PasswordResetRequest(BaseModel):
    username: str
    email: str

# 비밀번호 재설정 응답을 위한 모델
class PasswordResetResponse(BaseModel):
    message: str
    new_password: Optional[str] = None

# OCR 문서 응답을 위한 모델
class OcrDocumentResponse(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

# 사용자 정보 업데이트 요청을 위한 모델 정의
class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None

# 사용자 프로필 관련 Pydantic 모델들
class UserProfileCreate(BaseModel):
    real_name: Optional[str] = None
    phone: Optional[str] = None
    age_group: Optional[str] = None
    education_level: Optional[str] = None
    target_certifications: Optional[List[str]] = []
    bio: Optional[str] = None
    daily_goal: Optional[int] = 5
    study_time_goal: Optional[str] = "1시간"

class UserProfileUpdate(BaseModel):
    real_name: Optional[str] = None
    phone: Optional[str] = None
    age_group: Optional[str] = None
    education_level: Optional[str] = None
    target_certifications: Optional[List[str]] = None
    bio: Optional[str] = None
    daily_goal: Optional[int] = None
    study_time_goal: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    real_name: Optional[str]
    phone: Optional[str]
    age_group: Optional[str]
    education_level: Optional[str]
    target_certifications: Optional[List[str]]
    bio: Optional[str]
    daily_goal: int
    study_time_goal: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@app.get("/")
# @limiter.limit(os.getenv("RATE_LIMIT_PER_MINUTE", "60") + "/minute")
def read_root(request: Request):
    return {"message": "AI Cert Platform Backend is running!"}

@app.post("/register", status_code=status.HTTP_201_CREATED)
# @limiter.limit(os.getenv("RATE_LIMIT_PER_HOUR", "10") + "/hour")
async def register_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    # 사용자 이름 또는 이메일 중복 확인
    db_user_by_username = db.query(User).filter(User.username == user.username).first()
    if db_user_by_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    db_user_by_email = db.query(User).filter(User.email == user.email).first()
    if db_user_by_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # 비밀번호 해싱
    hashed_password = pwd_context.hash(user.password)
    
    # 이메일 인증 토큰 생성
    verification_token = generate_verification_token()

    # 새 사용자 생성 및 DB 저장
    new_user = User(
        username=user.username, 
        email=user.email, 
        password_hash=hashed_password,
        email_verification_token=verification_token,
        email_verification_sent_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 이메일 인증 이메일 발송
    email_sent = await send_verification_email(user.email, verification_token)
    
    return {
        "message": "User registered successfully. Please check your email for verification.",
        "username": new_user.username,
        "email": new_user.email,
        "email_verification_sent": email_sent
    }

@app.post("/token", response_model=Token)
# @limiter.limit(os.getenv("RATE_LIMIT_PER_MINUTE", "20") + "/minute")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "is_admin": user.is_admin}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 이메일 인증 관련 엔드포인트

# 이메일 인증 재발송
@app.post("/resend-verification", response_model=EmailVerificationResponse)
async def resend_verification_email(request: EmailVerificationRequest, db: Session = Depends(get_db)):
    # 사용자 확인
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="해당 이메일로 등록된 계정을 찾을 수 없습니다."
        )
    
    # 이미 인증된 경우
    if user.is_email_verified:
        return EmailVerificationResponse(
            message="이미 이메일 인증이 완료된 계정입니다.",
            verification_sent=False
        )
    
    # 새로운 인증 토큰 생성
    verification_token = generate_verification_token()
    user.email_verification_token = verification_token
    user.email_verification_sent_at = datetime.utcnow()
    db.commit()
    
    # 이메일 발송
    email_sent = await send_verification_email(request.email, verification_token)
    
    return EmailVerificationResponse(
        message="인증 이메일이 재발송되었습니다. 이메일을 확인해주세요.",
        verification_sent=email_sent
    )

# 이메일 인증 처리
@app.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    # 토큰으로 사용자 찾기
    user = db.query(User).filter(User.email_verification_token == request.token).first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="유효하지 않은 인증 토큰입니다."
        )
    
    # 토큰 만료 확인 (24시간)
    if user.email_verification_sent_at:
        time_diff = datetime.utcnow() - user.email_verification_sent_at
        if time_diff.total_seconds() > 24 * 60 * 60:  # 24시간
            raise HTTPException(
                status_code=400,
                detail="인증 토큰이 만료되었습니다. 새로운 인증 이메일을 요청해주세요."
            )
    
    # 이메일 인증 완료
    user.is_email_verified = True
    user.email_verification_token = None
    user.email_verification_sent_at = None
    db.commit()
    
    return VerifyEmailResponse(
        message="이메일 인증이 완료되었습니다!",
        email_verified=True
    )

# 비밀번호 재설정 엔드포인트
# OPTIONS 요청 처리 (CORS preflight)
@app.options("/resend-verification")
async def resend_verification_options():
    return {"message": "OK"}

@app.options("/verify-email")
async def verify_email_options():
    return {"message": "OK"}

@app.options("/reset-password")
async def reset_password_options():
    return {"message": "OK"}

@app.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    # 사용자 확인
    user = db.query(User).filter(
        User.username == request.username, 
        User.email == request.email
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=404, 
            detail="해당 사용자명과 이메일에 일치하는 계정을 찾을 수 없습니다."
        )
    
    # 임시 비밀번호 생성 (개발 환경에서는 간단한 비밀번호 사용)
    import random
    import string
    new_password = ''.join(random.choices(string.digits, k=6))  # 6자리 숫자
    
    # 비밀번호 업데이트
    user.password_hash = pwd_context.hash(new_password)
    db.commit()
    
    return PasswordResetResponse(
        message="비밀번호가 재설정되었습니다. 새로운 비밀번호로 로그인해주세요.",
        new_password=new_password  # 개발환경에서만 반환 (실제로는 이메일 발송)
    )

@app.get("/users/me", response_model=UserInDB)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/users/me/profile-picture")
# @limiter.limit(os.getenv("RATE_LIMIT_PER_HOUR", "30") + "/hour")
async def upload_profile_picture(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 파일 크기 검증
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"파일 크기가 {MAX_FILE_SIZE // 1024 // 1024}MB를 초과합니다.")
    
    # 허용되는 파일 확장자
    allowed_extensions = {"png", "jpg", "jpeg", "gif"}
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="PNG, JPG, JPEG, GIF 파일만 업로드할 수 있습니다.")

    # 고유한 파일 이름 생성
    unique_filename = f"{uuid4()}.{file_extension}"
    file_location = os.path.join(PROFILE_PICTURE_DIR, unique_filename)

    try:
        # 파일 저장
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        # 기존 프로필 사진 삭제 (선택 사항: 공간 절약)
        if current_user.profile_picture_url:
            old_filename = current_user.profile_picture_url.split("/")[-1]
            old_file_location = os.path.join(PROFILE_PICTURE_DIR, old_filename)
            if os.path.exists(old_file_location):
                os.remove(old_file_location)

        # 사용자 모델 업데이트
        current_user.profile_picture_url = f"/profile_pictures/{unique_filename}"
        db.add(current_user)
        db.commit()
        db.refresh(current_user)

        return {"message": "프로필 사진이 성공적으로 업로드되었습니다.", "profile_picture_url": current_user.profile_picture_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로필 사진 업로드 중 오류 발생: {str(e)}")

@app.put("/users/me", response_model=UserInDB)
async def update_users_me(user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_update.email:
        # 이메일 중복 확인 (자신을 제외한 다른 사용자)
        existing_user = db.query(User).filter(User.email == user_update.email, User.id != current_user.id).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered by another user")
        current_user.email = user_update.email

    if user_update.password:
        current_user.password_hash = pwd_context.hash(user_update.password)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@app.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted successfully"}

@app.get("/questions", response_model=List[QuestionResponse])
async def get_questions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 로그인한 사용자만 문제 목록에 접근 가능
    questions = db.query(Question).options(
        selectinload(Question.options)
    ).all()
    return questions

@app.post("/explain/{question_id}", response_model=ExplanationResponse)
async def get_explanation(question_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not client:
        # 개발 모드에서는 더미 해설 반환
        return ExplanationResponse(explanation="개발 모드입니다. AI 해설 기능은 현재 비활성화되어 있습니다.")

    question = db.query(Question).options(selectinload(Question.options)).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")

    try:
        prompt_text = f"Human: 다음 문제에 대해 자세히 설명해 주세요: {question.question_text}"
        if question.options:
            options_text = ", ".join([opt.option_text for opt in question.options])
            prompt_text += f"\n보기: {options_text}"
        prompt_text += "\nAssistant:"

        # Anthropic Claude API 호출
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620", # 최신 Claude 모델
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt_text
                }
            ]
        )
        explanation = message.content[0].text
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 해설 생성 중 오류 발생: {str(e)}")

@app.post("/api/v1/problems/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(
    request: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(Question).options(selectinload(Question.options)).filter(Question.id == request.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")

    is_correct = False
    correct_option_text = None

    # 객관식 문제 채점 로직
    if question.question_type == 'multiple_choice':
        for option in question.options:
            if option.is_correct == 1: # 정답인 보기
                correct_option_text = option.option_text
                if option.option_text == request.submitted_answer: # 사용자가 제출한 답안과 정답 보기가 일치하는지 확인
                    is_correct = True
                break
    # TODO: 주관식 문제에 대한 채점 로직 추가 (필요시 AI 활용)

    # 사용자 답안 저장
    user_answer = UserAnswer(
        user_id=current_user.id,
        question_id=question.id,
        submitted_answer=request.submitted_answer,
        is_correct=is_correct
    )
    db.add(user_answer)
    db.commit()
    db.refresh(user_answer)

    return SubmitAnswerResponse(
        is_correct=is_correct,
        correct_answer=correct_option_text,
        explanation=None # 해설은 별도 API를 통해 제공
    )


# PDF 업로드 및 OCR 처리를 위한 엔드포인트
@app.post("/admin/upload-pdf-for-ocr")
# @limiter.limit(os.getenv("RATE_LIMIT_PER_HOUR", "20") + "/hour")
async def upload_pdf_for_ocr(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="관리자 권한이 필요합니다.")

    # 파일 크기 검증
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"파일 크기가 {MAX_FILE_SIZE // 1024 // 1024}MB를 초과합니다.")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드할 수 있습니다.")

    upload_dir = "uploaded_pdfs"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 고유한 파일 이름 생성 (덮어쓰기 방지)
    unique_filename = f"{uuid4()}_{file.filename}"
    file_location = os.path.join(upload_dir, unique_filename)

    try:
        # 파일 저장
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        # OCR 처리 스크립트 호출
        extracted_text = process_pdf_for_text(file_location)
        if not extracted_text:
            raise HTTPException(status_code=400, detail="PDF에서 텍스트를 추출할 수 없습니다.")

        # OCR 결과 데이터베이스에 저장
        new_ocr_document = OcrDocument(
            filename=file.filename,
            file_path=file_location,
            extracted_text=extracted_text,
            uploaded_at=datetime.utcnow()
        )
        db.add(new_ocr_document)
        db.flush()  # ID를 얻기 위해 flush

        # OCR 텍스트에서 문제 파싱
        parsed_questions_data = parse_questions_from_text(extracted_text)
        if not parsed_questions_data:
            # 파싱 실패 시에도 문서는 저장하고, 메시지를 반환할 수 있습니다.
            db.commit()
            return {
                "filename": file.filename,
                "document_id": new_ocr_document.id,
                "message": "PDF 파일은 업로드되었지만, 문제 파싱에 실패했습니다."
            }
            
        parsed_questions = [ParsedQuestion(**q) for q in parsed_questions_data]

        for q_data in parsed_questions:
            new_question = Question(
                ocr_document_id=new_ocr_document.id,
                question_text=q_data.question_text,
                question_type='multiple_choice',  # 현재는 객관식만 지원
                difficulty=q_data.difficulty
            )
            db.add(new_question)
            db.flush()  # ID를 얻기 위해 flush

            for opt_data in q_data.options:
                new_option = Option(
                    question_id=new_question.id,
                    option_text=opt_data.option_text,
                    is_correct=opt_data.is_correct
                )
                db.add(new_option)
        
        db.commit()

        return {"filename": file.filename, "document_id": new_ocr_document.id, "message": "PDF 파일이 성공적으로 업로드 및 처리되었습니다."}
    except Exception as e:
        db.rollback()  # 오류 발생 시 트랜잭션 롤백
        print(f"Error in upload_pdf_for_ocr: {e}")  # 디버깅을 위한 출력
        raise HTTPException(status_code=500, detail=f"파일 업로드 중 오류 발생: {str(e)}")

# OCR 문서 조회 엔드포인트
@app.get("/ocr-documents/{document_id}")
async def get_ocr_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ocr_document = db.query(OcrDocument).filter(OcrDocument.id == document_id).first()
    if not ocr_document:
        raise HTTPException(status_code=404, detail="OCR 문서를 찾을 수 없습니다.")
    return {"filename": ocr_document.filename, "extracted_text": ocr_document.extracted_text, "uploaded_at": ocr_document.uploaded_at}

@app.get("/ocr-documents/{document_id}/questions", response_model=List[QuestionResponse])
async def get_ocr_document_questions(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 해당 OCR 문서에 연결된 문제들을 조회
    questions = db.query(Question).filter(Question.ocr_document_id == document_id).options(
        selectinload(Question.options)
    ).all()
    return questions

@app.get("/ocr-documents", response_model=List[OcrDocumentResponse])
async def get_all_ocr_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 모든 OCR 문서를 조회
    ocr_documents = db.query(OcrDocument).all()
    return ocr_documents


@app.delete("/ocr-documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ocr_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="관리자 권한이 필요합니다.")

    # 1. 문서 조회
    ocr_document = db.query(OcrDocument).filter(OcrDocument.id == document_id).first()
    if not ocr_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="문서를 찾을 수 없습니다.")

    # 2. 연결된 질문 및 보기 삭제
    questions_to_delete = db.query(Question).filter(Question.ocr_document_id == document_id).all()
    for question in questions_to_delete:
        # 보기 삭제
        db.query(Option).filter(Option.question_id == question.id).delete()
        # 질문 삭제
        db.delete(question)
    
    db.flush() # 변경사항을 세션에 반영

    # 3. 실제 PDF 파일 삭제
    if ocr_document.file_path and os.path.exists(ocr_document.file_path):
        os.remove(ocr_document.file_path)

    # 4. 문서 레코드 삭제
    db.delete(ocr_document)
    db.commit()

    return

# TODO: Add more API endpoints for user authentication,
#       question generation, problem solving, etc.

# 관리자 계정 테스트용 엔드포인트
@app.get("/test/admin")
async def test_admin_account(db: Session = Depends(get_db)):
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        return {
            "found": True,
            "username": admin.username,
            "email": admin.email,
            "is_admin": admin.is_admin,
            "password_check": pwd_context.verify("1234", admin.password_hash)
        }
    else:
        return {"found": False, "message": "관리자 계정을 찾을 수 없습니다"}

# 데이터베이스 완전 초기화 엔드포인트  
@app.post("/test/reset-database")
async def reset_database():
    try:
        print("🗑️ 데이터베이스 초기화 시작...")
        
        # 모든 테이블 삭제 후 재생성
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ 테이블 재생성 완료")
        
        # 새 데이터베이스 세션으로 관리자 계정 생성
        db = SessionLocal()
        try:
            hashed_password = pwd_context.hash("1234")
            admin_user = User(
                username="admin",
                email="admin@example.com", 
                password_hash=hashed_password,
                is_admin=True
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("✅ 관리자 계정 생성 완료")
            
            return {
                "success": True,
                "message": "데이터베이스 초기화 및 관리자 계정 생성 완료",
                "admin_info": {
                    "username": "admin", 
                    "password": "1234",
                    "email": "admin@example.com",
                    "user_id": admin_user.id
                }
            }
            
        finally:
            db.close()
            
    except Exception as e:
        return {
            "success": False,
            "message": f"데이터베이스 초기화 실패: {str(e)}"
        }

# 기존 admin 삭제 후 admin2 생성 엔드포인트
@app.post("/test/create-admin2")
async def create_admin2(db: Session = Depends(get_db)):
    try:
        # 기존 admin 계정 삭제
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            db.delete(existing_admin)
            db.commit()
            print("기존 admin 계정 삭제됨")
        
        # admin2 계정이 이미 있는지 확인
        existing_admin2 = db.query(User).filter(User.username == "admin2").first()
        if existing_admin2:
            return {
                "success": True,
                "message": "admin2 계정이 이미 존재합니다",
                "username": "admin2",
                "password": "12342"
            }
        
        # 새 admin2 계정 생성
        hashed_password = pwd_context.hash("12342")
        admin_user = User(
            username="admin2",
            email="admin2@example.com",
            password_hash=hashed_password,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        return {
            "success": True,
            "message": "기존 admin 삭제 후 admin2 계정 생성 완료",
            "username": "admin2",
            "password": "12342",
            "user_id": admin_user.id
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"admin2 계정 생성 실패: {str(e)}"
        }

# ===== 사용자 프로필 관련 API 엔드포인트들 =====
import json

@app.get("/users/me/profile", response_model=UserProfileResponse)
def get_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """현재 사용자의 프로필 정보 조회"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        # 프로필이 없으면 기본값으로 생성
        profile = UserProfile(
            user_id=current_user.id,
            real_name="",
            phone="",
            age_group="",
            education_level="",
            target_certifications="[]",
            bio="",
            daily_goal=5,
            study_time_goal="1시간"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    # target_certifications를 JSON에서 리스트로 변환
    target_certs = []
    if profile.target_certifications:
        try:
            target_certs = json.loads(profile.target_certifications)
        except:
            target_certs = []
    
    return UserProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        real_name=profile.real_name,
        phone=profile.phone,
        age_group=profile.age_group,
        education_level=profile.education_level,
        target_certifications=target_certs,
        bio=profile.bio,
        daily_goal=profile.daily_goal,
        study_time_goal=profile.study_time_goal,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

@app.put("/users/me/profile", response_model=UserProfileResponse)
def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 프로필 정보 업데이트"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        # 프로필이 없으면 생성
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # 업데이트할 필드들 처리
    if profile_update.real_name is not None:
        profile.real_name = profile_update.real_name
    if profile_update.phone is not None:
        profile.phone = profile_update.phone
    if profile_update.age_group is not None:
        profile.age_group = profile_update.age_group
    if profile_update.education_level is not None:
        profile.education_level = profile_update.education_level
    if profile_update.target_certifications is not None:
        profile.target_certifications = json.dumps(profile_update.target_certifications, ensure_ascii=False)
    if profile_update.bio is not None:
        profile.bio = profile_update.bio
    if profile_update.daily_goal is not None:
        profile.daily_goal = profile_update.daily_goal
    if profile_update.study_time_goal is not None:
        profile.study_time_goal = profile_update.study_time_goal
    
    profile.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(profile)
    
    # target_certifications를 JSON에서 리스트로 변환해서 반환
    target_certs = []
    if profile.target_certifications:
        try:
            target_certs = json.loads(profile.target_certifications)
        except:
            target_certs = []
    
    return UserProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        real_name=profile.real_name,
        phone=profile.phone,
        age_group=profile.age_group,
        education_level=profile.education_level,
        target_certifications=target_certs,
        bio=profile.bio,
        daily_goal=profile.daily_goal,
        study_time_goal=profile.study_time_goal,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

@app.get("/users/me/profile/stats")
def get_user_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """사용자 학습 통계 조회 (더미 데이터)"""
    # 실제로는 user_answers, user_progress 테이블에서 계산해야 함
    return {
        "solved_problems": 23,
        "correct_rate": 85,
        "streak_days": 7,
        "total_study_time": 45,
        "overall_progress": 68,
        "weekly_progress": 82,
        "daily_completed": 3
    }

# ===== 관리자 전용 API 엔드포인트들 =====

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """관리자 권한 확인"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    return current_user

@app.get("/admin/users")
def get_all_users(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """모든 사용자 목록 조회 (관리자 전용)"""
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "profile_picture_url": user.profile_picture_url
        }
        for user in users
    ]

class AdminPasswordReset(BaseModel):
    user_id: int
    new_password: str

@app.post("/admin/users/reset-password")
def admin_reset_user_password(
    reset_data: AdminPasswordReset,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """관리자가 사용자 비밀번호 재설정"""
    user = db.query(User).filter(User.id == reset_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    # 새 비밀번호 해시화
    hashed_password = pwd_context.hash(reset_data.new_password)
    user.password_hash = hashed_password
    
    db.commit()
    
    return {
        "success": True,
        "message": f"사용자 '{user.username}'의 비밀번호가 재설정되었습니다",
        "new_password": reset_data.new_password  # 관리자에게만 보여줌
    }

if __name__ == "__main__":
    create_initial_admin_user()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
