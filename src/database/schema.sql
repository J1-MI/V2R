-- V2R 프로젝트 데이터베이스 스키마
-- PostgreSQL 기반

-- 취약점 스캔 결과 테이블
CREATE TABLE IF NOT EXISTS scan_results (
    id BIGSERIAL PRIMARY KEY,
    scan_id VARCHAR(255) UNIQUE NOT NULL,
    target_host VARCHAR(255) NOT NULL,
    scan_type VARCHAR(100) NOT NULL,  -- nmap, nuclei, openvas, etc.
    scanner_name VARCHAR(100) NOT NULL,
    scan_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    raw_result JSONB,
    normalized_result JSONB,
    cve_list TEXT[],
    severity VARCHAR(20),  -- Critical, High, Medium, Low, Info
    status VARCHAR(50) DEFAULT 'pending',  -- pending, processing, completed, failed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- PoC 메타데이터 테이블
CREATE TABLE IF NOT EXISTS poc_metadata (
    id BIGSERIAL PRIMARY KEY,
    poc_id VARCHAR(255) UNIQUE NOT NULL,
    cve_id VARCHAR(50),
    poc_type VARCHAR(100),  -- exploit, misconfiguration, etc.
    source VARCHAR(255),  -- Exploit-DB, GitHub, etc.
    source_url TEXT,
    file_hash_sha256 VARCHAR(64),
    file_hash_md5 VARCHAR(32),
    version VARCHAR(50),
    reliability_score INTEGER CHECK (reliability_score >= 0 AND reliability_score <= 100),
    verification_status VARCHAR(50) DEFAULT 'unverified',  -- verified, unverified, failed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- PoC 재현 결과 테이블
CREATE TABLE IF NOT EXISTS poc_reproductions (
    id BIGSERIAL PRIMARY KEY,
    reproduction_id VARCHAR(255) UNIQUE NOT NULL,
    poc_id VARCHAR(255) REFERENCES poc_metadata(poc_id),
    scan_result_id BIGINT REFERENCES scan_results(id),
    target_host VARCHAR(255) NOT NULL,
    reproduction_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    status VARCHAR(50) NOT NULL,  -- success, failed, partial
    evidence_location TEXT,  -- S3 경로 등
    syscall_log_path TEXT,
    network_capture_path TEXT,
    filesystem_diff_path TEXT,
    screenshots_path TEXT[],
    reliability_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 이벤트 테이블 (탐지된 보안 이벤트)
CREATE TABLE IF NOT EXISTS events (
    id BIGSERIAL PRIMARY KEY,
    event_id VARCHAR(255) UNIQUE NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    event_category VARCHAR(100),
    severity INTEGER CHECK (severity >= 0 AND severity <= 10),
    summary TEXT,
    evidence_refs JSONB,  -- 관련 증거 파일 참조
    rule_id VARCHAR(255),
    ml_score FLOAT,
    client_id VARCHAR(255),
    host_name VARCHAR(255),
    source_ip VARCHAR(50),
    url_path TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 리포트 테이블
CREATE TABLE IF NOT EXISTS reports (
    id BIGSERIAL PRIMARY KEY,
    report_id VARCHAR(255) UNIQUE NOT NULL,
    report_type VARCHAR(50),  -- executive, technical, full
    scan_result_ids BIGINT[],
    poc_reproduction_ids BIGINT[],
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    file_path TEXT,  -- 리포트 파일 경로
    file_hash_sha256 VARCHAR(64),
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_scan_results_target ON scan_results(target_host);
CREATE INDEX IF NOT EXISTS idx_scan_results_timestamp ON scan_results(scan_timestamp);
CREATE INDEX IF NOT EXISTS idx_scan_results_cve ON scan_results USING GIN(cve_list);
CREATE INDEX IF NOT EXISTS idx_poc_metadata_cve ON poc_metadata(cve_id);
CREATE INDEX IF NOT EXISTS idx_poc_reproductions_poc ON poc_reproductions(poc_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity);

-- 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
CREATE TRIGGER update_scan_results_updated_at BEFORE UPDATE ON scan_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_poc_metadata_updated_at BEFORE UPDATE ON poc_metadata
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_poc_reproductions_updated_at BEFORE UPDATE ON poc_reproductions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

