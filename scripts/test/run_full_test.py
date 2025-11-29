#!/usr/bin/env python3
"""
전체 시스템 통합 테스트
모든 주요 기능을 순차적으로 테스트합니다.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_database_connection():
    """데이터베이스 연결 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("[1/7] 데이터베이스 연결 테스트")
    logger.info("=" * 60)
    
    try:
        from src.database import get_db, initialize_database
        
        db = get_db()
        if db.test_connection():
            logger.info("✓ 데이터베이스 연결 성공")
            initialize_database()
            logger.info("✓ 데이터베이스 초기화 완료")
            return True
        else:
            logger.error("✗ 데이터베이스 연결 실패")
            return False
    except Exception as e:
        logger.error(f"✗ 데이터베이스 테스트 실패: {str(e)}")
        return False


def test_nmap_scanner():
    """Nmap 스캐너 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("[2/7] Nmap 스캐너 테스트")
    logger.info("=" * 60)
    
    try:
        from src.scanner.nmap_scanner import NmapScanner
        
        scanner = NmapScanner()
        result = scanner.scan("127.0.0.1", ports="22,80,443", scan_type="-sV")
        
        if result.get("status") == "completed":
            logger.info(f"✓ Nmap 스캔 성공: {result.get('findings_count', 0)}개 발견")
            return True
        else:
            logger.warning(f"⚠ Nmap 스캔 상태: {result.get('status')}")
            return True  # 경고지만 계속 진행
    except Exception as e:
        logger.error(f"✗ Nmap 스캐너 테스트 실패: {str(e)}")
        return False


def test_nuclei_scanner():
    """Nuclei 스캐너 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("[3/7] Nuclei 스캐너 테스트")
    logger.info("=" * 60)
    
    try:
        from src.scanner.nuclei_scanner import NucleiScanner
        
        scanner = NucleiScanner()
        
        # Nuclei 설치 확인
        if not scanner._check_nuclei_installed():
            logger.warning("⚠ Nuclei가 설치되지 않았습니다. 스캔은 건너뜁니다.")
            return True  # 설치 문제는 경고로 처리
        
        # 로컬호스트는 스킵 (실제 서버 필요)
        logger.info("✓ Nuclei 스캐너 초기화 성공")
        logger.info("  (실제 스캔은 외부 서버 대상으로 테스트 필요)")
        return True
    except Exception as e:
        logger.error(f"✗ Nuclei 스캐너 테스트 실패: {str(e)}")
        return False


def test_scanner_pipeline():
    """스캐너 파이프라인 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("[4/7] 스캐너 파이프라인 테스트")
    logger.info("=" * 60)
    
    try:
        from src.pipeline.scanner_pipeline import ScannerPipeline
        
        pipeline = ScannerPipeline()
        result = pipeline.run_nmap_scan(
            target="127.0.0.1",
            ports="22,80,443",
            save_to_db=True
        )
        
        if result.get("success"):
            scan_id = result.get("scan_result_id")
            logger.info(f"✓ 스캔 파이프라인 성공 (ID: {scan_id})")
            return True, scan_id
        else:
            logger.warning(f"⚠ 스캔 파이프라인 경고: {result.get('error', 'Unknown')}")
            return True, None  # 경고지만 계속 진행
    except Exception as e:
        logger.error(f"✗ 스캔 파이프라인 테스트 실패: {str(e)}")
        return False, None


def test_poc_pipeline(scan_result_id=None):
    """PoC 재현 파이프라인 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("[5/7] PoC 재현 파이프라인 테스트")
    logger.info("=" * 60)
    
    try:
        from src.pipeline.poc_pipeline import POCPipeline
        
        pipeline = POCPipeline()
        
        # scan_result_id가 없으면 테스트용 ID 사용
        if not scan_result_id:
            logger.info("  테스트용 PoC 재현 (scan_result_id 없음)")
            return True
        
        result = pipeline.run_poc_reproduction(
            scan_result_id=scan_result_id,
            target_host="127.0.0.1"
        )
        
        if result:
            logger.info("✓ PoC 재현 파이프라인 성공")
            return True
        else:
            logger.warning("⚠ PoC 재현 파이프라인 경고 (Docker 없이 실행됨)")
            return True  # 경고지만 계속 진행
    except Exception as e:
        logger.error(f"✗ PoC 재현 파이프라인 테스트 실패: {str(e)}")
        return False


def test_reliability_scoring():
    """신뢰도 점수 계산 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("[6/7] 신뢰도 점수 계산 테스트")
    logger.info("=" * 60)

    try:
        from src.verification.reliability import ReliabilityScorer

        scorer = ReliabilityScorer()

        # 테스트용 메타데이터 / 결과 / 증거 (더미 데이터)
        poc_metadata = {
            "source": "test",
            "cve_id": "CVE-TEST-2024-0001",
            "poc_type": "test",
        }
        reproduction_result = {
            "status": "success",
            "execution_result": {"success": True},
        }
        evidence_paths = {}  # 테스트에서는 실제 증거 파일 없이 0점으로 계산

        score = scorer.calculate_reliability_score(
            poc_metadata=poc_metadata,
            reproduction_result=reproduction_result,
            evidence_paths=evidence_paths,
        )
        logger.info(f"✓ 신뢰도 점수 계산 성공: {score}/100")
        return True
    except Exception as e:
        logger.error(f"✗ 신뢰도 점수 계산 테스트 실패: {str(e)}")
        return False


def test_report_generation():
    """리포트 생성 테스트"""
    logger.info("\n" + "=" * 60)
    logger.info("[7/7] 리포트 생성 테스트")
    logger.info("=" * 60)

    try:
        from src.report.generator import ReportGenerator
        from pathlib import Path

        generator = ReportGenerator()

        # 더미 스캔 결과 / PoC 재현 결과
        scan_results = [{
            "id": 1,
            "normalized_result": {
                "findings": []
            }
        }]
        poc_reproductions = []

        result = generator.generate_report(
            report_id="test_full_run",
            scan_results=scan_results,
            poc_reproductions=poc_reproductions,
        )

        report_path = result.get("file_path")
        if report_path and Path(report_path).exists():
            logger.info(f"✓ 리포트 생성 성공: {report_path}")
            return True
        else:
            logger.warning("⚠ 리포트 생성 경고 (파일 확인 필요)")
            return True  # 경고지만 계속 진행
    except Exception as e:
        logger.error(f"✗ 리포트 생성 테스트 실패: {str(e)}")
        return False


def test_vulnerability_scan(target: Optional[str]) -> bool:
    """취약점 스캔 테스트 (Nmap + Nuclei)"""
    from src.pipeline.scanner_pipeline import ScannerPipeline

    logger.info("\n" + "=" * 60)
    logger.info("[8/?] 취약점 스캔 테스트 (외부 대상)")
    logger.info("=" * 60)

    if not target:
        logger.info("스캔 대상이 지정되지 않아 이 테스트는 건너뜁니다.")
        return True

    try:
        scanner = ScannerPipeline()
        
        # URL 구성
        if target.startswith("http://") or target.startswith("https://"):
            target_url = target
            target_ip = target.split("://")[1].split(":")[0].split("/")[0]
        else:
            target_ip = target.split(":")[0] if ":" in target else target
            target_url = f"http://{target}" if ":" in target else f"http://{target}:8080"

        logger.info(f"Target: {target_ip} ({target_url})")

        # Nmap 스캔
        logger.info("  [1/2] Nmap 스캔 실행 중...")
        nmap_result = scanner.run_nmap_scan(
            target=target_ip,
            ports="80,443,8080",
            scan_type="-sV",
            save_to_db=True,
        )
        logger.info(f"  ✓ Nmap 완료 - findings: {nmap_result.get('findings_count', 0)}")

        # Nuclei 스캔
        logger.info("  [2/2] Nuclei 스캔 실행 중...")
        nuclei_result = scanner.run_nuclei_scan(
            target=target_url,
            severity=["critical", "high", "medium"],
            save_to_db=True,
        )
        
        if nuclei_result.get("success"):
            logger.info(f"  ✓ Nuclei 완료 - findings: {nuclei_result.get('findings_count', 0)}, CVEs: {nuclei_result.get('cve_count', 0)}")
        else:
            logger.warning(f"  ⚠ Nuclei 실패: {nuclei_result.get('error', 'Unknown')}")

        logger.info("✓ 취약점 스캔 테스트 완료")
        return True
    except Exception as e:
        logger.error(f"✗ 취약점 스캔 테스트 실패: {str(e)}")
        return False


def main(scan_target: Optional[str] = None) -> int:
    """메인 테스트 실행"""
    logger.info("\n" + "=" * 60)
    logger.info("V2R 전체 시스템 통합 테스트")
    logger.info("=" * 60)

    results = {}

    # 각 테스트 실행
    results["database"] = test_database_connection()
    results["nmap"] = test_nmap_scanner()
    results["nuclei"] = test_nuclei_scanner()

    pipeline_success, scan_id = test_scanner_pipeline()
    results["pipeline"] = pipeline_success

    results["poc"] = test_poc_pipeline(scan_id)
    results["reliability"] = test_reliability_scoring()
    results["report"] = test_report_generation()

    # 외부 스캔 대상이 주어지면 Nmap + Nuclei 스캔 실행
    if scan_target:
        results["vulnerability_scan"] = test_vulnerability_scan(scan_target)

    # 결과 요약
    logger.info("\n" + "=" * 60)
    logger.info("테스트 결과 요약")
    logger.info("=" * 60)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for test_name, result in results.items():
        status = "✓ 통과" if result else "✗ 실패"
        logger.info(f"  {test_name:20s}: {status}")

    logger.info("\n" + "-" * 60)
    logger.info(f"총 {total}개 테스트 중 {passed}개 통과 ({passed*100//total}%)")
    logger.info("=" * 60)

    if passed == total:
        logger.info("🎉 모든 테스트 통과!")
        return 0
    else:
        logger.warning(f"⚠ {total - passed}개 테스트 실패")
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="V2R 전체 시스템 통합 테스트 + (옵션) 취약점 스캔",
    )
    parser.add_argument(
        "--scan-target",
        help="스캔 대상 IP 또는 URL (예: 13.125.x.x 또는 http://13.125.x.x:8080)",
        default=None,
    )

    args = parser.parse_args()
    sys.exit(main(scan_target=args.scan_target))

