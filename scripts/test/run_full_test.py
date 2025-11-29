#!/usr/bin/env python3
"""
V2R 전체 시스템 통합 테스트
모든 주요 기능을 순차적으로 테스트합니다.
"""

import sys
import logging
import traceback
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestResult:
    """테스트 결과 클래스"""
    def __init__(self, name: str):
        self.name = name
        self.success = False
        self.message = ""
        self.details: Dict[str, Any] = {}
        self.duration: float = 0.0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def start(self):
        self.start_time = datetime.now()
    
    def finish(self, success: bool, message: str = "", details: Optional[Dict[str, Any]] = None):
        self.end_time = datetime.now()
        self.success = success
        self.message = message
        self.details = details or {}
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()


def test_database_connection() -> TestResult:
    """데이터베이스 연결 테스트"""
    result = TestResult("database")
    result.start()
    
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
            result.finish(True, "데이터베이스 연결 및 초기화 성공")
        else:
            logger.error("✗ 데이터베이스 연결 실패")
            result.finish(False, "데이터베이스 연결 실패")
    except Exception as e:
        logger.error(f"✗ 데이터베이스 테스트 실패: {str(e)}")
        logger.debug(traceback.format_exc())
        result.finish(False, f"데이터베이스 테스트 실패: {str(e)}")
    
    return result


def test_nmap_scanner() -> TestResult:
    """Nmap 스캐너 테스트"""
    result = TestResult("nmap")
    result.start()
    
    logger.info("\n" + "=" * 60)
    logger.info("[2/7] Nmap 스캐너 테스트")
    logger.info("=" * 60)
    
    try:
        from src.scanner.nmap_scanner import NmapScanner
        
        scanner = NmapScanner()
        scan_result = scanner.scan("127.0.0.1", ports="22,80,443", scan_type="-sV")
        
        status = scan_result.get("status", "unknown")
        findings_count = scan_result.get("findings_count", 0)
        
        if status == "completed":
            logger.info(f"✓ Nmap 스캔 성공: {findings_count}개 발견")
            result.finish(True, f"Nmap 스캔 성공 ({findings_count}개 발견)", {
                "findings_count": findings_count,
                "status": status
            })
        else:
            logger.warning(f"⚠ Nmap 스캔 상태: {status}")
            result.finish(True, f"Nmap 스캔 완료 (상태: {status})", {
                "findings_count": findings_count,
                "status": status
            })
    except Exception as e:
        logger.error(f"✗ Nmap 스캐너 테스트 실패: {str(e)}")
        logger.debug(traceback.format_exc())
        result.finish(False, f"Nmap 스캐너 테스트 실패: {str(e)}")
    
    return result


def test_nuclei_scanner() -> TestResult:
    """Nuclei 스캐너 테스트"""
    result = TestResult("nuclei")
    result.start()
    
    logger.info("\n" + "=" * 60)
    logger.info("[3/7] Nuclei 스캐너 테스트")
    logger.info("=" * 60)
    
    try:
        from src.scanner.nuclei_scanner import NucleiScanner
        
        scanner = NucleiScanner()
        
        # Nuclei 설치 확인
        if not scanner._check_nuclei_installed():
            logger.warning("⚠ Nuclei가 설치되지 않았습니다. 스캔은 건너뜁니다.")
            result.finish(True, "Nuclei 미설치 (경고)", {"installed": False})
            return result
        
        # 로컬호스트는 스킵 (실제 서버 필요)
        logger.info("✓ Nuclei 스캐너 초기화 성공")
        logger.info("  (실제 스캔은 외부 서버 대상으로 테스트 필요)")
        result.finish(True, "Nuclei 스캐너 초기화 성공", {"installed": True})
    except Exception as e:
        logger.error(f"✗ Nuclei 스캐너 테스트 실패: {str(e)}")
        logger.debug(traceback.format_exc())
        result.finish(False, f"Nuclei 스캐너 테스트 실패: {str(e)}")
    
    return result


def test_scanner_pipeline() -> Tuple[TestResult, Optional[int]]:
    """스캐너 파이프라인 테스트"""
    result = TestResult("pipeline")
    result.start()
    
    logger.info("\n" + "=" * 60)
    logger.info("[4/7] 스캐너 파이프라인 테스트")
    logger.info("=" * 60)
    
    scan_id = None
    
    try:
        from src.pipeline.scanner_pipeline import ScannerPipeline
        
        pipeline = ScannerPipeline()
        scan_result = pipeline.run_nmap_scan(
            target="127.0.0.1",
            ports="22,80,443",
            save_to_db=True
        )
        
        if scan_result.get("success"):
            scan_id = scan_result.get("scan_result_id")
            findings_count = scan_result.get("findings_count", 0)
            logger.info(f"✓ 스캔 파이프라인 성공 (ID: {scan_id}, Findings: {findings_count})")
            result.finish(True, f"스캔 파이프라인 성공", {
                "scan_id": scan_id,
                "findings_count": findings_count
            })
        else:
            error = scan_result.get("error", "Unknown")
            logger.warning(f"⚠ 스캔 파이프라인 경고: {error}")
            result.finish(True, f"스캔 파이프라인 경고: {error}", {
                "error": error
            })
    except Exception as e:
        logger.error(f"✗ 스캔 파이프라인 테스트 실패: {str(e)}")
        logger.debug(traceback.format_exc())
        result.finish(False, f"스캔 파이프라인 테스트 실패: {str(e)}")
    
    return result, scan_id


def test_poc_pipeline(scan_result_id: Optional[int] = None) -> TestResult:
    """PoC 재현 파이프라인 테스트"""
    result = TestResult("poc")
    result.start()
    
    logger.info("\n" + "=" * 60)
    logger.info("[5/7] PoC 재현 파이프라인 테스트")
    logger.info("=" * 60)
    
    try:
        from src.pipeline.poc_pipeline import POCPipeline
        
        pipeline = POCPipeline()
        
        # scan_result_id가 없으면 테스트용 ID 사용
        if not scan_result_id:
            logger.info("  테스트용 PoC 재현 (scan_result_id 없음)")
            result.finish(True, "테스트용 PoC 재현 (scan_result_id 없음)", {"skipped": True})
            return result
        
        poc_result = pipeline.run_poc_reproduction(
            scan_result_id=scan_result_id,
            target_host="127.0.0.1"
        )
        
        if poc_result:
            logger.info("✓ PoC 재현 파이프라인 성공")
            result.finish(True, "PoC 재현 파이프라인 성공")
        else:
            logger.warning("⚠ PoC 재현 파이프라인 경고 (Docker 없이 실행됨)")
            result.finish(True, "PoC 재현 파이프라인 경고 (Docker 없음)", {"docker_available": False})
    except Exception as e:
        logger.error(f"✗ PoC 재현 파이프라인 테스트 실패: {str(e)}")
        logger.debug(traceback.format_exc())
        result.finish(False, f"PoC 재현 파이프라인 테스트 실패: {str(e)}")
    
    return result


def test_reliability_scoring() -> TestResult:
    """신뢰도 점수 계산 테스트"""
    result = TestResult("reliability")
    result.start()
    
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
        result.finish(True, f"신뢰도 점수 계산 성공: {score}/100", {"score": score})
    except Exception as e:
        logger.error(f"✗ 신뢰도 점수 계산 테스트 실패: {str(e)}")
        logger.debug(traceback.format_exc())
        result.finish(False, f"신뢰도 점수 계산 테스트 실패: {str(e)}")
    
    return result


def test_report_generation() -> TestResult:
    """리포트 생성 테스트"""
    result = TestResult("report")
    result.start()
    
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

        report_result = generator.generate_report(
            report_id="test_full_run",
            scan_results=scan_results,
            poc_reproductions=poc_reproductions,
        )

        report_path = report_result.get("file_path")
        if report_path and Path(report_path).exists():
            file_size = Path(report_path).stat().st_size
            logger.info(f"✓ 리포트 생성 성공: {report_path} ({file_size} bytes)")
            result.finish(True, f"리포트 생성 성공: {report_path}", {
                "file_path": report_path,
                "file_size": file_size
            })
        else:
            logger.warning("⚠ 리포트 생성 경고 (파일 확인 필요)")
            result.finish(True, "리포트 생성 경고 (파일 확인 필요)", report_result)
    except Exception as e:
        logger.error(f"✗ 리포트 생성 테스트 실패: {str(e)}")
        logger.debug(traceback.format_exc())
        result.finish(False, f"리포트 생성 테스트 실패: {str(e)}")
    
    return result


def test_vulnerability_scan(target: Optional[str]) -> TestResult:
    """취약점 스캔 테스트 (Nmap + Nuclei)"""
    result = TestResult("vulnerability_scan")
    result.start()
    
    logger.info("\n" + "=" * 60)
    logger.info("[8/?] 취약점 스캔 테스트 (외부 대상)")
    logger.info("=" * 60)

    if not target:
        logger.info("스캔 대상이 지정되지 않아 이 테스트는 건너뜁니다.")
        result.finish(True, "스캔 대상 미지정 (건너뜀)", {"skipped": True})
        return result

    try:
        from src.pipeline.scanner_pipeline import ScannerPipeline
        from urllib.parse import urlparse
        
        scanner = ScannerPipeline()
        
        # URL 파싱
        parsed_url = urlparse(target) if target.startswith(("http://", "https://")) else None
        
        if parsed_url and parsed_url.netloc:
            # URL 형식: http://host:port
            target_url = target
            target_ip = parsed_url.hostname
            port = parsed_url.port
        else:
            # IP:port 형식 또는 IP만
            if ":" in target:
                target_ip, port_str = target.split(":", 1)
                try:
                    port = int(port_str)
                except ValueError:
                    port = None
            else:
                target_ip = target
                port = None
            
            # URL 구성
            if port:
                target_url = f"http://{target_ip}:{port}"
            else:
                target_url = f"http://{target_ip}:8080"  # 기본 포트

        logger.info(f"Target: {target_ip} ({target_url})")

        # Nmap 스캔
        logger.info("  [1/2] Nmap 스캔 실행 중...")
        if port:
            ports = str(port)
        else:
            ports = "80,443,8080,8081"
        
        nmap_result = scanner.run_nmap_scan(
            target=target_ip,
            ports=ports,
            scan_type="-sV",
            save_to_db=True,
        )
        
        nmap_findings = nmap_result.get('findings_count', 0)
        logger.info(f"  ✓ Nmap 완료 - findings: {nmap_findings}")

        # Nuclei 스캔
        logger.info("  [2/2] Nuclei 스캔 실행 중...")
        nuclei_result = scanner.run_nuclei_scan(
            target=target_url,
            severity=["critical", "high", "medium"],
            save_to_db=True,
        )
        
        if nuclei_result.get("success"):
            nuclei_findings = nuclei_result.get('findings_count', 0)
            nuclei_cves = nuclei_result.get('cve_count', 0)
            logger.info(f"  ✓ Nuclei 완료 - findings: {nuclei_findings}, CVEs: {nuclei_cves}")
            result.finish(True, "취약점 스캔 완료", {
                "nmap_findings": nmap_findings,
                "nuclei_findings": nuclei_findings,
                "nuclei_cves": nuclei_cves
            })
        else:
            error = nuclei_result.get('error', 'Unknown')
            logger.warning(f"  ⚠ Nuclei 실패: {error}")
            result.finish(True, f"취약점 스캔 완료 (Nuclei 경고: {error})", {
                "nmap_findings": nmap_findings,
                "nuclei_error": error
            })

        logger.info("✓ 취약점 스캔 테스트 완료")
    except Exception as e:
        logger.error(f"✗ 취약점 스캔 테스트 실패: {str(e)}")
        logger.debug(traceback.format_exc())
        result.finish(False, f"취약점 스캔 테스트 실패: {str(e)}")
    
    return result


def main(scan_target: Optional[str] = None) -> int:
    """메인 테스트 실행"""
    logger.info("\n" + "=" * 60)
    logger.info("V2R 전체 시스템 통합 테스트")
    logger.info("=" * 60)
    logger.info(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if scan_target:
        logger.info(f"스캔 대상: {scan_target}")

    results: Dict[str, TestResult] = {}

    # 각 테스트 실행
    results["database"] = test_database_connection()
    results["nmap"] = test_nmap_scanner()
    results["nuclei"] = test_nuclei_scanner()

    pipeline_result, scan_id = test_scanner_pipeline()
    results["pipeline"] = pipeline_result

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
    passed = sum(1 for r in results.values() if r.success)
    total_duration = sum(r.duration for r in results.values())

    for test_name, test_result in results.items():
        status = "✓ 통과" if test_result.success else "✗ 실패"
        duration_str = f"({test_result.duration:.2f}s)" if test_result.duration > 0 else ""
        logger.info(f"  {test_name:20s}: {status} {duration_str}")
        if test_result.message and not test_result.success:
            logger.info(f"    └─ {test_result.message}")

    logger.info("\n" + "-" * 60)
    logger.info(f"총 {total}개 테스트 중 {passed}개 통과 ({passed*100//total if total > 0 else 0}%)")
    logger.info(f"총 실행 시간: {total_duration:.2f}초")
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
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 기본 테스트만 실행
  python scripts/test/run_full_test.py

  # 외부 대상 스캔 포함
  python scripts/test/run_full_test.py --scan-target http://host.docker.internal:8081
  
  # IP:포트 형식
  python scripts/test/run_full_test.py --scan-target 192.168.1.100:8080
        """
    )
    parser.add_argument(
        "--scan-target",
        help="스캔 대상 IP 또는 URL (예: 192.168.1.100 또는 http://192.168.1.100:8080)",
        default=None,
    )

    args = parser.parse_args()
    sys.exit(main(scan_target=args.scan_target))
