#!/usr/bin/env python3
"""
데이터베이스 마이그레이션 스크립트
이메일 인증 관련 컬럼 추가
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    # 데이터베이스 파일 경로
    db_path = "ai_cert_platform.db"
    
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found!")
        return False
    
    try:
        # 데이터베이스 연결
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 현재 users 테이블의 컬럼 확인
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        print("Current columns in users table:", columns)
        
        # 이메일 인증 관련 컬럼 추가
        migrations = []
        
        if 'is_email_verified' not in columns:
            migrations.append(("is_email_verified", "ALTER TABLE users ADD COLUMN is_email_verified BOOLEAN DEFAULT 0"))
        
        if 'email_verification_token' not in columns:
            migrations.append(("email_verification_token", "ALTER TABLE users ADD COLUMN email_verification_token VARCHAR(255)"))
        
        if 'email_verification_sent_at' not in columns:
            migrations.append(("email_verification_sent_at", "ALTER TABLE users ADD COLUMN email_verification_sent_at TIMESTAMP"))
        
        # 마이그레이션 실행
        if migrations:
            print("\nExecuting migrations...")
            for column_name, query in migrations:
                try:
                    cursor.execute(query)
                    print(f"✓ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    print(f"✗ Failed to add column {column_name}: {e}")
            
            # 변경사항 커밋
            conn.commit()
            print("\nMigration completed successfully!")
            
            # 기존 사용자들의 이메일 인증 상태를 True로 설정 (기존 사용자는 인증된 것으로 간주)
            cursor.execute("UPDATE users SET is_email_verified = 1 WHERE is_email_verified IS NULL OR is_email_verified = 0")
            affected_rows = cursor.rowcount
            conn.commit()
            print(f"Updated {affected_rows} existing users to verified status.")
        else:
            print("\nNo migrations needed - all columns already exist.")
        
        # 최종 테이블 구조 확인
        cursor.execute("PRAGMA table_info(users)")
        final_columns = cursor.fetchall()
        print("\nFinal users table structure:")
        for col in final_columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # 연결 종료
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("AI Cert Platform Database Migration")
    print("===================================")
    
    if migrate_database():
        print("\n✅ Database migration successful!")
        print("You can now restart the server.")
    else:
        print("\n❌ Database migration failed!")
        print("Please check the error messages above.")