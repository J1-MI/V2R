"""
데이터베이스 저장소 패턴 구현
스캔 결과 저장, 조회, 필터링 기능 제공
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, case

from src.database.models import (
    ScanResult,
    POCMetadata,
    POCReproduction,
    Event,
    Report,
    CCECheckResult,
    Agent,
    AgentTask
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
                # 기존 레코드가 있으면 업데이트하지 않고 새 레코드 생성
                # (같은 scan_id로 여러 스캔이 있을 수 있으므로)
                # 대신 scan_id에 타임스탬프를 추가하여 고유하게 만듦
                from src.utils.id_generator import generate_scan_id
                import time
                new_scan_id = f"{scan_data['scan_id']}_{int(time.time() * 1000)}"
                scan_data['scan_id'] = new_scan_id
                result = ScanResult(**scan_data)
                self.session.add(result)
                logger.info(f"Created new scan result (duplicate avoided): {new_scan_id}")
            else:
                # 새로 생성
                result = ScanResult(**scan_data)
                self.session.add(result)
                logger.info(f"Created new scan result: {scan_data['scan_id']}")

            self.session.commit()
            return result

        except Exception as e:
            self.session.rollback()
            # 중복 키 오류인 경우 업데이트 시도
            if "UniqueViolation" in str(e) or "duplicate key" in str(e).lower():
                logger.warning(f"Duplicate scan_id detected, attempting update: {scan_data.get('scan_id')}")
                try:
                    existing = self.session.query(ScanResult).filter(
                        ScanResult.scan_id == scan_data["scan_id"]
                    ).first()
                    if existing:
                        for key, value in scan_data.items():
                            if hasattr(existing, key) and key not in ["id", "scan_id", "created_at"]:
                                setattr(existing, key, value)
                        existing.updated_at = datetime.now()
                        self.session.commit()
                        logger.info(f"Updated existing scan result: {scan_data['scan_id']}")
                        return existing
                except Exception as update_error:
                    logger.error(f"Failed to update existing scan result: {str(update_error)}")
            
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
        # Windows 시스템 시간대 고려 (UTC로 변환)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        return self.session.query(ScanResult).filter(
            ScanResult.scan_timestamp >= cutoff_date
        ).order_by(desc(ScanResult.scan_timestamp)).limit(limit).all()
    
    def get_latest_scan_group(self) -> List[ScanResult]:
        """가장 최근 스캔 그룹 조회 (같은 실행 세션에서 생성된 스캔들)"""
        # 가장 최근 스캔의 타임스탬프를 기준으로 같은 분에 생성된 스캔들을 그룹화
        latest_scan = self.session.query(ScanResult).order_by(
            desc(ScanResult.scan_timestamp)
        ).first()
        
        if not latest_scan:
            return []
        
        # 같은 분에 생성된 스캔들을 모두 조회
        scan_time = latest_scan.scan_timestamp
        time_window_start = scan_time - timedelta(minutes=1)
        time_window_end = scan_time + timedelta(minutes=1)
        
        return self.session.query(ScanResult).filter(
            ScanResult.scan_timestamp >= time_window_start,
            ScanResult.scan_timestamp <= time_window_end
        ).order_by(
            # 심각도 순으로 정렬 (Critical > High > Medium > Low > Info)
            desc(
                case(
                    (ScanResult.severity == "Critical", 5),
                    (ScanResult.severity == "High", 4),
                    (ScanResult.severity == "Medium", 3),
                    (ScanResult.severity == "Low", 2),
                    (ScanResult.severity == "Info", 1),
                    else_=0
                )
            ),
            desc(ScanResult.scan_timestamp)
        ).all()

    def search_by_cve(self, cve_id: str) -> List[ScanResult]:
        """특정 CVE ID가 포함된 스캔 결과 조회"""
        return self.session.query(ScanResult).filter(
            ScanResult.cve_list.contains([cve_id])
        ).order_by(desc(ScanResult.scan_timestamp)).all()

    def get_statistics(self, target_host: Optional[str] = None) -> Dict[str, Any]:
        """
        스캔 결과 통계
        normalized_result.findings에서 severity를 추출하여 집계
        """
        query = self.session.query(ScanResult)

        if target_host:
            query = query.filter(ScanResult.target_host == target_host)

        total = query.count()
        by_status = {}
        by_severity = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0}
        by_scanner = {}

        # 상태별 통계
        for status in ["pending", "processing", "completed", "failed"]:
            count = query.filter(ScanResult.status == status).count()
            if count > 0:
                by_status[status] = count

        # 심각도별 통계: normalized_result.findings에서 추출
        all_scan_results = query.all()
        for scan_result in all_scan_results:
            # normalized_result에서 findings 추출
            normalized_result = scan_result.normalized_result
            if normalized_result and isinstance(normalized_result, dict):
                findings = normalized_result.get("findings", [])
                if findings:
                    # 각 finding의 severity 추출
                    for finding in findings:
                        if isinstance(finding, dict):
                            severity = finding.get("severity", "")
                            if severity in by_severity:
                                by_severity[severity] += 1
                            elif severity:
                                # 대소문자 구분 없이 매칭
                                severity_lower = severity.lower()
                                if severity_lower == "critical":
                                    by_severity["Critical"] += 1
                                elif severity_lower == "high":
                                    by_severity["High"] += 1
                                elif severity_lower == "medium":
                                    by_severity["Medium"] += 1
                                elif severity_lower == "low":
                                    by_severity["Low"] += 1
                                else:
                                    by_severity["Info"] += 1
            
            # scan_result.severity도 확인 (fallback)
            if scan_result.severity and scan_result.severity in by_severity:
                # 이미 findings에서 집계했으므로 중복 방지
                # 하지만 findings가 없는 경우를 대비하여 scan_result.severity도 사용
                if not (normalized_result and isinstance(normalized_result, dict) and normalized_result.get("findings")):
                    by_severity[scan_result.severity] += 1

        # 0인 항목 제거
        by_severity = {k: v for k, v in by_severity.items() if v > 0}

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

    def get_by_id(self, poc_id: str) -> Optional[POCMetadata]:
        """PoC ID로 메타데이터 조회"""
        return self.session.query(POCMetadata).filter(
            POCMetadata.poc_id == poc_id
        ).first()


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


class CCECheckResultRepository:
    """CCE 점검 결과 저장소"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, check_data: Dict[str, Any]) -> CCECheckResult:
        """CCE 점검 결과 저장"""
        try:
            result = CCECheckResult(**check_data)
            self.session.add(result)
            self.session.commit()
            logger.info(f"Saved CCE check result: {check_data.get('cce_id')}")
            return result
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to save CCE check result: {str(e)}")
            raise

    def save_batch(self, check_results: List[Dict[str, Any]]) -> List[CCECheckResult]:
        """CCE 점검 결과 일괄 저장"""
        try:
            results = []
            for check_data in check_results:
                result = CCECheckResult(**check_data)
                self.session.add(result)
                results.append(result)
            self.session.commit()
            logger.info(f"Saved {len(results)} CCE check results")
            return results
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to save CCE check results batch: {str(e)}")
            raise

    def get_by_session(self, session_id: str) -> List[CCECheckResult]:
        """점검 세션 ID로 조회"""
        return self.session.query(CCECheckResult).filter(
            CCECheckResult.check_session_id == session_id
        ).order_by(CCECheckResult.severity.desc(), CCECheckResult.cce_id).all()
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """점검 세션 정보 조회 (대상 이름, 점검 시간 등)"""
        first_result = self.session.query(CCECheckResult).filter(
            CCECheckResult.check_session_id == session_id
        ).first()
        
        if not first_result:
            return None
        
        # 세션의 모든 결과에서 target_name 확인
        target_name = first_result.target_name
        
        # target_name이 없으면 세션 ID에서 추출 시도
        if not target_name:
            # 세션 ID 형식: cce_{target}_{timestamp} 또는 cce_test_{timestamp}
            parts = session_id.split('_')
            if len(parts) >= 3 and parts[0] == 'cce':
                if parts[1] == 'test':
                    target_name = "테스트"
                else:
                    target_name = parts[1].capitalize()
            else:
                target_name = "알 수 없음"
        
        return {
            "session_id": session_id,
            "target_name": target_name,
            "check_timestamp": first_result.check_timestamp,
            "total_checks": self.session.query(CCECheckResult).filter(
                CCECheckResult.check_session_id == session_id
            ).count()
        }

    def get_recent_sessions(self, limit: int = 10) -> List[str]:
        """최근 점검 세션 ID 목록 조회"""
        # 서브쿼리를 사용하여 각 세션의 최신 타임스탬프를 구한 후 정렬
        from sqlalchemy import select
        subquery = self.session.query(
            CCECheckResult.check_session_id,
            func.max(CCECheckResult.check_timestamp).label('max_ts')
        ).group_by(
            CCECheckResult.check_session_id
        ).subquery()
        
        sessions = self.session.query(
            subquery.c.check_session_id
        ).order_by(
            subquery.c.max_ts.desc()
        ).limit(limit).all()
        return [s[0] for s in sessions]

    def get_latest_session(self) -> Optional[str]:
        """가장 최근 점검 세션 ID 조회"""
        # 서브쿼리를 사용하여 각 세션의 최신 타임스탬프를 구한 후 정렬
        from sqlalchemy import select
        subquery = self.session.query(
            CCECheckResult.check_session_id,
            func.max(CCECheckResult.check_timestamp).label('max_ts')
        ).group_by(
            CCECheckResult.check_session_id
        ).subquery()
        
        latest = self.session.query(
            subquery.c.check_session_id
        ).order_by(
            subquery.c.max_ts.desc()
        ).first()
        return latest[0] if latest else None

    def get_statistics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """CCE 점검 결과 통계"""
        query = self.session.query(CCECheckResult)
        
        if session_id:
            query = query.filter(CCECheckResult.check_session_id == session_id)
        
        total = query.count()
        by_result = {}
        by_severity = {}
        
        # 결과별 통계
        for result_type in ["양호", "취약", "NOT_APPLICABLE"]:
            count = query.filter(CCECheckResult.result == result_type).count()
            if count > 0:
                by_result[result_type] = count
        
        # 심각도별 통계
        for severity in range(1, 6):
            count = query.filter(CCECheckResult.severity == severity).count()
            if count > 0:
                by_severity[severity] = count
        
        return {
            "total": total,
            "by_result": by_result,
            "by_severity": by_severity
        }


class AgentRepository:
    """Agent 저장소"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, agent_data: Dict[str, Any]) -> Agent:
        """Agent 저장"""
        try:
            existing = self.session.query(Agent).filter(
                Agent.agent_id == agent_data["agent_id"]
            ).first()

            if existing:
                for key, value in agent_data.items():
                    if hasattr(existing, key) and key not in ["id", "agent_id", "created_at"]:
                        setattr(existing, key, value)
                existing.updated_at = datetime.now()
                result = existing
            else:
                result = Agent(**agent_data)
                self.session.add(result)

            self.session.commit()
            return result

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to save agent: {str(e)}")
            raise

    def get_by_id(self, agent_id: str) -> Optional[Agent]:
        """Agent ID로 조회"""
        return self.session.query(Agent).filter(
            Agent.agent_id == agent_id
        ).first()

    def get_by_token_hash(self, token_hash: str) -> Optional[Agent]:
        """토큰 해시로 조회"""
        return self.session.query(Agent).filter(
            Agent.agent_token_hash == token_hash
        ).first()

    def get_all(self, limit: int = 100) -> List[Agent]:
        """모든 Agent 조회"""
        return self.session.query(Agent).order_by(
            desc(Agent.created_at)
        ).limit(limit).all()

    def update_last_seen(self, agent_id: str) -> bool:
        """마지막 접속 시간 업데이트"""
        try:
            agent = self.get_by_id(agent_id)
            if agent:
                agent.last_seen = datetime.now()
                agent.status = "online"
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to update last_seen: {str(e)}")
            return False

    def update_status(self, agent_id: str, status: str) -> bool:
        """Agent 상태 업데이트"""
        try:
            agent = self.get_by_id(agent_id)
            if agent:
                agent.status = status
                if status == "online":
                    agent.last_seen = datetime.now()
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to update status: {str(e)}")
            return False


class AgentTaskRepository:
    """Agent 작업 저장소"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, task_data: Dict[str, Any]) -> AgentTask:
        """작업 저장"""
        try:
            existing = self.session.query(AgentTask).filter(
                AgentTask.task_id == task_data["task_id"]
            ).first()

            if existing:
                for key, value in task_data.items():
                    if hasattr(existing, key) and key not in ["id", "task_id", "created_at"]:
                        setattr(existing, key, value)
                existing.updated_at = datetime.now()
                result = existing
            else:
                result = AgentTask(**task_data)
                self.session.add(result)

            self.session.commit()
            return result

        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to save agent task: {str(e)}")
            raise

    def get_by_id(self, task_id: str) -> Optional[AgentTask]:
        """작업 ID로 조회"""
        return self.session.query(AgentTask).filter(
            AgentTask.task_id == task_id
        ).first()

    def get_by_agent_id(self, agent_id: str, status: Optional[str] = None, limit: int = 100) -> List[AgentTask]:
        """Agent ID로 작업 조회"""
        query = self.session.query(AgentTask).filter(
            AgentTask.agent_id == agent_id
        )

        if status:
            if status.lower() == "all":
                # 모든 상태 반환
                pass
            else:
                query = query.filter(AgentTask.status == status)

        return query.order_by(desc(AgentTask.created_at)).limit(limit).all()

    def get_pending_tasks(self, agent_id: str) -> List[AgentTask]:
        """대기 중인 작업 조회 (기본값)"""
        return self.get_by_agent_id(agent_id, status="pending")

    def update_status(self, task_id: str, status: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """작업 상태 업데이트"""
        try:
            task = self.get_by_id(task_id)
            if task:
                task.status = status
                if result is not None:
                    task.result = result
                task.updated_at = datetime.now()
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to update task status: {str(e)}")
            return False

    def get_statistics(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """작업 통계"""
        query = self.session.query(AgentTask)

        if agent_id:
            query = query.filter(AgentTask.agent_id == agent_id)

        total = query.count()
        by_status = {}
        by_type = {}

        # 상태별 통계
        for status in ["pending", "running", "completed", "failed"]:
            count = query.filter(AgentTask.status == status).count()
            if count > 0:
                by_status[status] = count

        # 타입별 통계
        type_stats = query.with_entities(
            AgentTask.task_type,
            func.count(AgentTask.id)
        ).group_by(AgentTask.task_type).all()

        by_type = {task_type: count for task_type, count in type_stats}

        return {
            "total": total,
            "by_status": by_status,
            "by_type": by_type
        }

