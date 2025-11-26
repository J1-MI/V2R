#!/usr/bin/env python3
"""
확장된 스모크 테스트 스크립트
새로 구현된 모듈들을 포함한 전체 기능 검증
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
            logger.error(f"[FAIL] {name} - {str(e)}")

    def print_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("EXTENDED SMOKE TEST RESULTS")
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
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 60)
        
        if self.failed_tests == 0:
            print("\n[SUCCESS] All smoke tests passed!")
            return True
        else:
            print(f"\n[WARNING] {self.failed_tests} test(s) failed")
            return False


def test_poc_modules():
    """PoC 모듈 import 테스트"""
    try:
        from src.poc import IsolationEnvironment, POCReproducer, EvidenceCollector
        return True
    except Exception as e:
        logger.error(f"PoC modules test failed: {e}")
        return False


def test_verification_modules():
    """검증 모듈 import 테스트"""
    try:
        from src.verification import ReliabilityScorer
        scorer = ReliabilityScorer()
        assert scorer is not None
        return True
    except Exception as e:
        logger.error(f"Verification modules test failed: {e}")
        return False


def test_llm_modules():
    """LLM 모듈 import 테스트"""
    try:
        from src.llm import LLMReportGenerator
        # API 키 없어도 인스턴스 생성은 가능해야 함
        generator = LLMReportGenerator()
        assert generator is not None
        return True
    except Exception as e:
        logger.error(f"LLM modules test failed: {e}")
        return False


def test_report_modules():
    """리포트 모듈 import 테스트"""
    try:
        from src.report import ReportGenerator, PRTemplateGenerator
        report_gen = ReportGenerator()
        pr_gen = PRTemplateGenerator()
        assert report_gen is not None
        assert pr_gen is not None
        return True
    except Exception as e:
        logger.error(f"Report modules test failed: {e}")
        return False


def test_dashboard_modules():
    """대시보드 모듈 import 테스트"""
    try:
        # streamlit은 import 시 대화형 모드로 들어갈 수 있으므로 주의
        import sys
        sys.argv = ['test']  # streamlit이 실행 모드로 인식하지 않도록
        
        # 모듈 파일 존재 확인
        dashboard_file = project_root / "src" / "dashboard" / "app.py"
        if dashboard_file.exists():
            return True
        return False
    except Exception as e:
        logger.error(f"Dashboard modules test failed: {e}")
        return False


def test_poc_pipeline():
    """PoC 파이프라인 모듈 테스트"""
    try:
        from src.pipeline.poc_pipeline import POCPipeline
        pipeline = POCPipeline()
        assert pipeline is not None
        return True
    except Exception as e:
        logger.error(f"PoC pipeline test failed: {e}")
        return False


def test_reliability_scoring():
    """신뢰도 점수화 로직 테스트"""
    try:
        from src.verification import ReliabilityScorer
        
        scorer = ReliabilityScorer()
        
        # 더미 데이터로 점수 계산 테스트
        poc_metadata = {"source": "test", "cve_id": "CVE-TEST", "poc_type": "test"}
        reproduction_result = {"status": "success", "execution_result": {"success": True}}
        evidence_paths = {}
        
        score = scorer.calculate_reliability_score(
            poc_metadata, reproduction_result, evidence_paths
        )
        
        assert 0 <= score <= 100, f"Score should be between 0-100, got {score}"
        return True
    except Exception as e:
        logger.error(f"Reliability scoring test failed: {e}")
        return False


def test_new_file_structure():
    """새로 추가된 파일 구조 테스트"""
    try:
        required_files = [
            "src/poc/__init__.py",
            "src/poc/isolation.py",
            "src/poc/reproduction.py",
            "src/poc/evidence.py",
            "src/verification/__init__.py",
            "src/verification/reliability.py",
            "src/llm/__init__.py",
            "src/llm/report_generator.py",
            "src/report/__init__.py",
            "src/report/generator.py",
            "src/report/pr_template.py",
            "src/dashboard/__init__.py",
            "src/dashboard/app.py",
            "src/pipeline/poc_pipeline.py",
        ]
        
        for file_path in required_files:
            full_path = project_root / file_path
            if not full_path.exists():
                logger.error(f"Required file not found: {file_path}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"New file structure test failed: {e}")
        return False


def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("V2R Project Extended Smoke Tests")
    print("=" * 60)
    print()
    
    test_runner = SmokeTest()
    
    # 기존 테스트
    from scripts.test.smoke_test import (
        test_imports, test_config, test_scanner_classes,
        test_normalizer, test_database_connection_class,
        test_database_models, test_database_repository,
        test_scanner_pipeline, test_file_structure
    )
    
    print("Running extended smoke tests...\n")
    
    # 기존 테스트
    test_runner.test("Module Imports", test_imports)
    test_runner.test("Config Module", test_config)
    test_runner.test("Scanner Classes", test_scanner_classes)
    test_runner.test("Normalizer Module", test_normalizer)
    test_runner.test("Database Connection Class", test_database_connection_class)
    test_runner.test("Database Models", test_database_models)
    test_runner.test("Database Repository", test_database_repository)
    test_runner.test("Scanner Pipeline", test_scanner_pipeline)
    test_runner.test("File Structure", test_file_structure)
    
    # 새로운 모듈 테스트
    test_runner.test("PoC Modules", test_poc_modules)
    test_runner.test("Verification Modules", test_verification_modules)
    test_runner.test("LLM Modules", test_llm_modules)
    test_runner.test("Report Modules", test_report_modules)
    test_runner.test("Dashboard Modules", test_dashboard_modules)
    test_runner.test("PoC Pipeline", test_poc_pipeline)
    test_runner.test("Reliability Scoring", test_reliability_scoring)
    test_runner.test("New File Structure", test_new_file_structure)
    
    # 결과 출력
    success = test_runner.print_summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

