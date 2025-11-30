#!/usr/bin/env python3
"""
데이터베이스 초기화 및 리셋 스크립트
기존 데이터를 삭제하고 스키마를 재생성합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database import initialize_database, get_db
from sqlalchemy import text
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def reset_database():
    """데이터베이스 초기화 및 리셋"""
    print("=" * 50)
    print("V2R Database Reset")
    print("=" * 50)

    # 연결 테스트
    db = get_db()
    print("\n1. Testing database connection...")
    if not db.test_connection():
        print("ERROR: Database connection failed!")
        print("Please check your database configuration in .env file")
        return False
    print("✓ Database connection successful")

    # 기존 테이블 삭제
    print("\n2. Dropping existing tables...")
    try:
        with db.get_session() as session:
            # 외래 키 제약 조건 비활성화
            session.execute(text("SET session_replication_role = 'replica';"))
            
            # 모든 테이블 삭제
            session.execute(text("DROP TABLE IF EXISTS cce_check_results CASCADE;"))
            session.execute(text("DROP TABLE IF EXISTS poc_reproductions CASCADE;"))
            session.execute(text("DROP TABLE IF EXISTS poc_metadata CASCADE;"))
            session.execute(text("DROP TABLE IF EXISTS scan_results CASCADE;"))
            session.execute(text("DROP TABLE IF EXISTS reports CASCADE;"))
            
            # 트리거 함수 삭제
            session.execute(text("DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;"))
            
            session.commit()
        print("✓ Existing tables dropped")
    except Exception as e:
        logger.error(f"Error dropping tables: {str(e)}")
        print(f"⚠️  Warning: {str(e)}")
        # 계속 진행

    # 스키마 재생성
    print("\n3. Creating database schema...")
    try:
        if initialize_database():
            print("✓ Database schema created successfully")
        else:
            print("ERROR: Failed to create database schema")
            # 스키마 파일을 직접 실행 시도
            print("\n4. Trying alternative schema creation method...")
            try:
                db = get_db()
                schema_file = Path(__file__).parent.parent.parent / "src" / "database" / "schema.sql"
                if schema_file.exists():
                    # psql을 통한 직접 실행 시도
                    import subprocess
                    result = subprocess.run(
                        ["psql", "-h", db.host, "-p", str(db.port), "-U", db.user, "-d", db.database, "-f", str(schema_file)],
                        env={"PGPASSWORD": db.password},
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print("✓ Database schema created via psql")
                        return True
                    else:
                        print(f"⚠️  psql method failed: {result.stderr}")
                return False
            except Exception as e:
                print(f"⚠️  Alternative method failed: {str(e)}")
                return False
    except Exception as e:
        print(f"ERROR: Database schema creation failed: {str(e)}")
        return False

    print("\n" + "=" * 50)
    print("Database reset completed!")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = reset_database()
    sys.exit(0 if success else 1)

