"""
스캔 결과 정규화 모듈
다양한 스캐너의 결과를 공통 스키마로 변환합니다.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class ScanResultNormalizer:
    """스캔 결과 정규화 클래스"""

    # 공통 심각도 매핑
    SEVERITY_MAP = {
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "info": "Info",
        "informational": "Info"
    }

    def __init__(self):
        self.normalized_schema = {
            "scan_id": "",
            "scanner_name": "",
            "scan_timestamp": "",
            "target_host": "",
            "scan_type": "",
            "status": "",
            "findings": [],
            "metadata": {}
        }

    def normalize(self, raw_result: Dict[str, Any], scanner_name: str) -> Dict[str, Any]:
        """
        스캔 결과를 공통 스키마로 정규화

        Args:
            raw_result: 원본 스캔 결과
            scanner_name: 스캐너 이름 (nmap, nuclei, etc.)

        Returns:
            정규화된 결과
        """
        try:
            if scanner_name.lower() == "nmap":
                return self._normalize_nmap(raw_result)
            elif scanner_name.lower() == "nuclei":
                return self._normalize_nuclei(raw_result)
            else:
                logger.warning(f"Unknown scanner: {scanner_name}, returning as-is")
                return self._normalize_generic(raw_result, scanner_name)

        except Exception as e:
            logger.error(f"Normalization failed: {str(e)}")
            return self._create_error_result(raw_result, scanner_name, str(e))

    def _normalize_nmap(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """Nmap 결과 정규화"""
        normalized = {
            "scan_id": raw_result.get("scan_id", ""),
            "scanner_name": "nmap",
            "scan_timestamp": raw_result.get("scan_timestamp", datetime.now().isoformat()),
            "target_host": raw_result.get("target_host", ""),
            "scan_type": raw_result.get("scan_type", "port_scan"),
            "status": raw_result.get("status", "unknown"),
            "findings": [],
            "metadata": {
                "summary": raw_result.get("summary", {}),
                "hosts": raw_result.get("hosts", [])
            }
        }

        # 열린 포트를 findings로 변환
        open_ports = raw_result.get("summary", {}).get("open_ports", [])
        for port_info in open_ports:
            finding = {
                "finding_id": f"nmap_{normalized['target_host']}_{port_info['port']}_{port_info['protocol']}",
                "type": "open_port",
                "title": f"Open Port: {port_info['port']}/{port_info['protocol']}",
                "description": f"Port {port_info['port']} ({port_info['protocol']}) is open",
                "severity": self._determine_severity_from_port(port_info),
                "evidence": {
                    "port": port_info["port"],
                    "protocol": port_info["protocol"],
                    "service": port_info.get("service", ""),
                    "version": port_info.get("version", "")
                },
                "source": "nmap",
                "cve_list": [],  # Nmap 자체는 CVE를 제공하지 않음
                "recommendation": self._get_port_recommendation(port_info)
            }
            normalized["findings"].append(finding)

        return normalized

    def _normalize_nuclei(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """Nuclei 결과 정규화"""
        normalized = {
            "scan_id": raw_result.get("scan_id", ""),
            "scanner_name": "nuclei",
            "scan_timestamp": raw_result.get("scan_timestamp", datetime.now().isoformat()),
            "target_host": raw_result.get("target_host", ""),
            "scan_type": "vulnerability_scan",
            "status": raw_result.get("status", "unknown"),
            "findings": [],
            "metadata": {
                "summary": raw_result.get("summary", {}),
                "total_findings": len(raw_result.get("findings", []))
            }
        }

        # Nuclei findings 변환
        for finding in raw_result.get("findings", []):
            info = finding.get("info", {})
            normalized_finding = {
                "finding_id": finding.get("template-id", "") + "_" + finding.get("host", ""),
                "type": info.get("classification", {}).get("cve-id") or info.get("name", "vulnerability"),
                "title": info.get("name", "Unknown Vulnerability"),
                "description": info.get("description", ""),
                "severity": self._normalize_severity(info.get("severity", "unknown")),
                "evidence": {
                    "matched_at": finding.get("matched-at", ""),
                    "request": finding.get("request", ""),
                    "response": finding.get("response", ""),
                    "curl_command": finding.get("curl-command", "")
                },
                "source": "nuclei",
                "cve_list": self._extract_cves(info),
                "reference": info.get("reference", []),
                "tags": info.get("tags", []),
                "recommendation": info.get("remediation", "")
            }
            normalized["findings"].append(normalized_finding)

        return normalized

    def _normalize_generic(self, raw_result: Dict[str, Any], scanner_name: str) -> Dict[str, Any]:
        """일반적인 스캔 결과 정규화"""
        return {
            "scan_id": raw_result.get("scan_id", ""),
            "scanner_name": scanner_name,
            "scan_timestamp": raw_result.get("scan_timestamp", datetime.now().isoformat()),
            "target_host": raw_result.get("target_host", ""),
            "scan_type": "generic",
            "status": raw_result.get("status", "unknown"),
            "findings": [],
            "metadata": raw_result
        }

    def _normalize_severity(self, severity: str) -> str:
        """심각도를 표준 형식으로 변환"""
        severity_lower = severity.lower()
        return self.SEVERITY_MAP.get(severity_lower, "Info")

    def _determine_severity_from_port(self, port_info: Dict[str, Any]) -> str:
        """포트 정보로부터 심각도 결정"""
        port = port_info.get("port", 0)
        service = port_info.get("service", "").lower()

        # 위험한 포트/서비스
        if port in [22, 3306, 5432, 1433, 3389] and not port_info.get("version"):
            return "Medium"  # 외부 노출된 관리 포트
        elif service in ["http", "https", "www"]:
            return "Low"  # 일반 웹 서비스
        elif port in [1, 1024]:
            return "Low"
        else:
            return "Info"

    def _get_port_recommendation(self, port_info: Dict[str, Any]) -> str:
        """포트에 대한 권장사항 생성"""
        port = port_info.get("port", 0)
        service = port_info.get("service", "").lower()

        if port == 22:
            return "SSH 포트가 외부에 노출되어 있습니다. 공개 키 인증 사용 및 강력한 비밀번호 정책 적용을 권장합니다."
        elif port == 3306:
            return "MySQL 포트가 외부에 노출되어 있습니다. 방화벽 규칙으로 접근 제한 및 강력한 인증 설정을 권장합니다."
        elif service in ["http", "https"]:
            return f"{service.upper()} 서비스가 실행 중입니다. 최신 보안 패치 적용 및 보안 헤더 설정을 권장합니다."
        else:
            return f"포트 {port} ({port_info.get('protocol')})이 열려있습니다. 필요한 서비스인지 확인하고 불필요한 경우 차단을 권장합니다."

    def _extract_cves(self, info: Dict[str, Any]) -> List[str]:
        """정보에서 CVE ID 추출"""
        cves = []

        # CVE ID 필드에서 추출
        cve_id = info.get("classification", {}).get("cve-id")
        if cve_id:
            cves.append(cve_id.upper())

        # 참조 링크에서 CVE 추출
        references = info.get("reference", [])
        if isinstance(references, list):
            for ref in references:
                if isinstance(ref, str):
                    # CVE 정규식으로 추출
                    cve_matches = re.findall(r'CVE-\d{4}-\d{4,7}', ref.upper())
                    cves.extend(cve_matches)

        # 중복 제거 및 정렬
        return sorted(list(set(cves)))

    def _create_error_result(
        self,
        raw_result: Dict[str, Any],
        scanner_name: str,
        error_message: str
    ) -> Dict[str, Any]:
        """에러 결과 생성"""
        return {
            "scan_id": raw_result.get("scan_id", ""),
            "scanner_name": scanner_name,
            "scan_timestamp": datetime.now().isoformat(),
            "target_host": raw_result.get("target_host", ""),
            "scan_type": "unknown",
            "status": "error",
            "findings": [],
            "metadata": {
                "error": error_message,
                "raw_result": raw_result
            }
        }

    def extract_cves(self, normalized_result: Dict[str, Any]) -> List[str]:
        """
        정규화된 결과에서 모든 CVE ID 추출

        Returns:
            CVE ID 리스트
        """
        cves = []
        for finding in normalized_result.get("findings", []):
            cves.extend(finding.get("cve_list", []))
        return sorted(list(set(cves)))

    def get_findings_by_severity(
        self,
        normalized_result: Dict[str, Any],
        severity: str
    ) -> List[Dict[str, Any]]:
        """
        특정 심각도의 findings만 필터링

        Args:
            normalized_result: 정규화된 결과
            severity: 심각도 (Critical, High, Medium, Low, Info)

        Returns:
            필터링된 findings 리스트
        """
        return [
            finding for finding in normalized_result.get("findings", [])
            if finding.get("severity", "").lower() == severity.lower()
        ]

