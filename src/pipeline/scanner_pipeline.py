"""
스캐너 파이프라인
스캔 실행 → 정규화 → DB 저장의 전체 워크플로우 관리
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.scanner import NmapScanner, NucleiScanner, ScanResultNormalizer
from src.database import get_db
from src.database.repository import ScanResultRepository

logger = logging.getLogger(__name__)


class ScannerPipeline:
    """스캐너 파이프라인 클래스"""

    def __init__(self, nuclei_templates_path: Optional[str] = None):
        """
        Args:
            nuclei_templates_path: Nuclei 템플릿 경로 (기본값: /usr/local/bin/nuclei-templates)
        """
        self.nmap_scanner = NmapScanner()
        # 템플릿 경로가 지정되지 않으면 기본 경로 사용
        default_templates_path = nuclei_templates_path or "/usr/local/bin/nuclei-templates"
        self.nuclei_scanner = NucleiScanner(templates_path=default_templates_path)
        self.normalizer = ScanResultNormalizer()

    def run_nmap_scan(
        self,
        target: str,
        ports: str = "1-1000",
        scan_type: str = "-sV",
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Nmap 스캔 실행 및 DB 저장

        Args:
            target: 스캔 대상
            ports: 포트 범위
            scan_type: 스캔 타입
            save_to_db: DB 저장 여부

        Returns:
            스캔 결과 딕셔너리
        """
        logger.info(f"Starting Nmap scan pipeline: target={target}")

        # 1. 스캔 실행
        raw_result = self.nmap_scanner.scan(target, ports, scan_type)

        if raw_result.get("status") == "failed":
            logger.error(f"Nmap scan failed: {raw_result.get('error')}")
            return raw_result

        # 2. 정규화
        normalized_result = self.normalizer.normalize(raw_result, "nmap")

        # 3. CVE 추출
        cve_list = self.normalizer.extract_cves(normalized_result)

        # 4. 최고 심각도 결정
        severity = self._determine_max_severity(normalized_result)

        # 5. DB 저장
        if save_to_db:
            try:
                db = get_db()
                with db.get_session() as session:
                    repo = ScanResultRepository(session)

                    scan_data = {
                        "scan_id": raw_result["scan_id"],
                        "target_host": target,
                        "scan_type": scan_type,
                        "scanner_name": "nmap",
                        "scan_timestamp": datetime.fromisoformat(raw_result["scan_timestamp"].replace("Z", "+00:00")),
                        "raw_result": raw_result,
                        "normalized_result": normalized_result,
                        "cve_list": cve_list,
                        "severity": severity,
                        "status": "completed"
                    }

                    saved_result = repo.save(scan_data)
                    logger.info(f"Scan result saved to DB: {saved_result.scan_id}")

            except Exception as e:
                logger.error(f"Failed to save to DB: {str(e)}")
                # DB 저장 실패해도 결과는 반환

        # 6. 결과 반환
        return {
            "success": True,
            "scan_id": raw_result["scan_id"],
            "target": target,
            "scanner": "nmap",
            "findings_count": len(normalized_result.get("findings", [])),
            "cve_count": len(cve_list),
            "severity": severity,
            "saved_to_db": save_to_db
        }

    def run_nuclei_scan(
        self,
        target: str,
        severity: Optional[List[str]] = None,
        template_files: Optional[List[str]] = None,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Nuclei 스캔 실행 및 DB 저장

        Args:
            target: 스캔 대상 URL
            severity: 심각도 필터 (예: ["critical", "high"])
            template_files: 특정 템플릿 파일 경로 리스트 (예: ["/path/to/template.yaml"])
            save_to_db: DB 저장 여부

        Returns:
            스캔 결과 딕셔너리
        """
        logger.info(f"Starting Nuclei scan pipeline: target={target}")

        # 1. 스캔 실행
        raw_result = self.nuclei_scanner.scan(
            target,
            severity=severity,
            template_files=template_files
        )

        if raw_result.get("status") in ["failed", "timeout"]:
            error_msg = raw_result.get("error") or raw_result.get("error_output") or "Unknown error"
            logger.error(f"Nuclei scan failed: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "scan_id": raw_result.get("scan_id"),
                "target": target,
                "scanner": "nuclei",
                "findings_count": 0,
                "cve_count": 0,
                "severity": "Unknown",
                "saved_to_db": False
            }

        # 2. 정규화
        normalized_result = self.normalizer.normalize(raw_result, "nuclei")

        # 3. CVE 추출
        cve_list = self.normalizer.extract_cves(normalized_result)

        # 4. 최고 심각도 결정
        severity = self._determine_max_severity(normalized_result)

        # 5. DB 저장
        if save_to_db:
            try:
                db = get_db()
                with db.get_session() as session:
                    repo = ScanResultRepository(session)

                    scan_data = {
                        "scan_id": raw_result["scan_id"],
                        "target_host": target,
                        "scan_type": "vulnerability_scan",
                        "scanner_name": "nuclei",
                        "scan_timestamp": datetime.fromisoformat(raw_result["scan_timestamp"].replace("Z", "+00:00")),
                        "raw_result": raw_result,
                        "normalized_result": normalized_result,
                        "cve_list": cve_list,
                        "severity": severity,
                        "status": "completed"
                    }

                    saved_result = repo.save(scan_data)
                    logger.info(f"Scan result saved to DB: {saved_result.scan_id}")

            except Exception as e:
                logger.error(f"Failed to save to DB: {str(e)}")

        # 6. 결과 반환
        return {
            "success": True,
            "scan_id": raw_result["scan_id"],
            "target": target,
            "scanner": "nuclei",
            "findings_count": len(normalized_result.get("findings", [])),
            "cve_count": len(cve_list),
            "severity": severity,
            "saved_to_db": save_to_db
        }

    def run_full_scan(
        self,
        target: str,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        전체 스캔 (Nmap + Nuclei)

        Args:
            target: 스캔 대상
            save_to_db: DB 저장 여부

        Returns:
            통합 스캔 결과
        """
        logger.info(f"Starting full scan pipeline: target={target}")

        results = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "nmap": None,
            "nuclei": None,
            "all_cves": [],
            "max_severity": None
        }

        # 1. Nmap 스캔
        try:
            nmap_result = self.run_nmap_scan(target, save_to_db=save_to_db)
            results["nmap"] = nmap_result
        except Exception as e:
            logger.error(f"Nmap scan failed: {str(e)}")
            results["nmap"] = {"error": str(e)}

        # 2. Nuclei 스캔 (HTTP/HTTPS 대상만)
        if target.startswith("http://") or target.startswith("https://"):
            try:
                nuclei_result = self.run_nuclei_scan(target, save_to_db=save_to_db)
                results["nuclei"] = nuclei_result
            except Exception as e:
                logger.error(f"Nuclei scan failed: {str(e)}")
                results["nuclei"] = {"error": str(e)}

        # 3. 통합 CVE 리스트
        all_cves = set()
        if results["nmap"] and results["nmap"].get("cve_count", 0) > 0:
            # Nmap 결과에서 CVE 추출 필요 시 추가
            pass

        if results["nuclei"]:
            # Nuclei 결과에서 CVE 추출
            if "nuclei" in results and results["nuclei"].get("cve_count", 0) > 0:
                # DB에서 조회하여 CVE 리스트 가져오기
                pass

        results["all_cves"] = sorted(list(all_cves))

        # 4. 최고 심각도 결정
        severities = []
        if results["nmap"] and results["nmap"].get("severity"):
            severities.append(results["nmap"]["severity"])
        if results["nuclei"] and results["nuclei"].get("severity"):
            severities.append(results["nuclei"]["severity"])

        if severities:
            severity_order = ["Critical", "High", "Medium", "Low", "Info"]
            results["max_severity"] = min(severities, key=lambda x: severity_order.index(x) if x in severity_order else 999)

        return results

    def _determine_max_severity(self, normalized_result: Dict[str, Any]) -> str:
        """정규화된 결과에서 최고 심각도 결정"""
        findings = normalized_result.get("findings", [])
        if not findings:
            return "Info"

        severities = [f.get("severity", "Info") for f in findings]
        severity_order = ["Critical", "High", "Medium", "Low", "Info"]

        # 최고 심각도 찾기
        max_severity = "Info"
        min_index = 999
        for severity in severities:
            if severity in severity_order:
                idx = severity_order.index(severity)
                if idx < min_index:
                    min_index = idx
                    max_severity = severity

        return max_severity

