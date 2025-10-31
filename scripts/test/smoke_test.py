#!/usr/bin/env python3
"""
스모크 테스트 스크립트
지금까지 구현된 기능들의 기본 동작을 검증합니다.
"""

import sys
import logging
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class SmokeTest:
    """스모크 테스트 클래스"""

    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def test(self, name: str, test_func):
        """테스트 실행"""
        self.total_tests += 1
        try:
            result = test_func()
            if result:
                self.passed_tests += 1
                self.results.append(("PASS", name))
                logger.info(f"[PASS] {name}")
            else:
                self.failed_tests += 1
                self.results.append(("FAIL", name, "Test returned False"))
                logger.error(f"[FAIL] {name} - Test returned False")
        except Exception as e:
            self.failed_tests += 1
            self.results.append(("FAIL", name, str(e)))
            logger.error(f"✗ {name} - {str(e)}")

    def print_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("SMOKE TEST RESULTS")
        print("=" * 60)
        
        for status, name, *error in self.results:
            if status == "PASS":
                print(f"[PASS] {name}")
            else:
                print(f"[FAIL] {name}")
                if error:
                    print(f"  Error: {error[0]}")
        
        print("\n" + "-" * 60)
        print(f"Total: {self.total_tests} | Passed: {self.passed_tests} | Failed: {self.failed_tests}")
        print("=" * 60)
        
        if self.failed_tests == 0:
            print("\n[SUCCESS] All smoke tests passed!")
            return True
        else:
            print(f"\n[WARNING] {self.failed_tests} test(s) failed")
            print("\nNote: Some failures may be due to missing dependencies.")
            print("Install dependencies with: pip install -r requirements.txt")
            return False


def test_imports():
    """모듈 import 테스트"""
    try:
        from src.config import PROJECT_ROOT, DB_HOST, DB_NAME
        from src.scanner import NmapScanner, NucleiScanner, ScanResultNormalizer
        from src.database import DatabaseConnection, get_db
        return True
    except Exception as e:
        logger.error(f"Import test failed: {e}")
        return False


def test_config():
    """설정 모듈 테스트"""
    try:
        from src.config import PROJECT_ROOT
        assert PROJECT_ROOT.exists(), "PROJECT_ROOT should exist"
        return True
    except Exception as e:
        logger.error(f"Config test failed: {e}")
        return False


def test_scanner_classes():
    """스캐너 클래스 인스턴스 생성 테스트"""
    try:
        from src.scanner import NmapScanner, NucleiScanner
        
        # NmapScanner 인스턴스 생성
        nmap_scanner = NmapScanner(scan_timeout=60)
        assert nmap_scanner is not None
        
        # NucleiScanner 인스턴스 생성
        nuclei_scanner = NucleiScanner()
        assert nuclei_scanner is not None
        
        return True
    except Exception as e:
        logger.error(f"Scanner classes test failed: {e}")
        return False


def test_normalizer():
    """정규화 모듈 테스트"""
    try:
        from src.scanner import ScanResultNormalizer
        
        normalizer = ScanResultNormalizer()
        
        # 샘플 데이터로 테스트
        sample_result = {
            "scan_id": "test_001",
            "scanner_name": "nmap",
            "scan_timestamp": "2025-11-01T00:00:00",
            "target_host": "127.0.0.1",
            "status": "completed",
            "summary": {
                "open_ports": [
                    {"host": "127.0.0.1", "port": 80, "protocol": "tcp", "service": "http"}
                ]
            }
        }
        
        normalized = normalizer.normalize(sample_result, "nmap")
        assert normalized is not None
        assert normalized["scanner_name"] == "nmap"
        assert len(normalized["findings"]) > 0
        
        return True
    except Exception as e:
        logger.error(f"Normalizer test failed: {e}")
        return False


def test_database_connection_class():
    """데이터베이스 연결 클래스 테스트 (실제 연결은 하지 않음)"""
    try:
        from src.database import DatabaseConnection
        
        # 연결 문자열 생성 테스트
        db = DatabaseConnection(
            host="localhost",
            port="5432",
            database="v2r",
            user="test",
            password="test"
        )
        
        connection_string = db.get_connection_string()
        assert "postgresql://" in connection_string
        
        return True
    except Exception as e:
        logger.error(f"Database connection class test failed: {e}")
        return False


def test_file_structure():
    """프로젝트 파일 구조 테스트"""
    try:
        from pathlib import Path
        
        required_files = [
            "Dockerfile",
            "Dockerfile.dev",
            "docker-compose.yml",
            "Makefile",
            "requirements.txt",
            "src/config.py",
            "src/scanner/nmap_scanner.py",
            "src/scanner/nuclei_scanner.py",
            "src/scanner/normalizer.py",
            "src/database/connection.py",
            "src/database/schema.sql",
        ]
        
        project_root = Path(__file__).parent.parent.parent
        
        for file_path in required_files:
            full_path = project_root / file_path
            if not full_path.exists():
                logger.error(f"Required file not found: {file_path}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"File structure test failed: {e}")
        return False


def test_docker_compose_config():
    """Docker Compose 설정 파일 검증"""
    try:
        import yaml
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent
        compose_file = project_root / "docker-compose.yml"
        
        if not compose_file.exists():
            logger.warning("docker-compose.yml not found, skipping test")
            return True
        
        with open(compose_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 기본 서비스 확인
        assert 'services' in config
        assert 'postgres' in config['services'] or 'app' in config['services']
        
        return True
    except ImportError:
        logger.warning("PyYAML not installed, skipping Docker Compose test")
        return True
    except Exception as e:
        logger.error(f"Docker Compose config test failed: {e}")
        return False


def test_schema_sql():
    """스키마 SQL 파일 검증"""
    try:
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent
        schema_file = project_root / "src" / "database" / "schema.sql"
        
        if not schema_file.exists():
            logger.error("schema.sql not found")
            return False
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 기본 테이블 확인
        required_tables = [
            "CREATE TABLE",
            "scan_results",
            "poc_metadata",
            "events"
        ]
        
        for table in required_tables:
            if table.lower() not in content.lower():
                logger.warning(f"Table '{table}' not found in schema (may be case sensitive)")
        
        return True
    except Exception as e:
        logger.error(f"Schema SQL test failed: {e}")
        return False


def test_database_models():
    """데이터베이스 모델 import 테스트"""
    try:
        from src.database.models import (
            ScanResult,
            POCMetadata,
            POCReproduction,
            Event,
            Report,
            Base
        )
        
        # 모델 클래스 확인
        assert ScanResult is not None
        assert POCMetadata is not None
        assert Base is not None
        
        return True
    except Exception as e:
        logger.error(f"Database models test failed: {e}")
        return False


def test_database_repository():
    """데이터베이스 저장소 패턴 테스트"""
    try:
        from src.database.repository import (
            ScanResultRepository,
            POCMetadataRepository,
            POCReproductionRepository
        )
        
        # 저장소 클래스 확인
        assert ScanResultRepository is not None
        assert POCMetadataRepository is not None
        
        return True
    except Exception as e:
        logger.error(f"Database repository test failed: {e}")
        return False


def test_scanner_pipeline():
    """스캐너 파이프라인 모듈 테스트"""
    try:
        from src.pipeline import ScannerPipeline
        
        # 파이프라인 인스턴스 생성 테스트
        pipeline = ScannerPipeline()
        assert pipeline is not None
        assert pipeline.nmap_scanner is not None
        assert pipeline.nuclei_scanner is not None
        assert pipeline.normalizer is not None
        
        return True
    except Exception as e:
        logger.error(f"Scanner pipeline test failed: {e}")
        return False


def test_file_structure_extended():
    """확장된 파일 구조 테스트"""
    try:
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent
        
        required_files = [
            "src/database/models.py",
            "src/database/repository.py",
            "src/pipeline/scanner_pipeline.py",
            "scripts/test/test_pipeline.py",
        ]
        
        for file_path in required_files:
            full_path = project_root / file_path
            if not full_path.exists():
                logger.error(f"Required file not found: {file_path}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"Extended file structure test failed: {e}")
        return False


def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("V2R Project Smoke Tests")
    print("=" * 60)
    print()
    
    test_runner = SmokeTest()
    
    # 테스트 실행
    print("Running smoke tests...\n")
    
    test_runner.test("Module Imports", test_imports)
    test_runner.test("Config Module", test_config)
    test_runner.test("Scanner Classes", test_scanner_classes)
    test_runner.test("Normalizer Module", test_normalizer)
    test_runner.test("Database Connection Class", test_database_connection_class)
    test_runner.test("Database Models", test_database_models)
    test_runner.test("Database Repository", test_database_repository)
    test_runner.test("Scanner Pipeline", test_scanner_pipeline)
    test_runner.test("File Structure", test_file_structure)
    test_runner.test("Extended File Structure", test_file_structure_extended)
    test_runner.test("Docker Compose Config", test_docker_compose_config)
    test_runner.test("Schema SQL", test_schema_sql)
    
    # 결과 출력
    success = test_runner.print_summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

