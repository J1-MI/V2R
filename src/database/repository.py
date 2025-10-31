"""
데이터베이스 저장소 패턴 구현
스캔 결과 저장, 조회, 필터링 기능 제공
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from src.database.models import (
    ScanResult,
    POCMetadata,
    POCReproduction,
    Event,
    Report
)

logger = logging.getLogger(__name__)


class ScanResultRepository:
    """스캔 결과 저장소"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, scan_data: Dict[str, Any]) -> ScanResult:
        """
        스캔 결과 저장

        Args:
            scan_data: 스캔 결과 데이터
                - scan_id: 필수
                - target_host: 필수
                - scanner_name: 필수
                - scan_type: 필수
                - raw_result: 원본 결과
                - normalized_result: 정규화된 결과
                - cve_list: CVE ID 리스트
                - severity: 최고 심각도
                - status: 상태

        Returns:
            저장된 ScanResult 객체
        """
        try:
            # 기존 스캔 결과 확인
            existing = self.session.query(ScanResult).filter(
                ScanResult.scan_id == scan_data["scan_id"]
            ).first()

            if existing:
                # 업데이트
                for key, value in scan_data.items():
                    if hasattr(existing, key) and key not in ["id", "scan_id", "created_at"]:
                        setattr(existing, key, value)
                existing.updated_at = datetime.now()
                result = existing
                logger.info(f"Updated scan result: {scan_data['scan_id']}")
            else:
                # 새로 생성
                result = ScanResult(**scan_data)
                self.session.add(result)
                logger.info(f"Created new scan result: {scan_data['scan_id']}")

            self.session.commit()
            return result

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to save scan result: {str(e)}")
            raise

    def get_by_id(self, scan_id: str) -> Optional[ScanResult]:
        """스캔 ID로 조회"""
        return self.session.query(ScanResult).filter(
            ScanResult.scan_id == scan_id
        ).first()

    def get_by_target(self, target_host: str, limit: int = 100) -> List[ScanResult]:
        """대상 호스트로 조회 (최신순)"""
        return self.session.query(ScanResult).filter(
            ScanResult.target_host == target_host
        ).order_by(desc(ScanResult.scan_timestamp)).limit(limit).all()

    def get_by_scanner(self, scanner_name: str, limit: int = 100) -> List[ScanResult]:
        """스캐너 이름으로 조회"""
        return self.session.query(ScanResult).filter(
            ScanResult.scanner_name == scanner_name
        ).order_by(desc(ScanResult.scan_timestamp)).limit(limit).all()

    def get_by_severity(self, severity: str, limit: int = 100) -> List[ScanResult]:
        """심각도로 필터링"""
        return self.session.query(ScanResult).filter(
            ScanResult.severity == severity
        ).order_by(desc(ScanResult.scan_timestamp)).limit(limit).all()

    def get_recent(self, days: int = 7, limit: int = 100) -> List[ScanResult]:
        """최근 N일간의 스캔 결과"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return self.session.query(ScanResult).filter(
            ScanResult.scan_timestamp >= cutoff_date
        ).order_by(desc(ScanResult.scan_timestamp)).limit(limit).all()

    def search_by_cve(self, cve_id: str) -> List[ScanResult]:
        """특정 CVE ID가 포함된 스캔 결과 조회"""
        return self.session.query(ScanResult).filter(
            ScanResult.cve_list.contains([cve_id])
        ).order_by(desc(ScanResult.scan_timestamp)).all()

    def get_statistics(self, target_host: Optional[str] = None) -> Dict[str, Any]:
        """스캔 결과 통계"""
        query = self.session.query(ScanResult)

        if target_host:
            query = query.filter(ScanResult.target_host == target_host)

        total = query.count()
        by_status = {}
        by_severity = {}
        by_scanner = {}

        # 상태별 통계
        for status in ["pending", "processing", "completed", "failed"]:
            count = query.filter(ScanResult.status == status).count()
            if count > 0:
                by_status[status] = count

        # 심각도별 통계
        for severity in ["Critical", "High", "Medium", "Low", "Info"]:
            count = query.filter(ScanResult.severity == severity).count()
            if count > 0:
                by_severity[severity] = count

        # 스캐너별 통계
        scanner_stats = query.with_entities(
            ScanResult.scanner_name,
            func.count(ScanResult.id)
        ).group_by(ScanResult.scanner_name).all()

        by_scanner = {name: count for name, count in scanner_stats}

        return {
            "total": total,
            "by_status": by_status,
            "by_severity": by_severity,
            "by_scanner": by_scanner
        }


class POCMetadataRepository:
    """PoC 메타데이터 저장소"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, poc_data: Dict[str, Any]) -> POCMetadata:
        """PoC 메타데이터 저장"""
        try:
            existing = self.session.query(POCMetadata).filter(
                POCMetadata.poc_id == poc_data["poc_id"]
            ).first()

            if existing:
                for key, value in poc_data.items():
                    if hasattr(existing, key) and key not in ["id", "poc_id", "created_at"]:
                        setattr(existing, key, value)
                existing.updated_at = datetime.now()
                result = existing
            else:
                result = POCMetadata(**poc_data)
                self.session.add(result)

            self.session.commit()
            return result

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to save POC metadata: {str(e)}")
            raise

    def get_by_cve(self, cve_id: str) -> List[POCMetadata]:
        """CVE ID로 PoC 조회"""
        return self.session.query(POCMetadata).filter(
            POCMetadata.cve_id == cve_id
        ).order_by(desc(POCMetadata.reliability_score)).all()

    def get_by_reliability(self, min_score: int = 70) -> List[POCMetadata]:
        """신뢰도 점수로 필터링"""
        return self.session.query(POCMetadata).filter(
            POCMetadata.reliability_score >= min_score
        ).order_by(desc(POCMetadata.reliability_score)).all()


class POCReproductionRepository:
    """PoC 재현 결과 저장소"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, reproduction_data: Dict[str, Any]) -> POCReproduction:
        """PoC 재현 결과 저장"""
        try:
            existing = self.session.query(POCReproduction).filter(
                POCReproduction.reproduction_id == reproduction_data["reproduction_id"]
            ).first()

            if existing:
                for key, value in reproduction_data.items():
                    if hasattr(existing, key) and key not in ["id", "reproduction_id", "created_at"]:
                        setattr(existing, key, value)
                existing.updated_at = datetime.now()
                result = existing
            else:
                result = POCReproduction(**reproduction_data)
                self.session.add(result)

            self.session.commit()
            return result

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to save POC reproduction: {str(e)}")
            raise

    def get_by_status(self, status: str) -> List[POCReproduction]:
        """상태로 필터링"""
        return self.session.query(POCReproduction).filter(
            POCReproduction.status == status
        ).order_by(desc(POCReproduction.reproduction_timestamp)).all()

    def get_successful_reproductions(self) -> List[POCReproduction]:
        """성공한 재현만 조회"""
        return self.get_by_status("success")

