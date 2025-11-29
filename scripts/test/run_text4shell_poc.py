#!/usr/bin/env python3
"""
Text4Shell (CVE-2022-42889) 스캔 + PoC 재현 워크플로우

1. Nmap/Nuclei 스캔으로 대상 서버의 취약점 스캔
2. Nuclei 결과를 DB에 저장
3. Text4Shell 대상에 대해 PoC 재현 파이프라인 실행
4. PoC 재현 결과를 DB(poc_reproductions)에 저장
"""

import sys
import argparse
import logging
from pathlib import Path as _P

# 프로젝트 루트를 Python 경로에 추가
project_root = _P(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.text4shell_workflow import (  # type: ignore  # noqa: E402
    run_text4shell_workflow,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("run_text4shell_poc")


def main():
    parser = argparse.ArgumentParser(
        description="Run Text4Shell (CVE-2022-42889) scan + PoC workflow",
    )
    parser.add_argument(
        "--target",
        required=True,
        help="EC2 퍼블릭 IP 또는 호스트네임 (예: 13.125.220.26)",
    )

    args = parser.parse_args()
    run_text4shell_workflow(args.target.strip())


if __name__ == "__main__":
    main()


