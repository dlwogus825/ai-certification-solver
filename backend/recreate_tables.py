#!/usr/bin/env python3
"""
데이터베이스 테이블 재생성 스크립트
SQLAlchemy 모델과 동기화
"""

import os
import shutil
from datetime import datetime
from sqlalchemy import create_engine
from main import Base, User, UserProfile, init_db, create_default_admin

def backup_database():
    """데이터베이스 백업 생성"""
    db_path = "ai_cert_platform.db"
    if os.path.exists(db_path):
        backup_path = f"ai_cert_platform_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_path, backup_path)
        print(f"✓ Database backed up to: {backup_path}")
        return backup_path
    return None

def recreate_database():
    """데이터베이스 재생성"""
    try:
        # 백업 생성
        backup_path = backup_database()
        
        # 기존 데이터베이스 삭제
        db_path = "ai_cert_platform.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✓ Old database removed")
        
        # 새 데이터베이스 생성
        print("\nCreating new database with updated schema...")
        
        # 엔진 생성
        engine = create_engine("sqlite:///./ai_cert_platform.db")
        
        # 모든 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully")
        
        # 기본 관리자 계정 생성
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # init_db 함수 호출하여 기본 관리자 생성
            create_default_admin(db)
            print("✓ Default admin account created")
        finally:
            db.close()
        
        print("\n✅ Database recreation completed successfully!")
        print("\nDefault credentials:")
        print("  Username: admin")
        print("  Password: 1234")
        
        if backup_path:
            print(f"\nYour old data is backed up at: {backup_path}")
            print("You may need to manually migrate data from the backup if needed.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during database recreation: {e}")
        return False

if __name__ == "__main__":
    print("AI Cert Platform Database Recreation")
    print("====================================")
    print("⚠️  WARNING: This will delete and recreate the database!")
    print("⚠️  All existing data will be backed up but not automatically restored.")
    
    response = input("\nDo you want to continue? (yes/no): ")
    
    if response.lower() == 'yes':
        if recreate_database():
            print("\nYou can now restart the server.")
        else:
            print("\nPlease check the error messages above.")
    else:
        print("\nOperation cancelled.")