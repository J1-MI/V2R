#!/usr/bin/env python3
"""
스캐너 파이프라인 통합 테스트
스캔 실행 → 정규화 → DB 저장 전체 플로우 테스트
"""

import sys
import logging
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline import ScannerPipeline
from src.database import get_db, initialize_database
from src.database.repository import ScanResultRepository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_pipeline_without_db():
    """DB 없이 파이프라인 테스트"""
    print("\n=== Pipeline Test (No DB) ===")
    
    pipeline = ScannerPipeline()
    
    # Nmap 스캔 테스트 (로컬호스트, 빠른 스캔)
    print("\n1. Nmap scan (localhost, quick scan)...")
    result = pipeline.run_nmap_scan("127.0.0.1", ports="22,80,443", save_to_db=False)
    
    print(f"   Scan ID: {result.get('scan_id', 'N/A')}")
    print(f"   Findings: {result.get('findings_count', 0)}")
    print(f"   Severity: {result.get('severity', 'N/A')}")
    print(f"   Success: {result.get('success', False)}")


def test_pipeline_with_db():
    """DB와 함께 파이프라인 테스트"""
    print("\n=== Pipeline Test (With DB) ===")
    
    try:
        # DB 초기화 확인
        db = get_db()
        if not db.test_connection():
            print("⚠️  Database connection failed. Skipping DB tests.")
            return False
        
        print("✓ Database connection successful")
        
        # 스키마 생성 (이미 있으면 무시됨)
        initialize_database()
        print("✓ Database schema ready")
        
        # 파이프라인 실행
        pipeline = ScannerPipeline()
        
        # Nmap 스캔 + DB 저장
        print("\n1. Nmap scan with DB save...")
        result = pipeline.run_nmap_scan(
            "127.0.0.1",
            ports="22,80,443",
            save_to_db=True
        )
        
        print(f"   Scan ID: {result.get('scan_id', 'N/A')}")
        print(f"   Saved to DB: {result.get('saved_to_db', False)}")
        
        # DB에서 조회
        if result.get("saved_to_db"):
            print("\n2. Querying from database...")
            with db.get_session() as session:
                repo = ScanResultRepository(session)
                saved = repo.get_by_id(result["scan_id"])
                
                if saved:
                    print(f"   ✓ Found in DB: {saved.scan_id}")
                    print(f"   Target: {saved.target_host}")
                    print(f"   Scanner: {saved.scanner_name}")
                    print(f"   Findings: {len(saved.normalized_result.get('findings', [])) if saved.normalized_result else 0}")
                    print(f"   CVEs: {len(saved.cve_list) if saved.cve_list else 0}")
                else:
                    print("   ✗ Not found in DB")
        
        # 통계 조회
        print("\n3. Statistics...")
        with db.get_session() as session:
            repo = ScanResultRepository(session)
            stats = repo.get_statistics()
            print(f"   Total scans: {stats['total']}")
            print(f"   By scanner: {stats['by_scanner']}")
            print(f"   By severity: {stats['by_severity']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {str(e)}")
        logger.exception(e)
        return False


def main():
    """메인 테스트 함수"""
    print("=" * 60)
    print("Scanner Pipeline Integration Test")
    print("=" * 60)
    
    # DB 없이 테스트
    test_pipeline_without_db()
    
    # DB와 함께 테스트
    success = test_pipeline_with_db()
    
    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] Pipeline test completed!")
    else:
        print("[WARNING] Some tests failed or DB unavailable")
    print("=" * 60)


if __name__ == "__main__":
    main()

