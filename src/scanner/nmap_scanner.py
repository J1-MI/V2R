"""
Nmap 스캐너 통합 모듈
python-nmap을 사용하여 포트 스캔 및 서비스 탐지를 수행합니다.
"""

import nmap
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class NmapScanner:
    """Nmap 스캐너 래퍼 클래스"""

    def __init__(self, scan_timeout: int = 60):  # 기본값 단축 (300 -> 60초)
        """
        Args:
            scan_timeout: 스캔 타임아웃 (초)
        """
        self.scan_timeout = scan_timeout
        self.nm = nmap.PortScanner()
        self.scan_id = None
        self.target = None

    def scan(self, target: str, ports: str = "1-1000", scan_type: str = "-sV") -> Dict[str, Any]:
        """
        대상 호스트 스캔 실행

        Args:
            target: 스캔 대상 IP 주소 또는 도메인
            ports: 스캔할 포트 범위 (기본값: "1-1000")
            scan_type: 스캔 타입 (기본값: "-sV" - 버전 탐지)

        Returns:
            스캔 결과 딕셔너리
        """
        self.target = target
        # 공통 ID 생성 유틸리티 사용
        from src.utils.id_generator import generate_scan_id
        port_suffix = f"p{ports.replace(',', '_').replace('-', '_').replace(' ', '_')}"
        self.scan_id = generate_scan_id("nmap", target, port_suffix)

        logger.info(f"Starting Nmap scan: target={target}, ports={ports}, type={scan_type}")

        try:
            # Nmap 스캔 실행
            self.nm.scan(
                hosts=target,
                ports=ports,
                arguments=scan_type,
                timeout=self.scan_timeout
            )

            # 결과 파싱
            result = self._parse_results()
            result["scan_id"] = self.scan_id
            result["scanner_name"] = "nmap"
            result["scan_timestamp"] = datetime.now().isoformat()
            result["target_host"] = target
            result["scan_type"] = scan_type

            logger.info(f"Nmap scan completed: {target}")
            return result

        except Exception as e:
            logger.error(f"Nmap scan failed: {target} - {str(e)}")
            return {
                "scan_id": self.scan_id,
                "scanner_name": "nmap",
                "scan_timestamp": datetime.now().isoformat(),
                "target_host": target,
                "status": "failed",
                "error": str(e)
            }

    def _parse_results(self) -> Dict[str, Any]:
        """Nmap 결과를 파싱하여 구조화된 형식으로 변환"""
        results = {
            "status": "completed",
            "hosts": [],
            "summary": {
                "total_hosts": 0,
                "up_hosts": 0,
                "down_hosts": 0,
                "open_ports": [],
                "total_open_ports": 0
            },
            "raw_xml": None
        }

        # 호스트별 결과 파싱
        for host in self.nm.all_hosts():
            host_info = {
                "host": host,
                "state": self.nm[host].state(),
                "hostnames": [h["name"] for h in self.nm[host].hostnames()],
                "ports": []
            }

            # 포트 정보 수집
            for proto in self.nm[host].all_protocols():
                ports = self.nm[host][proto].keys()
                for port in sorted(ports):
                    port_info = self.nm[host][proto][port]
                    host_info["ports"].append({
                        "port": port,
                        "protocol": proto,
                        "state": port_info["state"],
                        "service": port_info.get("name", ""),
                        "version": port_info.get("version", ""),
                        "product": port_info.get("product", ""),
                        "extrainfo": port_info.get("extrainfo", ""),
                        "cpe": port_info.get("cpe", "")
                    })

                    # 열린 포트만 요약에 추가
                    if port_info["state"] == "open":
                        results["summary"]["open_ports"].append({
                            "host": host,
                            "port": port,
                            "protocol": proto,
                            "service": port_info.get("name", ""),
                            "version": port_info.get("version", "")
                        })

            results["hosts"].append(host_info)

            # 호스트 상태 카운트
            if host_info["state"] == "up":
                results["summary"]["up_hosts"] += 1
            else:
                results["summary"]["down_hosts"] += 1

        results["summary"]["total_hosts"] = len(results["hosts"])
        results["summary"]["total_open_ports"] = len(results["summary"]["open_ports"])

        # XML 형식의 raw 결과 저장
        try:
            results["raw_xml"] = self.nm.csv()
        except Exception:
            results["raw_xml"] = None

        return results

    def quick_scan(self, target: str) -> Dict[str, Any]:
        """
        빠른 스캔 (일반 포트만)
        """
        return self.scan(target, ports="22,80,443,3306,8080", scan_type="-sS")

    def full_scan(self, target: str) -> Dict[str, Any]:
        """
        전체 스캔 (모든 포트 + 버전 탐지)
        """
        return self.scan(target, ports="1-65535", scan_type="-sV -sC")

    def version_scan(self, target: str, ports: str = "1-1000") -> Dict[str, Any]:
        """
        버전 탐지 스캔
        """
        return self.scan(target, ports=ports, scan_type="-sV")

    def save_results(self, results: Dict[str, Any], filepath: str) -> None:
        """
        스캔 결과를 JSON 파일로 저장

        Args:
            results: 스캔 결과 딕셔너리
            filepath: 저장할 파일 경로
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Scan results saved to: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")

