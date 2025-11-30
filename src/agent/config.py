"""
Agent 설정 관리
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

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

