#!/usr/bin/env python3
"""
Agent 시작 스크립트 (Windows/Unix 호환)
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agent.main import main

if __name__ == "__main__":
    # 환경 변수 확인
    if not os.getenv("AGENT_SERVER_URL"):
        print("❌ 오류: AGENT_SERVER_URL 환경 변수가 설정되지 않았습니다.")
        print("예시: export AGENT_SERVER_URL=http://ec2-server-ip:5000")
        sys.exit(1)
    
    main()

