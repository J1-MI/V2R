"""
우선순위 계산 파이프라인
ML 모델을 사용하여 취약점의 우선순위를 계산하고 DB에 저장합니다.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.ml import PriorityModel
from src.database import get_db
from src.database.repository import ScanResultRepository, POCReproductionRepository, POCMetadataRepository
from src.database.models import ScanResult

logger = logging.getLogger(__name__)


class PriorityPipeline:
    """우선순위 계산 파이프라인 클래스"""

    def __init__(self):
        self.priority_model = PriorityModel()

    def calculate_priorities_for_scans(self, scan_result_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        스캔 결과에 대한 우선순위 계산

        Args:
            scan_result_ids: 스캔 결과 ID 리스트 (None이면 최근 스캔 결과)

        Returns:
            우선순위 계산 결과
        """
        logger.info("우선순위 계산 파이프라인 시작")

        db = get_db()
        with db.get_session() as session:
            scan_repo = ScanResultRepository(session)
            poc_repo = POCReproductionRepository(session)
            poc_meta_repo = POCMetadataRepository(session)

            # 스캔 결과 조회
            if scan_result_ids:
                from src.database.models import ScanResult
                scans = session.query(ScanResult).filter(ScanResult.id.in_(scan_result_ids)).all()
            else:
                scans = scan_repo.get_recent(days=30, limit=100)

            if not scans:
                logger.warning("우선순위를 계산할 스캔 결과가 없습니다")
                return {"success": False, "error": "No scan results found"}

            # 각 스캔 결과에 대해 우선순위 계산
            results = []
            for scan in scans:
                try:
                    # PoC 정보 조회
                    poc_reproductions = poc_repo.get_by_scan_result_id(scan.id)
                    poc_metadata = None
                    if poc_reproductions:
                        poc_id = poc_reproductions[0].poc_id
                        if poc_id:
                            poc_metadata = poc_meta_repo.get_by_id(poc_id)

                    # 취약점 정보 구성
                    vulnerability_data = {
                        "severity": scan.severity or "Info",
                        "cve_list": scan.cve_list or [],
                        "reliability_score": poc_metadata.reliability_score if poc_metadata else 0,
                        "poc_id": poc_reproductions[0].poc_id if poc_reproductions else None,
                        "has_poc": len(poc_reproductions) > 0,
                        "poc_status": poc_reproductions[0].status if poc_reproductions else None,
                        "days_since_discovery": (datetime.now() - scan.scan_timestamp).days if scan.scan_timestamp else 0
                    }

                    # 우선순위 예측
                    priority_result = self.priority_model.predict_priority(vulnerability_data)

                    # normalized_result에 우선순위 정보 추가
                    normalized = scan.normalized_result or {}
                    if "metadata" not in normalized:
                        normalized["metadata"] = {}
                    normalized["metadata"]["priority"] = priority_result["priority"]
                    normalized["metadata"]["priority_score"] = priority_result["priority_score"]
                    normalized["metadata"]["priority_confidence"] = priority_result.get("confidence", 0)

                    # DB 업데이트
                    scan.normalized_result = normalized
                    session.commit()

                    results.append({
                        "scan_id": scan.scan_id,
                        "priority": priority_result["priority"],
                        "priority_score": priority_result["priority_score"],
                        "confidence": priority_result.get("confidence", 0)
                    })

                    logger.info(f"우선순위 계산 완료: {scan.scan_id} (우선순위: {priority_result['priority']}, 점수: {priority_result['priority_score']})")

                except Exception as e:
                    logger.error(f"우선순위 계산 실패 (scan_id: {scan.scan_id}): {str(e)}")
                    continue

            return {
                "success": True,
                "processed": len(results),
                "results": results
            }

    def calculate_priority_for_vulnerability(
        self,
        scan_result_id: int,
        poc_reproduction_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        단일 취약점에 대한 우선순위 계산

        Args:
            scan_result_id: 스캔 결과 ID
            poc_reproduction_id: PoC 재현 결과 ID (선택)

        Returns:
            우선순위 예측 결과
        """
        db = get_db()
        with db.get_session() as session:
            scan_repo = ScanResultRepository(session)
            poc_repo = POCReproductionRepository(session)
            poc_meta_repo = POCMetadataRepository(session)

            # 스캔 결과 조회
            from src.database.models import ScanResult
            scan = session.query(ScanResult).filter(ScanResult.id == scan_result_id).first()

            if not scan:
                return {"success": False, "error": "Scan result not found"}

            # PoC 정보 조회
            poc_reproductions = poc_repo.get_by_scan_result_id(scan_result_id)
            poc_metadata = None
            if poc_reproductions:
                poc_id = poc_reproductions[0].poc_id
                if poc_id:
                    poc_metadata = poc_meta_repo.get_by_id(poc_id)

            # 취약점 정보 구성
            vulnerability_data = {
                "severity": scan.severity or "Info",
                "cve_list": scan.cve_list or [],
                "reliability_score": poc_metadata.reliability_score if poc_metadata else 0,
                "poc_id": poc_reproductions[0].poc_id if poc_reproductions else None,
                "has_poc": len(poc_reproductions) > 0,
                "poc_status": poc_reproductions[0].status if poc_reproductions else None,
                "days_since_discovery": (datetime.now() - scan.scan_timestamp).days if scan.scan_timestamp else 0
            }

            # 우선순위 예측
            priority_result = self.priority_model.predict_priority(vulnerability_data)

            return {
                "success": True,
                "scan_result_id": scan_result_id,
                **priority_result
            }

