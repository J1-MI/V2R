"""
Agent 실행 진입점
"""

import logging
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agent.agent import Agent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Agent 실행"""
    try:
        agent = Agent()
        agent.run()
    except KeyboardInterrupt:
        logger.info("Agent 종료")
    except Exception as e:
        logger.error(f"Agent 실행 실패: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

