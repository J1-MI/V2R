"""
Nuclei 스캐너 통합 모듈
Nuclei를 사용하여 취약점 템플릿 기반 스캔을 수행합니다.
"""

import subprocess
import json
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class NucleiScanner:
    """Nuclei 스캐너 래퍼 클래스"""

    def __init__(self, nuclei_path: Optional[str] = None, templates_path: Optional[str] = None):
        """
        Args:
            nuclei_path: Nuclei 실행 파일 경로 (None이면 환경 변수 또는 PATH에서 찾음)
            templates_path: Nuclei 템플릿 경로 (None이면 환경 변수 또는 기본값 사용)
        """
        # 환경 변수에서 읽기 (우선순위: 인자 > 환경 변수 > 기본값)
        if nuclei_path is None:
            nuclei_path = os.getenv("NUCLEI_BINARY_PATH", None)
        if nuclei_path is None:
            nuclei_path = "nuclei"  # PATH에서 찾음
        
        if templates_path is None:
            templates_path = os.getenv("NUCLEI_TEMPLATES_DIR", None)
        if templates_path is None:
            templates_path = os.getenv("NUCLEI_TEMPLATES_PATH", None)
        
        self.nuclei_path = nuclei_path
        self.templates_path = templates_path
        self.scan_id = None
        self.target = None
        
        logger.info(f"NucleiScanner 초기화: binary={self.nuclei_path}, templates={self.templates_path}")

    def _check_nuclei_installed(self) -> bool:
        """Nuclei가 설치되어 있는지 확인"""
        try:
            result = subprocess.run(
                [self.nuclei_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def scan(
        self,
        target: str,
        template_types: Optional[List[str]] = None,
        template_files: Optional[List[str]] = None,
        severity: Optional[List[str]] = None,
        rate_limit: int = 500  # 기본값 증가 (300 -> 500, 스캔 속도 향상)
    ) -> Dict[str, Any]:
        """
        대상 호스트 Nuclei 스캔 실행

        Args:
            target: 스캔 대상 URL 또는 IP
            template_types: 스캔할 템플릿 타입 (예: ["cve", "vulnerability"])
            template_files: 특정 템플릿 파일 경로 리스트 (예: ["/path/to/template.yaml"])
            severity: 심각도 필터 (예: ["critical", "high"])
            rate_limit: 초당 요청 수 제한

        Returns:
            스캔 결과 딕셔너리
        """
        if not self._check_nuclei_installed():
            logger.error("Nuclei is not installed or not in PATH")
            return {
                "status": "failed",
                "error": "Nuclei not found",
                "target_host": target,
                "scan_timestamp": datetime.now().isoformat()
            }

        self.target = target
        # 공통 ID 생성 유틸리티 사용
        from src.utils.id_generator import generate_scan_id
        self.scan_id = generate_scan_id("nuclei", target)

        logger.info(f"Starting Nuclei scan: target={target}")

        try:
            # Nuclei 명령어 구성
            # Nuclei v3.x에서는 -jsonl 또는 -j 사용 (v2.x의 -json 대신)
            cmd = [self.nuclei_path, "-u", target, "-jsonl", "-rate-limit", str(rate_limit)]

            # 특정 템플릿 파일 지정 (우선순위 높음)
            if template_files:
                # 템플릿 파일 경로 검증
                from pathlib import Path
                valid_templates = []
                for template_file in template_files:
                    if Path(template_file).exists():
                        valid_templates.append(template_file)
                    else:
                        logger.warning(f"Template file not found: {template_file}")
                if valid_templates:
                    cmd.extend(["-t", ",".join(valid_templates)])
                    logger.info(f"Using template files: {valid_templates}")
                else:
                    logger.error("No valid template files found")
                    return {
                        "scan_id": self.scan_id,
                        "scanner_name": "nuclei",
                        "scan_timestamp": datetime.now().isoformat(),
                        "target_host": target,
                        "status": "failed",
                        "error": "No valid template files found",
                        "findings": []
                    }
            # 템플릿 타입 필터
            elif template_types:
                cmd.extend(["-t", ",".join(template_types)])

            # 심각도 필터
            if severity:
                cmd.extend(["-severity", ",".join(severity)])

            # 템플릿 경로 지정 (템플릿 파일이 절대 경로가 아닌 경우)
            if self.templates_path and not template_files:
                # 경로 존재 확인
                from pathlib import Path
                templates_path_obj = Path(self.templates_path)
                if templates_path_obj.exists():
                    cmd.extend(["-templates", self.templates_path])
                    logger.debug(f"Using templates path: {self.templates_path}")
                else:
                    logger.warning(f"Templates path does not exist: {self.templates_path}, skipping -templates flag")
            
            logger.info(f"Nuclei command: {' '.join(cmd)}")

            # 스캔 실행
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃 (속도와 안정성 균형)
            )

            # 결과 파싱
            findings = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            finding = json.loads(line)
                            findings.append(finding)
                        except json.JSONDecodeError:
                            continue

            # exit code에 따른 상태 결정
            # exit code 0: 성공, 1: 취약점 발견 (성공), 2+: 실패
            if result.returncode == 0:
                status = "completed"
            elif result.returncode == 1:
                # exit code 1은 취약점이 발견되었을 때도 발생할 수 있음
                status = "completed" if findings else "failed"
            else:
                status = "failed"
            
            scan_result = {
                "scan_id": self.scan_id,
                "scanner_name": "nuclei",
                "scan_timestamp": datetime.now().isoformat(),
                "target_host": target,
                "status": status,
                "findings": findings,
                "summary": {
                    "total_findings": len(findings),
                    "by_severity": self._count_by_severity(findings),
                    "by_template": self._count_by_template(findings)
                },
                "raw_output": result.stdout,
                "error_output": result.stderr if result.returncode != 0 else None,
                "exit_code": result.returncode
            }

            # stderr와 stdout 모두 로깅 (디버깅용)
            if result.stderr:
                logger.warning(f"Nuclei stderr (exit code {result.returncode}): {result.stderr}")
            elif result.returncode != 0:
                # stderr가 없어도 exit code가 0이 아니면 stdout을 확인
                logger.warning(f"Nuclei stdout (exit code {result.returncode}): {result.stdout[:500]}")
            
            if status == "completed":
                logger.info(f"Nuclei scan completed: {target}, findings={len(findings)}, exit_code={result.returncode}")
            else:
                # 에러 메시지 구성
                if result.stderr:
                    error_msg = result.stderr.strip()
                elif result.stdout:
                    error_msg = result.stdout.strip()[:200]
                else:
                    error_msg = f"Exit code {result.returncode}"
                logger.error(f"Nuclei scan failed: {target}, exit_code={result.returncode}, error={error_msg}")
            
            return scan_result

        except subprocess.TimeoutExpired:
            logger.error(f"Nuclei scan timeout: {target}")
            return {
                "scan_id": self.scan_id,
                "scanner_name": "nuclei",
                "scan_timestamp": datetime.now().isoformat(),
                "target_host": target,
                "status": "timeout",
                "error": "Scan timeout"
            }
        except Exception as e:
            logger.error(f"Nuclei scan failed: {target} - {str(e)}")
            return {
                "scan_id": self.scan_id,
                "scanner_name": "nuclei",
                "scan_timestamp": datetime.now().isoformat(),
                "target_host": target,
                "status": "failed",
                "error": str(e)
            }

    def _count_by_severity(self, findings: List[Dict[str, Any]]) -> Dict[str, int]:
        """심각도별 카운트"""
        counts = {}
        for finding in findings:
            severity = finding.get("info", {}).get("severity", "unknown").lower()
            counts[severity] = counts.get(severity, 0) + 1
        return counts

    def _count_by_template(self, findings: List[Dict[str, Any]]) -> Dict[str, int]:
        """템플릿별 카운트"""
        counts = {}
        for finding in findings:
            template_id = finding.get("template-id", "unknown")
            counts[template_id] = counts.get(template_id, 0) + 1
        return counts

    def cve_scan(self, target: str) -> Dict[str, Any]:
        """CVE 템플릿만 스캔"""
        return self.scan(target, template_types=["cve"], severity=["critical", "high"])

    def save_results(self, results: Dict[str, Any], filepath: str) -> None:
        """스캔 결과를 JSON 파일로 저장"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Nuclei scan results saved to: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")

