"""
SQLAlchemy ORM 모델 정의
데이터베이스 테이블과 Python 객체 간 매핑
"""

from sqlalchemy import Column, Integer, String, Float, Text, TIMESTAMP, ARRAY, JSON, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any, List

Base = declarative_base()


class ScanResult(Base):
    """스캔 결과 테이블 모델"""
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(255), unique=True, nullable=False, index=True)
    target_host = Column(String(255), nullable=False, index=True)
    scan_type = Column(String(100), nullable=False)  # nmap, nuclei, openvas, etc.
    scanner_name = Column(String(100), nullable=False)
    scan_timestamp = Column(TIMESTAMP, nullable=False, default=func.now(), index=True)
    raw_result = Column(JSONB)  # 원본 스캔 결과 (JSON)
    normalized_result = Column(JSONB)  # 정규화된 결과 (JSON)
    cve_list = Column(ARRAY(String))  # 발견된 CVE ID 리스트
    severity = Column(String(20))  # Critical, High, Medium, Low, Info
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<ScanResult(scan_id={self.scan_id}, target={self.target_host}, scanner={self.scanner_name})>"

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "scan_id": self.scan_id,
            "target_host": self.target_host,
            "scan_type": self.scan_type,
            "scanner_name": self.scanner_name,
            "scan_timestamp": self.scan_timestamp.isoformat() if self.scan_timestamp else None,
            "raw_result": self.raw_result,
            "normalized_result": self.normalized_result,
            "cve_list": self.cve_list,
            "severity": self.severity,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class POCMetadata(Base):
    """PoC 메타데이터 테이블 모델"""
    __tablename__ = "poc_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    poc_id = Column(String(255), unique=True, nullable=False, index=True)
    cve_id = Column(String(50), index=True)  # CVE-2021-44228 형식
    poc_type = Column(String(100))  # exploit, misconfiguration, etc.
    source = Column(String(255))  # Exploit-DB, GitHub, etc.
    source_url = Column(Text)
    file_hash_sha256 = Column(String(64))
    file_hash_md5 = Column(String(32))
    version = Column(String(50))
    reliability_score = Column(Integer, CheckConstraint('reliability_score >= 0 AND reliability_score <= 100'))
    verification_status = Column(String(50), default="unverified")  # verified, unverified, failed
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<POCMetadata(poc_id={self.poc_id}, cve_id={self.cve_id}, score={self.reliability_score})>"

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "poc_id": self.poc_id,
            "cve_id": self.cve_id,
            "poc_type": self.poc_type,
            "source": self.source,
            "source_url": self.source_url,
            "file_hash_sha256": self.file_hash_sha256,
            "file_hash_md5": self.file_hash_md5,
            "version": self.version,
            "reliability_score": self.reliability_score,
            "verification_status": self.verification_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class POCReproduction(Base):
    """PoC 재현 결과 테이블 모델"""
    __tablename__ = "poc_reproductions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reproduction_id = Column(String(255), unique=True, nullable=False, index=True)
    poc_id = Column(String(255), ForeignKey("poc_metadata.poc_id"), index=True)
    scan_result_id = Column(Integer, ForeignKey("scan_results.id"))
    target_host = Column(String(255), nullable=False)
    reproduction_timestamp = Column(TIMESTAMP, nullable=False, default=func.now())
    status = Column(String(50), nullable=False)  # success, failed, partial
    evidence_location = Column(Text)  # S3 경로 등
    syscall_log_path = Column(Text)
    network_capture_path = Column(Text)
    filesystem_diff_path = Column(Text)
    screenshots_path = Column(ARRAY(String))  # 스크린샷 경로 리스트
    reliability_score = Column(Integer, CheckConstraint('reliability_score >= 0 AND reliability_score <= 100'))
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<POCReproduction(reproduction_id={self.reproduction_id}, status={self.status})>"

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "reproduction_id": self.reproduction_id,
            "poc_id": self.poc_id,
            "scan_result_id": self.scan_result_id,
            "target_host": self.target_host,
            "reproduction_timestamp": self.reproduction_timestamp.isoformat() if self.reproduction_timestamp else None,
            "status": self.status,
            "evidence_location": self.evidence_location,
            "syscall_log_path": self.syscall_log_path,
            "network_capture_path": self.network_capture_path,
            "filesystem_diff_path": self.filesystem_diff_path,
            "screenshots_path": self.screenshots_path,
            "reliability_score": self.reliability_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Event(Base):
    """이벤트 테이블 모델 (탐지된 보안 이벤트)"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(255), unique=True, nullable=False, index=True)
    event_timestamp = Column(TIMESTAMP, nullable=False, index=True)
    event_category = Column(String(100))
    severity = Column(Integer, CheckConstraint('severity >= 0 AND severity <= 10'), index=True)
    summary = Column(Text)
    evidence_refs = Column(JSONB)  # 관련 증거 파일 참조
    rule_id = Column(String(255))
    ml_score = Column(Float)
    client_id = Column(String(255))
    host_name = Column(String(255))
    source_ip = Column(String(50))
    url_path = Column(Text)
    created_at = Column(TIMESTAMP, default=func.now())

    def __repr__(self):
        return f"<Event(event_id={self.event_id}, severity={self.severity})>"

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "event_id": self.event_id,
            "event_timestamp": self.event_timestamp.isoformat() if self.event_timestamp else None,
            "event_category": self.event_category,
            "severity": self.severity,
            "summary": self.summary,
            "evidence_refs": self.evidence_refs,
            "rule_id": self.rule_id,
            "ml_score": self.ml_score,
            "client_id": self.client_id,
            "host_name": self.host_name,
            "source_ip": self.source_ip,
            "url_path": self.url_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Report(Base):
    """리포트 테이블 모델"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(255), unique=True, nullable=False, index=True)
    report_type = Column(String(50))  # executive, technical, full
    scan_result_ids = Column(ARRAY(Integer))  # 관련 스캔 결과 ID 리스트
    poc_reproduction_ids = Column(ARRAY(Integer))  # 관련 PoC 재현 ID 리스트
    generated_at = Column(TIMESTAMP, nullable=False, default=func.now())
    file_path = Column(Text)  # 리포트 파일 경로
    file_hash_sha256 = Column(String(64))
    status = Column(String(50), default="draft")  # draft, final, published
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Report(report_id={self.report_id}, type={self.report_type}, status={self.status})>"

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "report_id": self.report_id,
            "report_type": self.report_type,
            "scan_result_ids": self.scan_result_ids,
            "poc_reproduction_ids": self.poc_reproduction_ids,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "file_path": self.file_path,
            "file_hash_sha256": self.file_hash_sha256,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

