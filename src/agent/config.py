"""
Agent 설정 관리
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# .env 파일 로드
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)  # override=True: 환경 변수가 이미 설정되어 있어도 .env 파일 값으로 덮어씀
    logger.info(f".env 파일 로드 완료: {env_path}")
else:
    logger.warning(f".env 파일을 찾을 수 없습니다: {env_path}")
    # .env 파일이 없어도 계속 진행 (환경 변수에서 직접 읽음)
    load_dotenv(env_path, override=False)

# Agent 서버 URL (EC2 서버)
AGENT_SERVER_URL = os.getenv("AGENT_SERVER_URL", "")
if not AGENT_SERVER_URL:
    raise ValueError("AGENT_SERVER_URL 환경 변수가 설정되지 않았습니다.")

# Agent 이름
AGENT_NAME = os.getenv("AGENT_NAME", "local-agent")

# 폴링 간격 (초)
POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL", "10"))

# 작업 타임아웃 (초)
TASK_TIMEOUT = int(os.getenv("TASK_TIMEOUT", "3600"))  # 1시간

# Nuclei 설정
NUCLEI_BINARY_PATH = os.getenv("NUCLEI_BINARY_PATH", None)  # None이면 PATH에서 찾음
NUCLEI_TEMPLATES_DIR = os.getenv("NUCLEI_TEMPLATES_DIR", None)  # None이면 기본 경로 사용

# 데이터베이스 설정 (Agent가 결과를 DB에 직접 저장할 경우)
DB_HOST = os.getenv("DB_HOST", None)
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", None)
DB_USER = os.getenv("DB_USER", None)
DB_PASSWORD = os.getenv("DB_PASSWORD", None)

