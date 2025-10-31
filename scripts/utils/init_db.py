#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
스키마를 생성하고 초기 데이터를 설정합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database import initialize_database, get_db
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    """데이터베이스 초기화 실행"""
    print("=" * 50)
    print("V2R Database Initialization")
    print("=" * 50)

    # 연결 테스트
    db = get_db()
    print("\n1. Testing database connection...")
    if not db.test_connection():
        print("ERROR: Database connection failed!")
        print("Please check your database configuration in .env file")
        return False
    print("✓ Database connection successful")

    # 스키마 생성
    print("\n2. Creating database schema...")
    if initialize_database():
        print("✓ Database schema created successfully")
    else:
        print("ERROR: Failed to create database schema")
        return False

    print("\n" + "=" * 50)
    print("Database initialization completed!")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

