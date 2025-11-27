#!/usr/bin/env python3
"""
CCE 서버 점검 테스트 스크립트
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.compliance import CCEChecker, ComplianceReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


def test_cce_checker(host: str, username: str = "root", password: str = None, key_file: str = None):
    """CCE 서버 점검 테스트"""
    logger.info("=" * 60)
    logger.info("CCE 서버 점검 테스트 시작")
    logger.info("=" * 60)
    logger.info(f"대상 호스트: {host}")
    logger.info("")
    
    # 1. CCE 점검 실행
    logger.info("[1/3] CCE 서버 점검 실행")
    checker = CCEChecker()
    
    result = checker.check_server(
        host=host,
        username=username,
        password=password,
        key_file=key_file
    )
    
    if not result.get("success"):
        logger.error(f"점검 실패: {result.get('error')}")
        return False
    
    # 2. 결과 출력
    logger.info("[2/3] 점검 결과")
    stats = result.get("statistics", {})
    logger.info(f"  전체: {stats.get('total', 0)}")
    logger.info(f"  양호: {stats.get('양호', 0)}")
    logger.info(f"  취약: {stats.get('취약', 0)}")
    logger.info(f"  주의: {stats.get('주의', 0)}")
    logger.info("")
    
    for check in result.get("checks", []):
        status_icon = "✓" if check.get("status") == "양호" else "✗" if check.get("status") == "취약" else "⚠"
        logger.info(f"  {status_icon} [{check.get('id')}] {check.get('title')}: {check.get('status')}")
    
    logger.info("")
    
    # 3. 리포트 생성
    logger.info("[3/3] 리포트 생성")
    generator = ComplianceReportGenerator()
    
    report_id = f"cce_report_{host.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    base_path = f"reports/{report_id}"
    
    files = generator.generate_both(result, base_path)
    logger.info(f"  ✓ XML 리포트: {files['xml']}")
    logger.info(f"  ✓ JSON 리포트: {files['json']}")
    logger.info("")
    logger.info("=" * 60)
    logger.info("CCE 서버 점검 테스트 완료")
    logger.info("=" * 60)
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CCE 서버 점검 테스트")
    parser.add_argument("--host", type=str, required=True, help="대상 서버 호스트")
    parser.add_argument("--username", type=str, default="root", help="SSH 사용자명")
    parser.add_argument("--password", type=str, help="SSH 비밀번호")
    parser.add_argument("--key-file", type=str, help="SSH 키 파일 경로")
    
    args = parser.parse_args()
    
    success = test_cce_checker(
        host=args.host,
        username=args.username,
        password=args.password,
        key_file=args.key_file
    )
    sys.exit(0 if success else 1)

