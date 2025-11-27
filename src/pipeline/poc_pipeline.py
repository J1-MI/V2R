"""
PoC 재현 파이프라인
스캔 결과 → PoC 재현 → 증거 수집 → DB 저장
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.poc import IsolationEnvironment, POCReproducer, EvidenceCollector
from src.database import get_db
from src.database.repository import POCReproductionRepository, POCMetadataRepository
from src.database.models import POCReproduction, POCMetadata

logger = logging.getLogger(__name__)


class POCPipeline:
    """PoC 재현 파이프라인 클래스"""

    def __init__(self, allow_docker_failure: bool = True):
        """
        Args:
            allow_docker_failure: Docker 실패 시 예외 없이 계속 진행 (테스트 환경용)
        """
        self.reproducer = POCReproducer(allow_docker_failure=allow_docker_failure)
        self.evidence_collector = None

    def run_poc_reproduction(
        self,
        scan_result_id: int,
        poc_script: str,
        poc_type: str = "command_injection",
        cve_id: Optional[str] = None,
        source: str = "manual",
        target_host: Optional[str] = None,
        collect_evidence: bool = True
    ) -> Dict[str, Any]:
        """
        PoC 재현 실행 및 DB 저장

        Args:
            scan_result_id: 스캔 결과 ID
            poc_script: PoC 스크립트 내용 또는 파일 경로
            poc_type: PoC 유형
            cve_id: CVE ID (선택)
            source: PoC 출처 (Exploit-DB, GitHub, etc.)
            target_host: 대상 호스트
            collect_evidence: 증거 수집 여부

        Returns:
            재현 결과 딕셔너리
        """
        logger.info(f"Starting PoC reproduction pipeline: scan_result_id={scan_result_id}")

        try:
            # 1. PoC 재현 실행
            reproduction_result = self.reproducer.reproduce(
                poc_script=poc_script,
                poc_type=poc_type,
                target_host=target_host,
                network_enabled=True
            )

            reproduction_id = reproduction_result.get("reproduction_id")

            # 2. 증거 수집
            evidence_paths = {}
            if collect_evidence and self.reproducer.isolation:
                evidence_collector = EvidenceCollector(self.reproducer.isolation)
                evidence_paths = evidence_collector.collect_after_execution(
                    reproduction_id=reproduction_id,
                    collect_syscalls=True,
                    collect_network=True,
                    collect_fs_diff=True
                )

            # 3. PoC 메타데이터 저장
            poc_metadata_id = None
            if cve_id:
                poc_metadata_id = self._save_poc_metadata(
                    cve_id=cve_id,
                    poc_type=poc_type,
                    source=source,
                    poc_script=poc_script
                )

            # 4. 재현 결과 DB 저장
            db = get_db()
            with db.get_session() as session:
                repo = POCReproductionRepository(session)

                reproduction_data = {
                    "reproduction_id": reproduction_id,
                    "poc_id": poc_metadata_id,
                    "scan_result_id": scan_result_id,
                    "target_host": target_host or reproduction_result.get("target_host", ""),
                    "reproduction_timestamp": datetime.fromisoformat(
                        reproduction_result.get("timestamp", datetime.now().isoformat())
                    ),
                    "status": reproduction_result.get("status", "failed"),
                    "evidence_location": str(evidence_paths.get("fs_diff", "")),
                    "syscall_log_path": str(evidence_paths.get("syscalls", "")),
                    "network_capture_path": str(evidence_paths.get("network", "")),
                    "filesystem_diff_path": str(evidence_paths.get("fs_diff", "")),
                    "screenshots_path": []
                }

                saved_reproduction = repo.save(reproduction_data)
                logger.info(f"PoC reproduction saved to DB: {reproduction_id}")

                return {
                    "success": True,
                    "reproduction_id": reproduction_id,
                    "status": reproduction_result.get("status"),
                    "evidence_paths": evidence_paths,
                    "db_id": saved_reproduction.id
                }

        except Exception as e:
            logger.error(f"PoC reproduction pipeline failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            # 리소스 정리
            if self.reproducer:
                self.reproducer.cleanup()

    def _save_poc_metadata(
        self,
        cve_id: str,
        poc_type: str,
        source: str,
        poc_script: str
    ) -> Optional[str]:
        """
        PoC 메타데이터 저장

        Args:
            cve_id: CVE ID
            poc_type: PoC 유형
            source: 출처
            poc_script: PoC 스크립트

        Returns:
            PoC ID
        """
        try:
            import hashlib

            # PoC ID 생성 (스크립트 해시 기반)
            poc_hash = hashlib.sha256(poc_script.encode()).hexdigest()[:16]
            poc_id = f"poc_{cve_id}_{poc_hash}"

            db = get_db()
            with db.get_session() as session:
                repo = POCMetadataRepository(session)

                poc_data = {
                    "poc_id": poc_id,
                    "cve_id": cve_id,
                    "poc_type": poc_type,
                    "source": source,
                    "file_hash_sha256": hashlib.sha256(poc_script.encode()).hexdigest(),
                    "verification_status": "unverified"
                }

                saved_poc = repo.save(poc_data)
                logger.info(f"PoC metadata saved: {poc_id}")
                return poc_id

        except Exception as e:
            logger.error(f"Failed to save PoC metadata: {str(e)}")
            return None

