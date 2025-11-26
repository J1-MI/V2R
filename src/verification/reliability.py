"""
PoC 신뢰도 점수화 모듈
출처, 증거, 실행 결과를 기반으로 PoC의 신뢰도를 점수화합니다.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from src.config import PROJECT_ROOT

logger = logging.getLogger(__name__)


class ReliabilityScorer:
    """PoC 신뢰도 점수화 클래스"""

    # 출처별 가중치 (0-100)
    SOURCE_WEIGHTS = {
        "exploit-db": 80,
        "github": 70,
        "cve-details": 75,
        "security-advisory": 85,
        "manual": 50,
        "other": 50
    }

    # 증거 유형별 가중치 (0-30)
    EVIDENCE_WEIGHTS = {
        "syscalls": 30,  # 시스템콜 로그
        "network": 20,   # 네트워크 캡처
        "fs_diff": 20,   # 파일 시스템 변화
        "screenshot": 10  # 스크린샷
    }

    # 재현 상태별 가중치
    STATUS_WEIGHTS = {
        "success": 100,
        "partial": 60,
        "failed": 0
    }

    def __init__(self):
        """신뢰도 점수화 클래스 초기화"""
        pass

    def calculate_reliability_score(
        self,
        poc_metadata: Dict[str, Any],
        reproduction_result: Dict[str, Any],
        evidence_paths: Dict[str, str]
    ) -> int:
        """
        PoC 신뢰도 점수 계산 (0-100)

        Args:
            poc_metadata: PoC 메타데이터
                - source: 출처 (exploit-db, github, etc.)
                - cve_id: CVE ID
                - poc_type: PoC 유형
            reproduction_result: 재현 결과
                - status: 재현 상태 (success, partial, failed)
                - execution_result: 실행 결과
            evidence_paths: 증거 파일 경로
                - syscalls: 시스템콜 로그 경로
                - network: 네트워크 캡처 경로
                - fs_diff: 파일 시스템 diff 경로

        Returns:
            신뢰도 점수 (0-100)
        """
        try:
            # 1. 출처 기반 점수 (0-40점)
            source_score = self._calculate_source_score(poc_metadata.get("source", "other"))

            # 2. 재현 상태 기반 점수 (0-40점)
            status_score = self._calculate_status_score(reproduction_result.get("status", "failed"))

            # 3. 증거 기반 점수 (0-20점)
            evidence_score = self._calculate_evidence_score(evidence_paths)

            # 최종 점수 계산
            total_score = source_score + status_score + evidence_score

            # 점수 정규화 (0-100)
            final_score = min(100, max(0, total_score))

            logger.info(
                f"Reliability score calculated: {final_score} "
                f"(source: {source_score}, status: {status_score}, evidence: {evidence_score})"
            )

            return final_score

        except Exception as e:
            logger.error(f"Failed to calculate reliability score: {str(e)}")
            return 0

    def _calculate_source_score(self, source: str) -> int:
        """
        출처 기반 점수 계산 (0-40점)

        Args:
            source: 출처

        Returns:
            출처 점수
        """
        source_lower = source.lower()

        # 출처 가중치를 0-40 범위로 스케일링
        base_weight = self.SOURCE_WEIGHTS.get(source_lower, 50)
        source_score = int((base_weight / 100) * 40)

        return source_score

    def _calculate_status_score(self, status: str) -> int:
        """
        재현 상태 기반 점수 계산 (0-40점)

        Args:
            status: 재현 상태

        Returns:
            상태 점수
        """
        status_lower = status.lower()
        base_weight = self.STATUS_WEIGHTS.get(status_lower, 0)
        status_score = int((base_weight / 100) * 40)

        return status_score

    def _calculate_evidence_score(self, evidence_paths: Dict[str, str]) -> int:
        """
        증거 기반 점수 계산 (0-20점)

        Args:
            evidence_paths: 증거 파일 경로 딕셔너리

        Returns:
            증거 점수
        """
        evidence_score = 0

        # 각 증거 유형별 점수 계산
        for evidence_type, file_path in evidence_paths.items():
            if not file_path:
                continue

            # 파일 존재 여부 확인
            evidence_file = Path(file_path)
            if evidence_file.exists() and evidence_file.stat().st_size > 0:
                weight = self.EVIDENCE_WEIGHTS.get(evidence_type, 0)
                # 증거 가중치를 0-20 범위로 스케일링
                evidence_score += int((weight / 100) * 20)

        # 최대 20점으로 제한
        return min(20, evidence_score)

    def update_poc_reliability(
        self,
        poc_id: str,
        reliability_score: int
    ) -> bool:
        """
        PoC 메타데이터의 신뢰도 점수 업데이트

        Args:
            poc_id: PoC ID
            reliability_score: 신뢰도 점수

        Returns:
            업데이트 성공 여부
        """
        try:
            from src.database import get_db
            from src.database.repository import POCMetadataRepository
            from src.database.models import POCMetadata

            db = get_db()
            with db.get_session() as session:
                repo = POCMetadataRepository(session)

                # PoC 메타데이터 조회
                from sqlalchemy.orm import Session
                poc = session.query(POCMetadata).filter(POCMetadata.poc_id == poc_id).first()

                if not poc:
                    logger.warning(f"PoC not found: {poc_id}")
                    return False

                # 신뢰도 점수 업데이트
                poc_data = {
                    "poc_id": poc_id,
                    "reliability_score": reliability_score,
                    "verification_status": "verified" if reliability_score >= 70 else "unverified"
                }

                repo.save(poc_data)
                logger.info(f"PoC reliability updated: {poc_id} = {reliability_score}")

                return True

        except Exception as e:
            logger.error(f"Failed to update PoC reliability: {str(e)}")
            return False

    def get_reliability_level(self, score: int) -> str:
        """
        신뢰도 점수에 따른 레벨 반환

        Args:
            score: 신뢰도 점수

        Returns:
            레벨 (high, medium, low)
        """
        if score >= 80:
            return "high"
        elif score >= 60:
            return "medium"
        else:
            return "low"

