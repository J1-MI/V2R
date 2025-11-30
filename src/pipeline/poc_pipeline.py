"""
PoC 재현 파이프라인
스캔 결과 → PoC 재현 → 증거 수집 → DB 저장
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.poc import IsolationEnvironment, POCReproducer, EvidenceCollector
from src.database import get_db
from src.database.repository import POCReproductionRepository, POCMetadataRepository
from src.database.models import POCReproduction, POCMetadata

logger = logging.getLogger(__name__)


class POCPipeline:
    """PoC 재현 파이프라인 클래스"""

    def __init__(self):
        self.reproducer = POCReproducer()
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

                # 4-1. PoC 재현 성공 시 관련 scan_result의 severity 업데이트
                if reproduction_result.get("status") == "success" and cve_id:
                    try:
                        from src.database.models import ScanResult
                        
                        # scan_result_id는 정수 ID이므로 직접 조회
                        if scan_result_id:
                            scan_result = session.query(ScanResult).filter(
                                ScanResult.id == scan_result_id
                            ).first()
                            if scan_result:
                                # Log4j (CVE-2021-44228) PoC 재현 성공 시 severity = Critical로 업데이트
                                if cve_id == "CVE-2021-44228":
                                    scan_result.severity = "Critical"
                                    
                                    # normalized_result의 findings도 업데이트
                                    if scan_result.normalized_result:
                                        normalized_result = scan_result.normalized_result
                                        if isinstance(normalized_result, dict):
                                            findings = normalized_result.get("findings", [])
                                            for finding in findings:
                                                if isinstance(finding, dict):
                                                    # CVE-2021-44228 관련 finding의 severity를 Critical로 업데이트
                                                    finding_cves = finding.get("cve_list", [])
                                                    if cve_id in finding_cves or finding.get("type", "").lower() in ["log4j", "log4shell", "cve-2021-44228"]:
                                                        finding["severity"] = "Critical"
                                            normalized_result["findings"] = findings
                                            scan_result.normalized_result = normalized_result
                                    
                                    session.commit()
                                    logger.info(f"✓ {cve_id} PoC 재현 성공: scan_result.severity를 Critical로 업데이트 완료")
                    except Exception as e:
                        logger.error(f"✗ PoC 재현 성공 후 severity 업데이트 실패: {str(e)}")
                        session.rollback()

                # 5. 신뢰도 점수 계산 및 저장
                reliability_score = None
                logger.info(f"Calculating reliability score for reproduction_id: {reproduction_id}, poc_metadata_id: {poc_metadata_id}")
                
                # poc_metadata_id가 없어도 source, cve_id, poc_type이 있으면 계산 가능
                if poc_metadata_id or (cve_id and source):
                    try:
                        from src.verification.reliability import ReliabilityScorer
                        
                        # PoC 메타데이터 준비
                        poc_metadata_dict = {}
                        if poc_metadata_id:
                            from src.database.repository import POCMetadataRepository
                            poc_metadata_repo = POCMetadataRepository(session)
                            poc_metadata = poc_metadata_repo.get_by_id(poc_metadata_id)
                            
                            if poc_metadata:
                                poc_metadata_dict = poc_metadata.to_dict() if hasattr(poc_metadata, 'to_dict') else {
                                    "source": poc_metadata.source if hasattr(poc_metadata, 'source') else source,
                                    "cve_id": poc_metadata.cve_id if hasattr(poc_metadata, 'cve_id') else cve_id,
                                    "poc_type": poc_metadata.poc_type if hasattr(poc_metadata, 'poc_type') else poc_type
                                }
                            else:
                                logger.warning(f"PoC metadata not found: {poc_metadata_id}, using provided values")
                                poc_metadata_dict = {
                                    "source": source,
                                    "cve_id": cve_id,
                                    "poc_type": poc_type
                                }
                        else:
                            # poc_metadata_id가 없으면 제공된 값 사용
                            poc_metadata_dict = {
                                "source": source,
                                "cve_id": cve_id,
                                "poc_type": poc_type
                            }
                        
                        scorer = ReliabilityScorer()
                        reliability_score = scorer.calculate_reliability_score(
                            poc_metadata=poc_metadata_dict,
                            reproduction_result=reproduction_result,
                            evidence_paths=evidence_paths
                        )
                        
                        # 신뢰도 점수 업데이트
                        saved_reproduction.reliability_score = reliability_score
                        session.commit()
                        # 세션 새로고침하여 변경사항 반영
                        session.refresh(saved_reproduction)
                        logger.info(f"Reliability score calculated and saved: {reliability_score}/100 (reproduction_id: {reproduction_id})")
                    except Exception as e:
                        logger.error(f"Failed to calculate reliability score: {str(e)}")
                        import traceback
                        logger.error(traceback.format_exc())
                else:
                    logger.warning(f"Cannot calculate reliability score: poc_metadata_id={poc_metadata_id}, cve_id={cve_id}, source={source}")

                return {
                    "success": True,
                    "reproduction_id": reproduction_id,
                    "status": reproduction_result.get("status"),
                    "evidence_paths": evidence_paths,
                    "reliability_score": reliability_score,
                    "db_id": saved_reproduction.id
                }

        except Exception as e:
            logger.error(f"PoC reproduction pipeline failed: {str(e)}")
            
            # 실패한 경우에도 DB에 저장 (상태: failed)
            try:
                reproduction_id = f"poc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
                import uuid
                
                # PoC 메타데이터 저장 시도
                poc_metadata_id = None
                if cve_id:
                    poc_metadata_id = self._save_poc_metadata(
                        cve_id=cve_id,
                        poc_type=poc_type,
                        source=source,
                        poc_script=poc_script
                    )
                
                # 실패한 재현 결과도 DB에 저장
                db = get_db()
                with db.get_session() as session:
                    repo = POCReproductionRepository(session)
                    
                    # 에러 메시지를 evidence_location에 저장 (임시)
                    error_msg = str(e)[:500]  # 최대 500자
                    reproduction_data = {
                        "reproduction_id": reproduction_id,
                        "poc_id": poc_metadata_id,
                        "scan_result_id": scan_result_id,
                        "target_host": target_host or "",
                        "reproduction_timestamp": datetime.now(),
                        "status": "failed",
                        "evidence_location": f"ERROR: {error_msg}",  # 에러 메시지 저장
                        "syscall_log_path": "",
                        "network_capture_path": "",
                        "filesystem_diff_path": "",
                        "screenshots_path": []
                    }
                    
                    saved_reproduction = repo.save(reproduction_data)
                    logger.info(f"Failed PoC reproduction saved to DB: {reproduction_id}")
            except Exception as save_error:
                logger.error(f"Failed to save failed PoC reproduction: {str(save_error)}")
            
            return {
                "success": False,
                "error": str(e),
                "reproduction_id": reproduction_id if 'reproduction_id' in locals() else None
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

