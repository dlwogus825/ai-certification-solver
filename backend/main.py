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
import json

# JWT 관련 라이브러리
import jwt
from jwt import PyJWTError as JWTError

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
print(f"DEBUG: API Key loaded: {api_key[:20] if api_key else 'None'}...")
if api_key and api_key != "sk-test-key":
    client = anthropic.Anthropic(api_key=api_key)
    print("DEBUG: Anthropic client initialized successfully!")
else:
    client = None  # 개발 모드에서는 AI 기능 비활성화
    print("DEBUG: AI features disabled")

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

# OCR 문서 저장 테이블 모델
class OCRDocument(Base):
    __tablename__ = "ocr_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    extracted_text = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("Question", back_populates="ocr_document", cascade="all, delete-orphan")

# 문제 테이블 모델
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=True)
    ocr_document_id = Column(Integer, ForeignKey("ocr_documents.id"), nullable=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50))  # 예: 'multiple_choice', 'short_answer'
    difficulty = Column(Integer)  # 1-5
    created_at = Column(DateTime, default=datetime.utcnow)

    certification = relationship("Certification", back_populates="questions")
    ocr_document = relationship("OCRDocument", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")

# 보기 테이블 (객관식 문제용)
class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)

    question = relationship("Question", back_populates="options")

# 사용자 답변 테이블 추가
class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option_id = Column(Integer, ForeignKey("options.id"), nullable=True)
    is_correct = Column(Boolean, nullable=False)
    answered_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    question = relationship("Question")
    selected_option = relationship("Option")

# 사용자 학습 기록 테이블 모델
class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    is_correct = Column(Boolean)
    attempt_count = Column(Integer, default=1)
    last_attempt_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    question = relationship("Question")

# AI 문제 생성 관련 모델
class AIGeneratedProblem(Base):
    __tablename__ = "ai_generated_problems"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source_pdf_path = Column(String(255), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # multiple_choice, short_answer, essay, true_false, fill_blank
    difficulty = Column(String(20), nullable=False)  # beginner, intermediate, advanced
    choices = Column(Text, nullable=True)  # JSON 문자열로 객관식 선택지 저장
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    topic = Column(String(100), nullable=True)
    points = Column(Integer, default=1)
    estimated_time = Column(Integer, default=2)  # 예상 소요 시간(분)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")

# 데이터베이스 초기화 함수
def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        create_default_admin(db)
        create_test_user(db)
    finally:
        db.close()

# 테스트용 사용자 생성 함수
def create_test_user(db: Session):
    test_user = db.query(User).filter(User.username == "testuser").first()
    if not test_user:
        test_password = "test123"
        hashed_password = pwd_context.hash(test_password)
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hashed_password,
            is_admin=False
        )
        db.add(test_user)
        db.commit()
        print("테스트 사용자 계정이 생성되었습니다 (username: testuser, password: test123)")

# 기본 관리자 생성 함수
def create_default_admin(db: Session):
    # 관리자 계정이 이미 존재하는지 확인
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        # 관리자 계정 생성
        admin_password = os.getenv("ADMIN_PASSWORD", "1234")
        hashed_password = pwd_context.hash(admin_password)
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=hashed_password,
            is_admin=True
        )
        db.add(admin)
        db.commit()
        print("기본 관리자 계정이 생성되었습니다 (username: admin, password: 1234)")

# 애플리케이션 생성
app = FastAPI(title="AI 자격증 학습 플랫폼")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진 허용 (개발 환경용. 프로덕션에서는 특정 오리진만 허용)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# Rate limiting 설정 (temporarily disabled)
# limiter = Limiter(key_func=get_remote_address)
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# JWT 설정
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")  # 실제 환경에서는 강력한 키 사용
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 데이터베이스 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 비밀번호 검증
def verify_password(plain_password, hashed_password):
    # bcrypt는 72바이트까지만 처리 가능하므로 제한
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)

# 비밀번호 해싱
def get_password_hash(password):
    # bcrypt는 72바이트까지만 처리 가능하므로 제한
    if isinstance(password, str):
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

# 사용자 인증
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

# JWT 토큰 생성
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 현재 사용자 가져오기
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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

# 관리자 권한 확인
async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    return current_user

# 프로필 사진 디렉토리 설정
PROFILE_PICTURES_DIR = "profile_pictures"
os.makedirs(PROFILE_PICTURES_DIR, exist_ok=True)

# 프로필 사진 정적 파일 서빙
app.mount("/profile_pictures", StaticFiles(directory=PROFILE_PICTURES_DIR), name="profile_pictures")

# PDF 업로드 디렉토리 설정
UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 업로드된 PDF 정적 파일 서빙
app.mount("/uploaded_pdfs", StaticFiles(directory=UPLOAD_DIR), name="uploaded_pdfs")

# 유저 등록 요청 모델
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

# 토큰 응답 모델
class Token(BaseModel):
    access_token: str
    token_type: str
    is_admin: bool = False

# 유저 응답 모델
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool = False
    profile_picture_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# 기본 사용자 업데이트 모델
class UserUpdate(BaseModel):
    email: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

# 프로필 업데이트 요청 모델
class UserProfileUpdate(BaseModel):
    real_name: Optional[str] = None
    phone: Optional[str] = None
    age_group: Optional[str] = None
    education_level: Optional[str] = None
    target_certifications: Optional[List[str]] = None
    bio: Optional[str] = None
    daily_goal: Optional[int] = None
    study_time_goal: Optional[str] = None

# 프로필 응답 모델
class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    real_name: Optional[str] = None
    phone: Optional[str] = None
    age_group: Optional[str] = None
    education_level: Optional[str] = None
    target_certifications: Optional[List[str]] = None
    bio: Optional[str] = None
    daily_goal: int = 5
    study_time_goal: str = "1시간"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 질문 응답 모델
class OptionResponse(BaseModel):
    id: int
    option_text: str
    is_correct: bool

    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    id: int
    question_text: str
    question_type: Optional[str] = None
    difficulty: Optional[int] = None
    options: List[OptionResponse] = []

    class Config:
        from_attributes = True

# AI 문제 해설 응답 모델
class ExplainResponse(BaseModel):
    question_id: int
    question_text: str
    explanation: str

# 문제 제출 요청 모델
class SubmitAnswerRequest(BaseModel):
    question_id: int
    selected_option_id: int

# 문제 제출 응답 모델
class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    message: str
    correct_option_id: Optional[int] = None

# OCR 문서 응답 모델
class OCRDocumentResponse(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime
    question_count: Optional[int] = 0

    class Config:
        from_attributes = True

# 비밀번호 재설정 요청 모델
class PasswordResetRequest(BaseModel):
    new_password: str

# 비밀번호 재설정 요청 모델 (관리자용)
class AdminPasswordResetRequest(BaseModel):
    username: str
    new_password: str

# 사용자 목록 응답 모델
class UserListResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

# 프로필 통계 모델
class ProfileStatsResponse(BaseModel):
    total_problems_solved: int = 0
    correct_answers: int = 0
    accuracy_rate: float = 0.0
    study_streak: int = 0
    total_study_time: str = "0시간 0분"
    average_daily_problems: float = 0.0
    target_achievement_rate: float = 0.0

# 비밀번호 재설정 모델
class ResetPasswordRequest(BaseModel):
    username: str
    email: str

class ResetPasswordResponse(BaseModel):
    message: str
    temporary_password: str

# 라우트
@app.get("/")
def read_root():
    return {"message": "AI 자격증 학습 플랫폼 API에 오신 것을 환영합니다."}

# 회원가입
@app.post("/register", response_model=UserResponse)
async def register(user: UserRegister, db: Session = Depends(get_db)):
    # 사용자명 중복 확인
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자명입니다.")
    
    # 이메일 중복 확인
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
    
    # 새 사용자 생성
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        is_admin=new_user.is_admin,
        profile_picture_url=new_user.profile_picture_url,
        created_at=new_user.created_at
    )

# 로그인
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 사용자명 또는 비밀번호입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "is_admin": user.is_admin}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "is_admin": user.is_admin}

# 현재 사용자 정보
@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_admin=current_user.is_admin,
        profile_picture_url=current_user.profile_picture_url,
        created_at=current_user.created_at
    )

# 사용자 정보 수정
@app.put("/users/me", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 이메일 변경
    if user_update.email:
        # 이메일 중복 확인
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다.")
        current_user.email = user_update.email
    
    # 비밀번호 변경
    if user_update.current_password and user_update.new_password:
        # 현재 비밀번호 확인
        if not verify_password(user_update.current_password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="현재 비밀번호가 일치하지 않습니다.")
        # 새 비밀번호 설정
        current_user.password_hash = get_password_hash(user_update.new_password)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_admin=current_user.is_admin,
        profile_picture_url=current_user.profile_picture_url,
        created_at=current_user.created_at
    )

# 프로필 사진 업로드
@app.post("/users/me/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 파일 확장자 확인
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif"}
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="허용되지 않는 파일 형식입니다.")
    
    # 파일 크기 확인 (5MB 제한)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="파일 크기가 5MB를 초과합니다.")
    
    # 기존 프로필 사진 삭제
    if current_user.profile_picture_url:
        old_file_path = current_user.profile_picture_url.replace("/profile_pictures/", "")
        old_full_path = os.path.join(PROFILE_PICTURES_DIR, old_file_path)
        if os.path.exists(old_full_path):
            os.remove(old_full_path)
    
    # 새 파일명 생성
    file_id = str(uuid4())
    new_filename = f"{file_id}{file_extension}"
    file_path = os.path.join(PROFILE_PICTURES_DIR, new_filename)
    
    # 파일 저장
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # DB 업데이트
    current_user.profile_picture_url = f"/profile_pictures/{new_filename}"
    db.commit()
    
    return {"message": "프로필 사진이 업로드되었습니다.", "url": current_user.profile_picture_url}

# 프로필 정보 조회
@app.get("/users/me/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        # 프로필이 없으면 기본값으로 생성
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    # target_certifications를 JSON에서 리스트로 변환
    import json
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

# 프로필 정보 수정
@app.put("/users/me/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # 업데이트 가능한 필드 설정
    update_data = profile_update.dict(exclude_unset=True)
    
    # target_certifications 처리
    if "target_certifications" in update_data:
        import json
        update_data["target_certifications"] = json.dumps(update_data["target_certifications"], ensure_ascii=False)
    
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    profile.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(profile)
    
    # 응답 준비
    import json
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

# 전체 문제 목록 조회
@app.get("/questions", response_model=List[QuestionResponse])
async def get_questions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    questions = db.query(Question).options(selectinload(Question.options)).offset(skip).limit(limit).all()
    return questions

# AI 문제 해설 생성
@app.post("/explain/{question_id}", response_model=ExplainResponse)
async def explain_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 문제 조회
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")
    
    # 개발 모드에서는 미리 정의된 해설 반환
    if not client:
        explanation = f"""이 문제는 {question.question_text[:50]}... 에 대한 문제입니다.
        
핵심 포인트:
1. 문제를 꼼꼼히 읽고 핵심 키워드를 파악하세요.
2. 각 선택지를 신중히 검토하여 정답을 찾으세요.
3. 관련 개념을 복습하면 도움이 됩니다.

(개발 모드: AI 해설 기능은 Anthropic API 키가 설정되면 사용 가능합니다.)"""
    else:
        # Claude API를 사용하여 해설 생성
        try:
            # 문제와 선택지 정보 수집
            options = db.query(Option).filter(Option.question_id == question_id).all()
            options_text = "\n".join([f"{i+1}. {opt.option_text}" for i, opt in enumerate(options)])
            correct_option = next((opt for opt in options if opt.is_correct), None)
            
            prompt = f"""다음 문제에 대한 구조화된 해설을 마크다운 형식으로 작성해주세요:

문제: {question.question_text}

선택지:
{options_text}

정답: {correct_option.option_text if correct_option else "정답 정보 없음"}

다음 형식으로 해설을 작성해주세요:

## 📌 정답

**정답은 {correct_option.option_text if correct_option else '정답 정보 없음'}입니다.**

## ✅ 정답 해설

(정답이 맞는 이유를 명확하게 설명)

## ❌ 오답 해설

### 1번 선택지
- (틀린 이유 설명)

### 2번 선택지  
- (틀린 이유 설명)

(나머지 선택지도 동일하게)

## 💡 핵심 개념

- **개념 1**: 설명
- **개념 2**: 설명

## 📚 추가 학습 포인트

1. 첫 번째 포인트
2. 두 번째 포인트

## 🔍 실무 팁 (있다면)

- 실무에서 이렇게 활용됩니다

---

마크다운 문법을 활용하여 가독성 높게 작성해주세요."""

            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.3,  # 낮은 온도로 일관된 해설 생성
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            explanation = response.content[0].text
        except Exception as e:
            explanation = f"AI 해설 생성 중 오류가 발생했습니다: {str(e)}"
    
    return ExplainResponse(
        question_id=question_id,
        question_text=question.question_text,
        explanation=explanation
    )

# 사용자 답변 제출
@app.post("/api/v1/problems/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(
    request: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 문제 존재 확인
    question = db.query(Question).filter(Question.id == request.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")
    
    # 선택지 존재 확인
    selected_option = db.query(Option).filter(
        Option.id == request.selected_option_id,
        Option.question_id == request.question_id
    ).first()
    if not selected_option:
        raise HTTPException(status_code=404, detail="선택지를 찾을 수 없습니다.")
    
    # 정답 확인
    is_correct = selected_option.is_correct
    
    # 사용자 답변 기록
    user_answer = UserAnswer(
        user_id=current_user.id,
        question_id=request.question_id,
        selected_option_id=request.selected_option_id,
        is_correct=is_correct
    )
    db.add(user_answer)
    
    # 학습 진도 업데이트
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.question_id == request.question_id
    ).first()
    
    if progress:
        progress.attempt_count += 1
        progress.is_correct = is_correct
        progress.last_attempt_at = datetime.utcnow()
    else:
        progress = UserProgress(
            user_id=current_user.id,
            question_id=request.question_id,
            is_correct=is_correct
        )
        db.add(progress)
    
    db.commit()
    
    # 정답 ID 찾기
    correct_option = db.query(Option).filter(
        Option.question_id == request.question_id,
        Option.is_correct == True
    ).first()
    
    return SubmitAnswerResponse(
        is_correct=is_correct,
        message="정답입니다!" if is_correct else "틀렸습니다. 다시 시도해보세요.",
        correct_option_id=correct_option.id if correct_option else None
    )

# PDF 업로드 및 OCR 처리 (관리자 전용)
@app.post("/admin/upload-pdf-for-ocr")
async def upload_pdf_for_ocr(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    # 파일 확장자 확인
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")
    
    # 파일 저장
    file_id = str(uuid4())
    file_name = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    
    try:
        # OCR 처리
        print(f"Starting OCR for file: {file_path}")
        extracted_text = process_pdf_for_text(file_path)
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="PDF에서 텍스트를 추출할 수 없습니다.")
        
        # OCR 문서 저장
        ocr_doc = OCRDocument(
            filename=file.filename,
            file_path=file_path,
            extracted_text=extracted_text
        )
        db.add(ocr_doc)
        db.commit()
        db.refresh(ocr_doc)
        
        # AI를 사용한 문제 파싱
        print(f"Parsing questions from extracted text...")
        questions_data = parse_questions_from_text(extracted_text)
        
        if not questions_data:
            return {
                "message": "OCR은 성공했지만 문제를 파싱할 수 없습니다.",
                "document_id": ocr_doc.id,
                "extracted_text_preview": extracted_text[:500] + "...",
                "questions_count": 0
            }
        
        # 파싱된 문제들을 데이터베이스에 저장
        saved_questions = 0
        print(f"DEBUG: Parsed {len(questions_data)} questions from Claude")
        for i, q_data in enumerate(questions_data):
            try:
                print(f"DEBUG: Processing question {i+1}: {q_data}")
                print(f"DEBUG: Question has {len(q_data.get('options', []))} options")
                # 문제 생성
                question = Question(
                    ocr_document_id=ocr_doc.id,
                    question_text=q_data['question_text'],
                    question_type='multiple_choice'
                )
                db.add(question)
                db.flush()  # ID를 얻기 위해 flush
                
                # 선택지 생성
                options_list = q_data.get('options', [])
                print(f"DEBUG: Options for question {i+1}: {options_list}")
                
                for j, option_data in enumerate(options_list):
                    print(f"DEBUG: Processing option {j+1}: {option_data}")
                    
                    # 옵션 데이터 구조 확인 및 안전한 접근
                    if isinstance(option_data, dict):
                        option_text = option_data.get('option_text', '')
                        is_correct = option_data.get('is_correct', False)
                    else:
                        # 만약 option_data가 문자열이라면
                        option_text = str(option_data) if option_data else ''
                        is_correct = False
                    
                    print(f"DEBUG: Creating option with text='{option_text}', correct={is_correct}")
                    
                    option = Option(
                        question_id=question.id,
                        option_text=option_text,
                        is_correct=is_correct
                    )
                    db.add(option)
                
                saved_questions += 1
            except Exception as e:
                print(f"Error saving question: {e}")
                continue
        
        db.commit()
        
        return {
            "message": "PDF 업로드 및 OCR 처리가 완료되었습니다.",
            "document_id": ocr_doc.id,
            "filename": file.filename,
            "questions_parsed": len(questions_data),
            "questions_saved": saved_questions,
            "extracted_text_preview": extracted_text[:500] + "..."
        }
        
    except Exception as e:
        # 에러 발생 시 업로드된 파일 삭제
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"OCR 처리 중 오류가 발생했습니다: {str(e)}")

# OCR 문서 목록 조회
@app.get("/ocr-documents", response_model=List[OCRDocumentResponse])
async def get_ocr_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    documents = db.query(OCRDocument).order_by(OCRDocument.uploaded_at.desc()).all()
    
    # 각 문서의 문제 개수 계산
    result = []
    for doc in documents:
        question_count = db.query(Question).filter(Question.ocr_document_id == doc.id).count()
        result.append(OCRDocumentResponse(
            id=doc.id,
            filename=doc.filename,
            uploaded_at=doc.uploaded_at,
            question_count=question_count
        ))
    
    return result

# 특정 OCR 문서의 문제 목록 조회
@app.get("/ocr-documents/{document_id}/questions", response_model=List[QuestionResponse])
async def get_document_questions(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 문서 존재 확인
    document = db.query(OCRDocument).filter(OCRDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
    
    # 해당 문서의 문제들 조회
    questions = db.query(Question).filter(
        Question.ocr_document_id == document_id
    ).options(selectinload(Question.options)).all()
    
    return questions

# 특정 OCR 문서 조회
@app.get("/ocr-documents/{document_id}")
async def get_ocr_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(OCRDocument).filter(OCRDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
    
    question_count = db.query(Question).filter(Question.ocr_document_id == document_id).count()
    
    return {
        "id": document.id,
        "filename": document.filename,
        "uploaded_at": document.uploaded_at,
        "question_count": question_count
    }

# OCR 문서 삭제 (관리자 전용)
@app.delete("/ocr-documents/{document_id}")
async def delete_ocr_document(
    document_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    # 문서 조회
    document = db.query(OCRDocument).filter(OCRDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
    
    # 파일 삭제
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # 데이터베이스에서 삭제 (관련 문제들도 cascade로 자동 삭제됨)
    db.delete(document)
    db.commit()
    
    return {"message": "문서가 성공적으로 삭제되었습니다."}

# 관리자 전용: 전체 사용자 목록 조회
@app.get("/admin/users", response_model=List[UserListResponse])
async def get_all_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return users

# 관리자 전용: 사용자 비밀번호 재설정
@app.post("/admin/users/reset-password")
async def admin_reset_user_password(
    request: AdminPasswordResetRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    # 사용자 조회
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    # 비밀번호 재설정
    user.password_hash = get_password_hash(request.new_password)
    db.commit()
    
    return {"message": f"{user.username}의 비밀번호가 재설정되었습니다."}

# 회원 탈퇴
@app.delete("/users/me")
async def delete_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 관리자 계정은 삭제 불가
    if current_user.is_admin:
        raise HTTPException(status_code=403, detail="관리자 계정은 삭제할 수 없습니다.")
    
    # 프로필 사진 삭제
    if current_user.profile_picture_url:
        file_path = current_user.profile_picture_url.replace("/profile_pictures/", "")
        full_path = os.path.join(PROFILE_PICTURES_DIR, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
    
    # 사용자 삭제 (관련 데이터는 cascade로 자동 삭제)
    db.delete(current_user)
    db.commit()
    
    return {"message": "회원 탈퇴가 완료되었습니다."}

# 프로필 통계 조회 (실제 데이터)
@app.get("/users/me/profile/stats", response_model=ProfileStatsResponse)
async def get_profile_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 전체 문제 풀이 수
    total_problems_solved = db.query(UserAnswer).filter(
        UserAnswer.user_id == current_user.id
    ).count()
    
    # 정답 수
    correct_answers = db.query(UserAnswer).filter(
        UserAnswer.user_id == current_user.id,
        UserAnswer.is_correct == True
    ).count()
    
    # 정답률 계산
    accuracy_rate = 0.0
    if total_problems_solved > 0:
        accuracy_rate = round((correct_answers / total_problems_solved) * 100, 1)
    
    # 연속 학습일 계산 (최근 7일간 활동한 날짜 수)
    from sqlalchemy import func
    from datetime import datetime, timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    study_days = db.query(func.date(UserAnswer.answered_at)).filter(
        UserAnswer.user_id == current_user.id,
        UserAnswer.answered_at >= seven_days_ago
    ).distinct().count()
    
    # 일일 평균 문제 풀이 수
    user_created_days = (datetime.utcnow() - current_user.created_at).days or 1
    average_daily_problems = round(total_problems_solved / user_created_days, 1)
    
    # 목표 달성률 (사용자 프로필의 daily_goal 기준)
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    daily_goal = profile.daily_goal if profile else 5
    
    # 오늘 푼 문제 수
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_problems = db.query(UserAnswer).filter(
        UserAnswer.user_id == current_user.id,
        UserAnswer.answered_at >= today_start
    ).count()
    
    target_achievement_rate = round((today_problems / daily_goal) * 100, 1) if daily_goal > 0 else 0.0
    
    # 총 학습 시간 (문제당 평균 2분으로 추정)
    total_minutes = total_problems_solved * 2
    hours = total_minutes // 60
    minutes = total_minutes % 60
    total_study_time = f"{hours}시간 {minutes}분"
    
    return ProfileStatsResponse(
        total_problems_solved=total_problems_solved,
        correct_answers=correct_answers,
        accuracy_rate=accuracy_rate,
        study_streak=study_days,
        total_study_time=total_study_time,
        average_daily_problems=average_daily_problems,
        target_achievement_rate=target_achievement_rate
    )

# 비밀번호 재설정 (임시 비밀번호 발급)
@app.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    # 사용자 조회
    user = db.query(User).filter(
        User.username == request.username,
        User.email == request.email
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="일치하는 사용자 정보를 찾을 수 없습니다."
        )
    
    # 임시 비밀번호 생성 (8자리 랜덤)
    temp_password = secrets.token_urlsafe(6)[:8]
    
    # 비밀번호 업데이트
    user.password_hash = get_password_hash(temp_password)
    db.commit()
    
    return ResetPasswordResponse(
        message="임시 비밀번호가 발급되었습니다. 로그인 후 반드시 비밀번호를 변경하세요.",
        temporary_password=temp_password
    )

# 테스트용 엔드포인트들
@app.get("/test/admin")
async def test_admin(current_user: User = Depends(get_current_admin_user)):
    return {"message": f"관리자 {current_user.username}님, 환영합니다!"}

@app.post("/test/reset-database")
async def reset_database(current_user: User = Depends(get_current_admin_user)):
    """데이터베이스 초기화 (테스트용)"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    init_db()
    return {"message": "데이터베이스가 초기화되었습니다."}

# Pydantic 모델
class ProblemGenerationRequest(BaseModel):
    text: str
    settings: dict

class GeneratedProblem(BaseModel):
    question: str
    type: str
    difficulty: str
    choices: Optional[List[str]] = None
    answer: str
    explanation: Optional[str] = None
    topic: Optional[str] = None
    points: int = 1
    estimatedTime: int = 2

# PDF 업로드 엔드포인트
@app.post("/api/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """PDF 파일 업로드"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")
    
    if file.size > 10 * 1024 * 1024:  # 10MB 제한
        raise HTTPException(status_code=400, detail="파일 크기는 10MB 이하여야 합니다.")
    
    # 고유한 파일명 생성
    file_id = str(uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{file_id}{file_extension}"
    
    # 업로드된 PDF 저장 디렉토리
    upload_dir = "uploaded_pdfs"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, unique_filename)
    
    # 파일 저장
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # 데이터베이스에 기록
    ocr_doc = OCRDocument(
        filename=file.filename,
        file_path=file_path,
        extracted_text=""  # 텍스트 추출은 별도 엔드포인트에서
    )
    db.add(ocr_doc)
    db.commit()
    db.refresh(ocr_doc)
    
    return {"id": ocr_doc.id, "filename": file.filename, "status": "uploaded"}

# 텍스트 추출 엔드포인트
@app.post("/api/extract-text/{pdf_id}")
async def extract_text(
    pdf_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """PDF에서 텍스트 추출"""
    ocr_doc = db.query(OCRDocument).filter(OCRDocument.id == pdf_id).first()
    if not ocr_doc:
        raise HTTPException(status_code=404, detail="PDF 문서를 찾을 수 없습니다.")
    
    try:
        # OCR 처리를 통해 텍스트 추출
        extracted_text = process_pdf_for_text(ocr_doc.file_path)
        
        # 데이터베이스 업데이트
        ocr_doc.extracted_text = extracted_text
        db.commit()
        
        return {"content": extracted_text, "length": len(extracted_text)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"텍스트 추출 실패: {str(e)}")

# AI 문제 생성 엔드포인트
@app.post("/api/generate-problems")
async def generate_problems(
    request: ProblemGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI를 사용하여 문제 생성"""
    if not client:
        raise HTTPException(status_code=503, detail="AI 서비스를 사용할 수 없습니다.")
    
    try:
        # AI 프롬프트 구성
        prompt = create_problem_generation_prompt(request.text, request.settings)
        
        # Claude API 호출
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4000,
            temperature=0.3,  # 일관된 결과를 위한 낮은 온도 설정
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # 응답 파싱
        problems = parse_ai_response(message.content[0].text)
        
        # 데이터베이스에 저장
        saved_problems = []
        for i, problem_data in enumerate(problems):
            try:
                ai_problem = AIGeneratedProblem(
                    user_id=current_user.id,
                    source_pdf_path="",  # PDF 경로는 별도로 관리
                    question_text=problem_data.get('question', f'문제 {i+1}'),
                    question_type=problem_data.get('type', 'multiple_choice'),
                    difficulty=problem_data.get('difficulty', 'intermediate'),
                    choices=json.dumps(problem_data.get('choices', [])) if problem_data.get('choices') else None,
                    correct_answer=str(problem_data.get('answer', '')),
                    explanation=problem_data.get('explanation', ''),
                    topic=problem_data.get('topic', ''),
                    points=problem_data.get('points', 1),
                    estimated_time=problem_data.get('estimatedTime', problem_data.get('estimated_time', 2))
                )
                db.add(ai_problem)
                saved_problems.append(problem_data)
            except Exception as e:
                print(f"Error saving problem {i+1}: {str(e)}")
                # 개별 문제 저장 실패 시 해당 문제만 스킵하고 계속 진행
                continue
        
        db.commit()
        
        return saved_problems
        
    except Exception as e:
        print(f"AI 문제 생성 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"문제 생성 실패: {str(e)}")

def create_problem_generation_prompt(text: str, settings: dict) -> str:
    """AI 문제 생성을 위한 프롬프트 생성"""
    question_types = settings.get('questionTypes', ['multiple_choice'])
    difficulty = settings.get('difficulty', 'intermediate')
    question_count = settings.get('questionCount', 20)
    language = settings.get('language', 'ko')
    include_explanations = settings.get('includeExplanations', True)
    custom_prompt = settings.get('customPrompt', '')
    
    type_descriptions = {
        'multiple_choice': '4지선다 객관식 문제',
        'short_answer': '단답형 문제',
        'essay': '서술형 문제',
        'true_false': 'O/X 문제',
        'fill_blank': '빈칸 채우기 문제'
    }
    
    difficulty_descriptions = {
        'beginner': '초급 (기본 개념 이해)',
        'intermediate': '중급 (응용 및 분석)',
        'advanced': '고급 (종합 및 평가)'
    }
    
    selected_types = [type_descriptions[t] for t in question_types if t in type_descriptions]
    
    prompt = f"""
다음 텍스트를 바탕으로 {question_count}개의 학습 문제를 생성해주세요.

**텍스트 내용:**
{text[:3000]}

**문제 생성 요구사항:**
- 문제 유형: {', '.join(selected_types)}
- 난이도: {difficulty_descriptions[difficulty]}
- 언어: {'한국어' if language == 'ko' else language}
- 해설 포함: {'네' if include_explanations else '아니오'}

**추가 요구사항:**
{custom_prompt if custom_prompt else '없음'}

**출력 형식 (JSON):**
```json
[
  {{
    "question": "문제 내용",
    "type": "문제_유형",
    "difficulty": "{difficulty}",
    "choices": ["선택지1", "선택지2", "선택지3", "선택지4"],
    "answer": "정답 또는 정답 인덱스",
    "explanation": "해설",
    "topic": "주제",
    "points": 1,
    "estimatedTime": 2
  }}
]
```

주의사항:
1. 객관식 문제의 경우 answer는 정답 선택지의 인덱스 (0, 1, 2, 3)
2. 단답형/서술형의 경우 answer는 정답 텍스트
3. O/X 문제의 경우 answer는 true 또는 false
4. 빈칸 채우기의 경우 question에 ___로 빈칸 표시
5. 모든 문제는 제공된 텍스트 내용을 기반으로 생성
6. 문제별로 적절한 주제(topic) 설정

JSON 배열 형태로만 응답해주세요.
"""
    
    return prompt

def parse_ai_response(response_text: str) -> List[dict]:
    """AI 응답을 파싱하여 문제 리스트 반환"""
    import json
    import re
    
    print(f"DEBUG: AI 응답 파싱 시작, 응답 길이: {len(response_text)}")
    print(f"DEBUG: AI 응답 미리보기: {response_text[:500]}")
    
    try:
        # JSON 코드 블록에서 내용 추출
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
            print("DEBUG: JSON 코드 블록에서 내용 추출 성공")
        else:
            # JSON 코드 블록이 없으면 전체 텍스트에서 JSON 배열 찾기
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                print("DEBUG: 전체 텍스트에서 JSON 배열 추출 성공")
            else:
                print("DEBUG: JSON 형식을 찾을 수 없음")
                raise ValueError("JSON 형식을 찾을 수 없습니다.")
        
        print(f"DEBUG: 추출된 JSON 텍스트: {json_text[:200]}...")
        problems = json.loads(json_text)
        print(f"DEBUG: JSON 파싱 성공, 문제 개수: {len(problems)}")
        
        # 데이터 검증 및 정리
        validated_problems = []
        for i, problem in enumerate(problems):
            print(f"DEBUG: 문제 {i+1} 검증 중: {problem.get('question', 'NO QUESTION')[:50]}...")
            validated_problem = {
                'question': problem.get('question', ''),
                'type': problem.get('type', 'multiple_choice'),
                'difficulty': problem.get('difficulty', 'intermediate'),
                'answer': problem.get('answer', ''),
                'explanation': problem.get('explanation', ''),
                'topic': problem.get('topic', ''),
                'points': problem.get('points', 1),
                'estimatedTime': problem.get('estimatedTime', 2)
            }
            
            if problem.get('choices'):
                validated_problem['choices'] = problem['choices']
                print(f"DEBUG: 문제 {i+1} 선택지 개수: {len(problem['choices'])}")
                
            validated_problems.append(validated_problem)
        
        print(f"DEBUG: 검증 완료, 최종 문제 개수: {len(validated_problems)}")
        return validated_problems
        
    except Exception as e:
        print(f"DEBUG: AI 응답 파싱 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        # 파싱 실패 시 더미 데이터 반환 (개발/테스트용)
        return [
            {
                "question": "파싱 오류로 인한 더미 문제입니다.",
                "type": "multiple_choice",
                "difficulty": "intermediate",
                "choices": ["선택지 1", "선택지 2", "선택지 3", "선택지 4"],
                "answer": 0,
                "explanation": f"AI 응답 파싱 중 오류 발생: {str(e)}",
                "topic": "오류",
                "points": 1,
                "estimatedTime": 2
            }
        ]

# 테스트 엔드포인트
@app.get("/test/auth")
async def test_auth(current_user: User = Depends(get_current_user)):
    """인증 테스트 엔드포인트"""
    return {"message": "인증 성공", "user": current_user.username}

# 인증 없이 테스트할 수 있는 PDF 업로드 엔드포인트
@app.post("/api/upload-pdf-test")
async def upload_pdf_test(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """테스트용 PDF 파일 업로드 (인증 없음)"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")
    
    if file.size > 10 * 1024 * 1024:  # 10MB 제한
        raise HTTPException(status_code=400, detail="파일 크기는 10MB 이하여야 합니다.")
    
    # 고유한 파일명 생성
    file_id = str(uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{file_id}{file_extension}"
    
    # 업로드된 PDF 저장 디렉토리
    upload_dir = "uploaded_pdfs"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, unique_filename)
    
    # 파일 저장
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return {"id": 999, "filename": file.filename, "status": "uploaded", "message": "테스트용 업로드 성공"}

# 테스트용 더미 문제 생성 엔드포인트
@app.post("/api/generate-problems-test")
async def generate_problems_test(request: ProblemGenerationRequest):
    """테스트용 더미 문제 생성"""
    dummy_problems = [
        {
            "question": "다음 중 Python의 데이터 타입이 아닌 것은?",
            "type": "multiple_choice",
            "difficulty": "intermediate",
            "choices": ["int", "str", "bool", "array"],
            "answer": 3,
            "explanation": "Python에서는 array가 아닌 list를 사용합니다.",
            "topic": "Python 기초",
            "points": 2,
            "estimatedTime": 3
        },
        {
            "question": "변수란 무엇인가요?",
            "type": "essay",
            "difficulty": "beginner",
            "answer": "변수는 데이터를 저장하는 공간입니다.",
            "explanation": "변수는 프로그램에서 데이터를 임시로 저장하고 참조할 수 있는 메모리 공간을 의미합니다.",
            "topic": "프로그래밍 개념",
            "points": 3,
            "estimatedTime": 5
        },
        {
            "question": "Python에서 리스트는 순서가 있는 자료구조이다.",
            "type": "true_false",
            "difficulty": "beginner",
            "answer": True,
            "explanation": "Python의 리스트는 순서가 있는(ordered) 컬렉션입니다.",
            "topic": "Python 자료구조",
            "points": 1,
            "estimatedTime": 1
        }
    ]
    return dummy_problems

@app.post("/test/create-admin2")
async def create_test_admin(db: Session = Depends(get_db)):
    """테스트용 추가 관리자 계정 생성"""
    existing = db.query(User).filter(User.username == "admin2").first()
    if existing:
        return {"message": "admin2 계정이 이미 존재합니다."}
    
    admin2 = User(
        username="admin2",
        email="admin2@example.com",
        password_hash=get_password_hash("admin2"),
        is_admin=True
    )
    db.add(admin2)
    db.commit()
    return {"message": "admin2 계정이 생성되었습니다. (비밀번호: admin2)"}

# 애플리케이션 시작 시 데이터베이스 초기화
if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)