"""
설정 관리 모듈
환경 변수 및 설정 파일 로드
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# AWS 설정
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")

# 데이터베이스 설정
# Docker 환경에서는 'postgres' 서비스 이름 사용
DB_HOST = os.getenv("DB_HOST", "localhost")  # Docker: "postgres", 로컬: "localhost"
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "v2r")
DB_USER = os.getenv("DB_USER", "v2r")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# S3 설정
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")
S3_EVIDENCE_PREFIX = os.getenv("S3_EVIDENCE_PREFIX", "evidence/")

# LLM 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-nano")

# 스캐닝 설정
SCAN_TIMEOUT = int(os.getenv("SCAN_TIMEOUT", "300"))  # 5분
MAX_CONCURRENT_SCANS = int(os.getenv("MAX_CONCURRENT_SCANS", "5"))

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent

